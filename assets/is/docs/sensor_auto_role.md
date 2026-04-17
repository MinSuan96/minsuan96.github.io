---
Title: Sensor Auto Role
author: Teh Min Suan
date: 6 April 2026
---

- [Sensor Auto Role](#sensor-auto-role)
  - [Overview](#overview)
  - [Purpose](#purpose)
  - [Architecture](#architecture)
    - [Components](#components)
    - [Data Flow](#data-flow)
  - [How It Works](#how-it-works)
    - [1. Role Assignment](#1-role-assignment)
    - [2. Tag Assignment](#2-tag-assignment)
    - [3. System Type Detection](#3-system-type-detection)
    - [4. Scheduling](#4-scheduling)
  - [Configuration](#configuration)
    - [Constants](#constants)
    - [MongoDB Collections](#mongodb-collections)
    - [Redis Keys](#redis-keys)
  - [Installation and Setup](#installation-and-setup)
    - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Starting the Script](#starting-the-script)
    - [Stopping the Script](#stopping-the-script)
    - [Monitoring the Service](#monitoring-the-service)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Log Locations](#log-locations)
  - [Related Files](#related-files)

# Sensor Auto Role

## Overview

Sensor Auto Role is a Python-based background service that automatically assigns roles and tags to sensors in the ContextGuard platform. It inspects Redis routing keys to determine what type of system a sensor is installed on (Windows, Linux, SharePoint, or database), then writes the detected roles back to MongoDB. It also applies tag assignments to sensors by evaluating regex-based filter rules stored in the `customer_pref` collection.

## Purpose

1. **Automatic Role Detection**: Eliminate the need to manually configure sensor roles by inferring them from the data the sensor is already producing.
2. **Tag Management**: Keep sensor tags in sync with customer-defined filter rules without manual intervention.
3. **Continuous Synchronisation**: Run on a recurring schedule so that newly onboarded sensors are classified without requiring a restart or manual action.

## Architecture

### Components

- **Role updater** (`run_role_update`): Reads the sensor list from `customer_pref`, scans Redis for routing keys that match each sensor name, determines the system type from those keys, and writes the result back to `customer_pref`.
- **Tag updater** (`run_tag_update`): Reads server entities from `visuals_entity_card`, evaluates each sensor name against the regex filter rules stored in `customer_pref`, and writes any new tags back to `visuals_entity_card`.
- **System type classifier** (`check_system_type`): Inspects a set of Redis routing keys and maps them to one of four system categories using keyword lists defined as module-level constants.
- **APScheduler**: Runs both updaters every 2 minutes in the background. Both jobs are coalesced and limited to a single concurrent instance.

### Data Flow

```
Redis (routing keys)
        │
        ▼
check_system_type()  ──► customer_pref.roles.<sensor>.services (MongoDB)

customer_pref.sensor_tag_filter (MongoDB)
        │
        ▼
check_condition()    ──► visuals_entity_card.tags (MongoDB)
```

## How It Works

### 1. Role Assignment

`run_role_update` is called with `non_empty=True`, which skips sensors that have no registered agents.

For each sensor in the `customer_pref["sensor"]` document:

1. Queries Redis for all keys matching `*<sensor_name>*`.
2. Passes the matched keys to `check_system_type`, which returns a set of system labels (e.g., `{"windows", "db"}`).
3. Compares the detected systems against the sensor's existing `services` list.
4. If a new system type is found, appends it and updates the document with:

```mongodb
{ "$set": { "roles.<sensor_name>.services": <updated_list> } }
```

### 2. Tag Assignment

`run_tag_update` reads all documents of type `"server"` from `visuals_entity_card`.

For each sensor:

1. Loads the current tag list (defaults to `[]` if missing).
2. Retrieves the filter rules from `customer_pref` under the key `"sensor_tag_filter"`. Each rule contains:
   - `keys`: a list of regex patterns that must all match the sensor's entity name.
   - `tags`: a list of tags to apply when all patterns match.
3. Calls `check_condition`, which uses `re.search` and requires every pattern in `keys` to match.
4. Appends any tags not already present and updates the document with:

```mongodb
{ "$set": { "tags": <updated_list> } }
```

### 3. System Type Detection

`check_system_type` decodes each Redis key (bytes → UTF-8) and checks it against four identifier lists:

| System label | Identifier keywords                                             |
| ------------ | --------------------------------------------------------------- |
| `windows`    | `sys_events`, `win_events`, `share_events`, `windows`           |
| `linux`      | `ssh`, `linux`                                                  |
| `sharepoint` | `sharepoint`                                                    |
| `db`         | `db`, `database`, `sql`, `mysql`, `postgresql`, `oracle`, `db2` |

Each key is matched against every system's identifiers and, on the first match, the system label is added to the result set. A single Redis key can only contribute one system label (the first match wins). Multiple keys can each contribute different labels.

### 4. Scheduling

On startup, both updaters are run immediately, then handed off to APScheduler:

- **Interval**: every 2 minutes.
- **Coalescing**: missed executions are collapsed into a single run.
- **Max instances**: 1 — a running job will not be launched again until it completes.
- **Status logging**: every hour the main thread logs cumulative counts of tag and role updates performed since startup.

## Configuration

### Constants

```python
WINDOWS_IDENTIFIER  = ["sys_events", "win_events", "share_events", "windows"]
LINUX_IDENTIFIER    = ["ssh", "linux"]
SHAREPOINT_IDENTIFIER = ["sharepoint"]
DB_IDENTIFIER       = ["db", "database", "sql", "mysql", "postgresql", "oracle", "db2"]

IDENTIFIER_MAP = {
    "windows":    WINDOWS_IDENTIFIER,
    "linux":      LINUX_IDENTIFIER,
    "sharepoint": SHAREPOINT_IDENTIFIER,
    "db":         DB_IDENTIFIER,
}
```

To add a new system type, add a new identifier list and a corresponding entry in `IDENTIFIER_MAP`.

### MongoDB Collections

**`customer_pref`**

- Document with `_key: "sensor"`: holds the sensor role registry.
  ```json
  {
    "_key": "sensor",
    "roles": {
      "<sensor_name>": {
        "agents": [...],
        "services": ["windows", "db"]
      }
    }
  }
  ```
- Document with `_key: "sensor_tag_filter"`: holds tag assignment rules.
  ```json
  {
    "_key": "sensor_tag_filter",
    "filters": [
      {
        "keys": ["^prod-", "\\.windows$"],
        "tags": ["production", "windows"]
      }
    ]
  }
  ```

**`visuals_entity_card`**

- Documents with `type: "server"` are the sensor records that receive tag updates.
  ```json
  {
    "entity": "<sensor_name>",
    "type": "server",
    "tags": ["production", "windows"]
  }
  ```

### Redis Keys

The script queries Redis using the pattern `*<sensor_name>*`. The content of the key is not read — only its name is inspected for system-type identifier keywords.

Examples of keys that would trigger role assignment:

- `routing.sys_events.server01` → classified as `windows`
- `routing.ssh.linuxhost` → classified as `linux`
- `routing.postgresql.dbserver` → classified as `db`

## Installation and Setup

### Prerequisites

- Python 3.x
- Required packages: `redis`, `apscheduler`
- MongoDB instance accessible via `env_helper`
- Redis instance on `localhost` (default port)

## Usage

### Starting the Script

```bash
cd /home/bitnami/casw
./algo.rb start sensor_auto_role sensor_auto_role.py
```

### Stopping the Script

```bash
./algo.rb stop sensor_auto_role sensor_auto_role.py
```

Then remove the entry from `monit/algos_main.monit`.

### Monitoring the Service

```bash
# Check service status
monit status sensor_auto_role

# View logs
tail -f /home/bitnami/casw/nohup-$(hostname).out | grep sensor_auto_role
tail -f /home/bitnami/casw/log/sensor_auto_role-$(hostname).log
```

The script logs cumulative update counts every hour:

```
Update Statistics - Total tag updates: 12 | Total role updates: 5 (total)
```

## Troubleshooting

### Common Issues

1. **No roles assigned**: Verify that Redis contains keys matching the sensor names stored in `customer_pref["sensor"]["roles"]`. Use `redis-cli keys "*<sensor_name>*"` to check.
2. **No tags assigned**: Confirm that a `sensor_tag_filter` document exists in `customer_pref` and that its `filters` array is non-empty. Verify the regex patterns in `keys` are valid and match the intended sensor entity names.
3. **Sensors skipped during role update**: The default call uses `non_empty=True`, so sensors without any registered agents are intentionally skipped. Check the `agents` field in the `customer_pref` sensor document.
4. **Redis connection error**: Ensure Redis is running on `localhost` at the default port (6379).
5. **MongoDB connection error**: Verify that `env_helper` is configured with a reachable MongoDB instance and that the `contextguard` database exists.

### Log Locations

- Main logs: `/home/bitnami/casw/nohup-$(hostname).out`
- Script-specific logs: `/home/bitnami/casw/log/sensor_auto_role-$(hostname).log`

## Related Files

- **Main implementation**: `algos/sensor_auto_role/sensor_auto_role.py`
- **Test suite**: `tests/fast/algos/sensor_auto_role/`
- **Monit configuration**: `monit/algos_main.monit`
- **Environment helper**: `lib/py/env_helper.py`
