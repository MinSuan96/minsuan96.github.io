---
Title: Agent Config for Windows Sensor
author: InsiderSecurity
date: 3 October 2025
---

- [Section: `[local agent]`](#section-local-agent)
- [Section: `[logs]`](#section-logs)
- [Section: `[log_rotate_path]`](#section-log_rotate_path)
- [Section: `[log_rotate_size]`](#section-log_rotate_size)
- [Section: `[auth]`](#section-auth)
- [Windows Event Log–Related Sections](#windows-event-logrelated-sections)
- [Derived / Implicit Limits \& Constants](#derived--implicit-limits--constants)
- [Configuration Reload Behavior](#configuration-reload-behavior)
- [Error Handling \& Logging](#error-handling--logging)
- [Best Practices for Editing](#best-practices-for-editing)
- [Example Minimal Configuration](#example-minimal-configuration)
- [Change Log Considerations](#change-log-considerations)
- [Troubleshooting Tips](#troubleshooting-tips)
- [Security Considerations](#security-considerations)
- [Glossary](#glossary)

This document explains every configurable setting supported by the Windows agent as parsed in `windows2/cgagent/cgagent/config.cpp` (and the associated `configuration` struct in `main.h`). It maps INI sections/keys to the agent's internal behavior, lists defaults (where determinable from code), valid value ranges, and operational notes.

The sample file shown earlier (`agent_config`) follows classic INI semantics:

- Sections are in square brackets (e.g. `[local agent]`).
- Keys are case‐sensitive as per direct `strcmp` usage in code.
- Unknown keys are ignored (handler returns 0) and produce an error only if the INI parser is strict.
- Repeated keys override previous values (last one wins) unless logic intentionally preserves earlier entries (e.g. iptables rule re-add suppression).

---

## Section: `[local agent]`

Primary runtime, network capture, compression, retry and logging controls.

| Key | Purpose | Type | Default (code) | Notes |
|-----|---------|------|----------------|-------|
| scalable_role | Logical role name for sensor | string | NULL | Used wherever `config.scalable_role` is referenced (not in this file). |
| sniffer_remote | Analytic server IP | string | NULL (later default of port only) | Freed/replaced on reload. |
| sniffer_remote_port | Analytic server port | int | 22 (set in defaults) | Change it to 441 |
| evtlog_rotate_size | Rotation threshold for Windows Event Log file copy / spool | integer (off_t) | `EVTLOG_ROTATE_SIZE_BYTES` (10 MiB) | Overridden by per-log rotate values if set. |

Notes:

- Memory ownership: any previously set string is freed then replaced (`strdup`). Ensure custom modifications also allocate new memory.
- Invalid / extreme compression settings are sanitized after file parse.

---

## Section: `[logs]`

Maps logical log types (pika routing keys) to file paths or glob patterns. Patterns use Windows `FindFirstFileA` semantics (wildcards `*` and `?`). For each matched file (up to `MAX_LOGS`, global cap), a log tracking slot is either:

- Reused (same file path already in that slot)
- Replaced (slot had a different file path)
- Newly initialized

Per log record fields initialized/reset:

- `file_path`
- `type` (key name)
- `fp` (FILE pointer)
- `last_pos`
- `checksum`
- `tidx` (thread index)
- `event_retryMicrosec`
- `event_source` / `event_ids`
- `etw_source`
- `event_data_format`
- `log_rotate_path` / `log_rotate_size`

Sockets tied to the same index are forcibly closed on reload to allow port/host changes.

Typical keys seen:

- `win_events`
- `share_events`
- `sys_events`
- `app_events`
- `os.windows.account_info`
- `app_events.db_mssql.mssql.db`
- `SQLEvent.db_mssql.mssql.db`
- `shared.event_viewer.sharepoint.app`
- `foundation.event_viewer.sharepoint.app`
- `site_audit.sharepoint.app`
- `evtlog.db_oracle.oracle.db`
- `powershell_events`
- `log.postgresql.db`

You can add additional custom log types, then refine behavior via subsequent sections (winevent, rotation, etc.) referencing the same key name.

---

## Section: `[log_rotate_path]`

Provides an alternate rotation destination file per log type. Keys must match a defined log type from `[logs]`. Value is a file path used when rotation occurs. Stored in `logs[i].log_rotate_path`.

---

## Section: `[log_rotate_size]`

Per-log override threshold (bytes) for rotation. Only applied if value ≥ `MIN_ROTATION_SIZE` (constant defined elsewhere). Stored in `logs[i].log_rotate_size`.

---

## Section: `[auth]`

Authentication / tunneling parameters.

| Key | Purpose | Notes |
|-----|---------|-------|
| user | Username for SSH / remote channel | Stored in `username` |
| user_file | File containing username (alternative) | Stored in `username_file` |

Defaults:

- `password` = empty string
- `key_private` = `<BINARY_DIR>\key_private.txt`
- `key_public`  = `<BINARY_DIR>\key_public.txt`

---

## Windows Event Log–Related Sections

Processed only after `[logs]` defines the key.

| Section | Purpose | Value Format | Stored Fields |
|---------|---------|--------------|---------------|
| winevent_security | Attach security event IDs to a log key | Comma-separated numeric IDs | `event_source="Security"`, `event_ids` list |
| winevent_application | Application log events | Comma-separated IDs | `event_source="Application"` |
| winevent_system | System log events | Comma-separated IDs | `event_source="System"` |
| extra_winevent | Arbitrary event log channel + IDs + retry | `<channel>;;<id list>;;<retryMicrosec>` | `event_source`, `event_ids`, `event_retryMicrosec` |
| extra_winevent_format | Specify data format for extra winevent log | `raw` / `text` / `xml` (string) | `event_data_format` (consumer decides mapping) |
| retroactive_updates_interval | Poll interval for retroactive event pull | integer seconds | `retroactive_updateInterval` |
| retroactive_max_history | Max seconds back to pull historical events | integer seconds | `retroactive_maxhistory` |
| SQLExtendedEvent | ETW / SQL Extended Events channel | Channel / session name | `etw_source` (events enumerated elsewhere) |

Validation: If a key (log type) is not found among existing logs, an informational message is logged and the directive is ignored.

---

## Derived / Implicit Limits & Constants

| Constant | Meaning |
|----------|---------|
| `MAX_LOGS` | Maximum total tracked log files (100 for binary forwarder; global usage for text). |
| `MAX_POLICY` | Maximum number of port policy entries (1000). |
| `COMPRESSION_BLOCK_SIZE` | Default compression block (50,000 bytes). |
| `COMPRESSION_BLOCK_SIZE_MAX` | Maximum allowed block (200,000 bytes). |
| `COMPRESSION_BLOCK_INTERVAL` | Default seconds between forced block send (3). |
| `EVTLOG_SENT_COMPLETE_SEC` | Default wait for complete event log send (600s). |
| `EVTLOG_ROTATE_SIZE_BYTES` | Default rotation threshold for event log copy (10 MiB). |
| `LOG_FORWARDER_MAX_RETRIES_COUNT` | Default retry attempts for log forwarding (20). |
| `MIN_ROTATION_SIZE` | Minimum per-log rotation size for override (10 MiB). |

---

## Configuration Reload Behavior

- All logs are re-evaluated; indices beyond new total are cleaned (file handles closed, sockets closed, metadata cleared).
- For existing indices, if file path changes the old file is closed and state reset.
- Sockets for every (re)loaded log index are terminated to ensure correct remote parameters after reload.
- Compression sanity check applied post-parse.

---

## Error Handling & Logging

- Unknown section/name pairs return 0 (ini parser may log/report).
- Misformatted `extra_winevent` entries (not exactly two delimiters `;;`) produce an error log and are discarded.
- Missing log type references (winevent / rotation / retroactive / etc.) yield informational log lines and are ignored.

---

## Best Practices for Editing

1. Define base log keys in `[logs]` before referencing them in other sections.
2. Keep `compression_block` reasonable; excessive values revert to default if over max.
3. Avoid setting `default_record_all = 1` unless necessary; may cause high bandwidth and storage usage.
4. Use port policies sparingly; each additional entry increases lookup overhead.
5. When introducing new binary log forwarding patterns, keep total under `MAX_LOGS`.
6. Leverage `retroactive_max_history` cautiously to prevent large historical pulls on restart.

---

## Example Minimal Configuration

```agent_config
# Copyright Insider Security Pte Ltd 2015

# Windows Agent

[local agent]

scalable_role = local-test

# enable_network_sniffer = 1

pcap_filter = ip    ;make sure it does not monitor its own traffic

ignore_lo_interface = 1

promiscuous = 0
default_record_ignore = 0
default_record_flow = 1
default_record_basic = 0
default_record_all = 0
use_udp = 0

sniffer = 127.0.0.1
sniffer_port =  1010
log_forward_port =  1013


sniffer_remote = 192.168.8.133
sniffer_remote_port = 441

enable_compression = 1
compression_block = 50000
compression_interval = 3

evtlog_rotate_size = 10000000000000000000000

# ===================================================================================================
#
# Port policy configuration
#
# [port no] = [incoming sport] [incoming dport] [outgoing sport] [outgoing dport]
#
# i means drop
# f means record flow only, ie, ip addresses, data transfer. Flow are send per connection.
# s means record stats only, ie packet len + ip src + ip dest + timestamp. Stats are send per packet
# a means record all. This is send per packet.


# for example
#
# 22 = sisa
# this means for port 22
#
# record stats only if incoming source port is 22
# ignore if incoming dest port is 22
# record stats only if outgoing source port is 22
# record all if outgoing dest port is 22
#
# order of priority if multiple fields match for a packet : record all, record stats, record flow, ignore

[tcp ports]
# maximum 1000 ports allowed, extra ports are rejected

22 = ffff
80 = ffff

[udp ports]
53 = aaaa


[logs]
log.postgresql.db = C:\Program Files\PostgreSQL\16\data\log\postgresql.log
powershell_events = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\powershell_events.log
win_events = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\sec.log
#share_events = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\share.log
#sys_events = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\sys.log
#app_events = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\app_win.log
#os.windows.account_info = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\account_info.log
#app_events.db_mssql.mssql.db = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\app.log
#SQLEvent.db_mssql.mssql.db = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\etw_sql.log
#shared.event_viewer.sharepoint.app = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\event_sp_shared.log
#foundation.event_viewer.sharepoint.app = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\event_sp_foundation.log
#site_audit.sharepoint.app = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\event_sp_site_audit.log
#evtlog.db_oracle.oracle.db = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\sys_oracle_db.log
#win_events_xml = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\sec_xml.log
#share_events_xml = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\share_xml.log
#sys_events_xml = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\sys_xml.log
#app_events_xml = C:\Users\testuser\OneDrive\Desktop\Work\cgagent\logs\app_win_xml.log

[log_rotate_path]
log.postgresql.db = C:\Program Files\PostgreSQL\16\data\log\postgresql_backup.log

[log_rotate_size]
log.postgresql.db = 1100000

[winevent_security]
win_events = 4740,4728,4732,4756,4720,4722,4735,4625,4648,4624,4634,1102,4768,4769,4672,4725,4698,4699,4704,4705,4729,4733,4688,4731,4727,4754,4757,4734,4758,4730,4715,4719,4902,4904,4905,4906,4907,4912,4867,4866,4865,4716,4707,4706,6144,4726,4767,4697,5024,5025,5030,6416,4946,4947,4948,4950,4663,4954,4700,4701,4702
share_events = 5140,5142,5143,5144,5145
#win_events_xml = 4740,4728,4732,4756,4720,4722,4735,4625,4648,4624,4634,1102,4768,4769,4672,4725,4698,4699,4704,4705,4729,4733,4688,4731,4727,4754,4757,4734,4758,4730,4715,4719,4902,4904,4905,4906,4907,4912,4867,4866,4865,4716,4707,4706,6144,4726,4767,4697,5024,5025,5030,6416,4946,4947,4948,4950,4663,4954,4700,4701,4702
#share_events_xml = 5140,5142,5143,5144,5145

[winevent_system]
sys_events = 7040,7045,104,1074,7036,6006,6008,109,13,12
#sys_events_xml = 7040,7045,104,1074,7036,6006,6008,109,13,12

[auth]
user = remote_cg_agent
user_file = remote_cg_file

[winevent_application]
app_events = 1040,1042,1033,11707,11708
#app_events.db_mssql.mssql.db = 18454,18453,18455,18456,33205
#app_events_xml = 1040,1042,1033,11707,11708

[SQLExtendedEvent]
#SQLEvent.db_mssql.mssql.db = XE_DEFAULT_ETW_IS

[extra_winevent]
powershell_events = Microsoft-Windows-PowerShell/Operational;;4104,40962,40961,53504;;0
# Format: key = <source>;;<event ids>;;<retry time>
#shared.event_viewer.sharepoint.app = Microsoft-SharePoint Products-Shared/Operational;;6753,6754,6756,6757,6758, 7039,7041, 8087;;900000
#foundation.event_viewer.sharepoint.app = Microsoft-SharePoint Products-Shared/Audit;;8324,8325,8326;;900000
#evtlog.db_oracle.oracle.db = Application;;34;;900000

[retroactive_updates_interval]
win_events = 1
share_events = 10
sys_events = 0
app_events = 10
#win_events_xml = 1
#share_events_xml = 10
#sys_events_xml = 0
#app_events_xml = 10

[retroactive_max_history]
win_events = 3600
share_events = 3600
sys_events = 3600
app_events = 3600
#win_events_xml = 3600
#share_events_xml = 3600
#sys_events_xml = 3600
#app_events_xml = 3600

#[extra_winevent_format]
#win_events_xml = xml
#share_events_xml = xml
#sys_events_xml = xml
#app_events_xml = xml
```

---

## Change Log Considerations

When adding new keys in code:

- Extend `config_handler` with a new `MATCH` block or section case.
- Update this document to reflect semantics, defaults, and interactions.
- If string, ensure previous memory freed before `strdup`.
- If integer with constraints, sanitize immediately and log adjustments.

---

## Troubleshooting Tips

| Symptom | Likely Cause | Resolution |
|---------|--------------|-----------|
| Log not forwarding | Not defined in `[logs]` or exceeded `MAX_LOGS` | Check logs for "key not found" messages; reduce count. |
| Event IDs ignored | Section processed before `[logs]` key exists | Ensure order: `[logs]` first. |
| High CPU / bandwidth | `default_record_all=1` or many `aaaa` port policies | Reduce scope or switch to flow/stat modes. |
| No compression effect | `enable_compression=0` or block never fills | Enable and/or reduce `compression_block` for frequent sends. |
| Repeated blacklist_rule ignored | Duplicate detection logic | Change rule string or remove existing rule entry. |

---

## Security Considerations

- Large `evtlog_rotate_size` or disabled rotation can retain sensitive data longer on disk.
- Ensure key files (`key_private.txt`, `key_public.txt`) have restricted ACLs.
- Avoid overly permissive glob patterns in `[logs]` that could capture confidential files unintentionally.

---

## Glossary

- Flow: Aggregated connection record summarizing bytes/packets transferred over a TCP/UDP 5-tuple direction.
- Stats: Lightweight per-packet metadata (length, endpoints, timestamp) without full payload.
- All: Full per-packet capture (payload + metadata) as permitted by logic.

---
If any additional internal modules introduce new fields, update both `configuration` struct and this reference accordingly.
