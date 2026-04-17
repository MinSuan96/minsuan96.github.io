---
Title: sensor_log_rotation
author: Teh Min Suan
date: 21 August 2025
---

- [Overview](#overview)
  - [Core API (log\_rotate)](#core-api-log_rotate)
  - [How it’s used (log\_forward)](#how-its-used-log_forward)
  - [Configuration (agent\_config)](#configuration-agent_config)
  - [Windows Event Logs (Security/System/Application/ETW)](#windows-event-logs-securitysystemapplicationetw)
  - [Behavior summary](#behavior-summary)
  - [Testing with fill\_dummy\_data.py](#testing-with-fill_dummy_datapy)
    - [Prerequisites](#prerequisites)
    - [Test A — Archive + truncate (per-log)](#test-a--archive--truncate-per-log)
    - [Test B — Truncate-only (per-log)](#test-b--truncate-only-per-log)
    - [Test C — Windows Event Logs (truncate-only)](#test-c--windows-event-logs-truncate-only)
  - [Troubleshooting](#troubleshooting)
  - [Notes](#notes)

# Overview

This document explains the sensor's log rotation mechanism. The core logic is in `log_rotate.cpp`/`log_rotate.h` and is invoked by `log_forward.cpp`. Configuration is read by `config.cpp` from `agent_config`.

When a tracked log exceeds its configured size, the sensor will:

- Optionally copy the beginning portion of the file to an archive (append mode), then
- Remove that beginning portion from the original file by sliding remaining bytes forward and truncating.

This keeps the active tail of the log while preserving earlier bytes in an archive (when configured).

## Core API (log_rotate)

- Function: `int copytruncate(const char* file_path, const char* archive_path, int64_t last_pos);`
- Location: `log_rotate.h` / `log_rotate.cpp`
- Behavior:
  - Copies bytes `[0, last_pos)` from `file_path` to `archive_path` if provided, appending to the archive (no overwrite).
  - Slides remaining bytes `[last_pos .. end)` to the front of `file_path` and truncates.
  - Returns `0` on success, non-zero on error.
- Edge cases:
  - `last_pos <= 0`: no-op.
  - `last_pos >= file_size`: optionally copy entire file, then truncate to 0.
- Notes:
  - Archive is opened with `OPEN_ALWAYS` and writes seek to `FILE_END` (append).
  - `MIN_ROTATION_SIZE = 1024 * 1024` bytes is a guard constant.

## How it’s used (log_forward)

`log_forward.cpp` monitors configured files and triggers rotation once a file crosses its threshold. It passes the source path, the archive path (if any), and the byte offset to rotate (`last_pos`) into `copytruncate`.

## Configuration (agent_config)

Configuration is parsed by `config.cpp`. Use the same keys under each section.

- Define tracked logs in `[logs]`:
  - Example: `log.postgresql.db = C:\\Program Files\\PostgreSQL\\16\\data\\log\\postgresql.log`
- Configure per-log archive path in `[log_rotate_path]`:
  - Example: `log.postgresql.db = C:\\Program Files\\PostgreSQL\\16\\data\\log\\postgresql_backup.log`
  - If this value is empty or the key is missing, rotation is truncate-only (no copy).
- Set per-log thresholds in `[log_rotate_size]` (bytes):
  - Must be bigger than MIN_ROTATION_SIZE (1MB)
  - Example: `log.postgresql.db = 10485760`

## Windows Event Logs (Security/System/Application/ETW)

- Global key: `evtlog_rotate_size` (in the `[local agent]` block of `agent_config`).
  - Can be smaller than MIN_ROTATION_SIZE (1MB)
  - Example: `evtlog_rotate_size = 1000`
- Scope: applies only to all Windows Event Logs
- Behavior: truncate-only (no copy/archive for event logs).
  When the `evtlog_rotate_size` threshold is reached, the Windows event log buffer is truncated in place and nothing is copied. This logic is implemented in `winevent.cpp` (copytruncate is not used for event logs).
- Coexistence with file rotation settings, you can define both the global `evtlog_rotate_size` and per-file entries in `[log_rotate_size]` at the same time. They control different rotation and do not conflict.
- Additional key: `evtlog_sent_complete_timeout`.
  - Example: `evtlog_sent_complete_timeout = 10`
  - Purpose: If the data of the event log is not completely sent, specifies the amount of time to wait (in seconds) for the event log data to be sent before truncating.

## Behavior summary

- `[log_rotate_size]` controls when to rotate for each key in `[logs]`.
- `[log_rotate_path]` controls whether the rotated prefix is appended to an archive.
- Empty or missing `[log_rotate_path]` means truncate-only.
- `evtlog_rotate_size` is truncate-only, no archive.
- `evtlog_rotate_size` can coexist with file rotation settings.

## Testing with fill_dummy_data.py

Use `fill_dummy_data.py` to generate files of a specified size for testing.

### Prerequisites

- Python 3.
- `fill_dummy_data.py` script.
- Agent running and monitoring the configured log path.
- Use elevated PowerShell if writing under `C:\\Program Files`.

### Test A — Archive + truncate (per-log)

1. Configure `agent_config`:
   - `[logs]`
     - `log.postgresql.db = C:\\Program Files\\PostgreSQL\\16\\data\\log\\postgresql.log`
   - `[log_rotate_path]`
     - `log.postgresql.db = C:\\Program Files\\PostgreSQL\\16\\data\\log\\postgresql_backup.log`
   - `[log_rotate_size]`
     - `log.postgresql.db = 10485760`
   - Reload/restart the agent if required.

2. Create a file over threshold:

    ```powershell
    python "C:\Users\testuser\OneDrive\Desktop\Work\temp\fill_dummy_data.py" "C:\Program Files\PostgreSQL\16\data\log\postgresql.log" 20485760
    ```

3. Verify:

- `postgresql_backup.log` grows (appended).
- `postgresql.log` shrinks, retaining only the tail.

```powershell
(Get-Item 'C:\Program Files\PostgreSQL\16\data\log\postgresql.log').Length
(Get-Item 'C:\Program Files\PostgreSQL\16\data\log\postgresql_backup.log').Length
```

### Test B — Truncate-only (per-log)

1. Remove or leave empty the `[log_rotate_path]` value for the key.
1. Keep `[log_rotate_size] = 10485760`.
1. Recreate/extend the file above threshold:

```powershell
python "C:\Users\testuser\OneDrive\Desktop\Work\temp\fill_dummy_data.py" "C:\Program Files\PostgreSQL\16\data\log\postgresql.log" 20485760
```

1. Expected: only the source file is truncated; no archive file changes or creation.

### Test C — Windows Event Logs (truncate-only)

1. Set `evtlog_rotate_size` (e.g., `evtlog_rotate_size = 1000`).
1. Ensure Windows Event Log collection is enabled (e.g., `win_events`, `sys_events`, `app_events`).
1. Generate sufficient event activity (e.g., service changes, logon attempts).
1. Expected: truncate-only behavior; no archive file produced. This setting does not affect non-Windows files in `[logs]`.

## Troubleshooting

- Archive not growing:
  - Confirm `[log_rotate_path]` is present for the key and points to a writable location.
  - Check process permissions.
- File not shrinking:
  - Ensure file exceeded `[log_rotate_size]` and is at least `MIN_ROTATION_SIZE` (1MB).
  - Verify the monitored path matches `[logs]` exactly.
- Rotation not triggering:
  - Append a few more bytes to prompt detection after crossing the threshold.

## Notes

- Archive files are appended to, not overwritten.
- If copy fails, the source is left unchanged (best effort to avoid data loss).
- Quote paths with spaces in manual commands.
