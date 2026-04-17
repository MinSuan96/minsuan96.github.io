---
Title: Log Activity Monitor
author: Teh Min Suan
date: 18 July 2025
---

- [Log Activity Monitor](#log-activity-monitor)
  - [Overview](#overview)
  - [Purpose](#purpose)
  - [Architecture](#architecture)
    - [Components](#components)
      - [1. ResourceManager Class](#1-resourcemanager-class)
      - [2. LogActivityMonitor Class](#2-logactivitymonitor-class)
    - [Data Flow](#data-flow)
  - [How It Works](#how-it-works)
    - [1. Data Collection](#1-data-collection)
    - [2. Data Processing](#2-data-processing)
    - [3. Anomaly Detection Algorithm](#3-anomaly-detection-algorithm)
    - [4. Configuration Management](#4-configuration-management)
    - [5. Alert Generation](#5-alert-generation)
    - [6. Scheduling](#6-scheduling)
  - [Configuration](#configuration)
    - [Constants](#constants)
    - [JSON Configuration File](#json-configuration-file)
    - [MongoDB Collections](#mongodb-collections)
    - [Redis Keys](#redis-keys)
  - [Installation and Setup](#installation-and-setup)
    - [Prerequisites](#prerequisites)
    - [Environment Setup](#environment-setup)
  - [Usage](#usage)
    - [Starting the Monitor](#starting-the-monitor)
      - [Using the Algorithm Framework](#using-the-algorithm-framework)
    - [Configuring Thresholds](#configuring-thresholds)
      - [Monit Service Management](#monit-service-management)
    - [Stopping the Monitor](#stopping-the-monitor)
    - [Monitoring the Service](#monitoring-the-service)
  - [Historical Data Access](#historical-data-access)
    - [MongoDB Query Examples](#mongodb-query-examples)
    - [Data Structure in MongoDB](#data-structure-in-mongodb)
  - [Testing](#testing)
    - [Test Script](#test-script)
    - [Test Features](#test-features)
    - [Running Tests](#running-tests)
    - [Test Menu Options](#test-menu-options)
  - [Alert Integration](#alert-integration)
    - [Email Report Integration](#email-report-integration)
    - [Alert Message Format](#alert-message-format)
    - [Alert Content](#alert-content)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Log Locations](#log-locations)
    - [Performance Monitoring](#performance-monitoring)
  - [Future Enhancements](#future-enhancements)
  - [Related Files](#related-files)

# Log Activity Monitor

## Overview

The Log Activity Monitor is a Python-based anomaly detection system that monitors log ingestion rates from various sources within the ContextGuard platform. It tracks the volume of logs received from different sensors and applications, detecting unusual patterns that might indicate system issues, sensor failures, or security incidents.

## Purpose

The primary goals of the Log Activity Monitor are:

1. **Early Detection**: Identify anomalies in log ingestion patterns before they impact system performance
2. **System Health Monitoring**: Monitor the health of log sources and data pipelines
3. **Alerting**: Automatically notify administrators when anomalies are detected
4. **Historical Analysis**: Maintain historical data for trend analysis and capacity planning

## Architecture

### Components

#### 1. ResourceManager Class

Handles the initialization and cleanup of external resources:

- **MongoDB Client**: Stores historical metrics and configuration
- **Redis Client**: Retrieves real-time log counts from metrics
- **RabbitMQ Client**: Publishes alerts to the email reporting system
- **Logger**: Provides structured logging capabilities

#### 2. LogActivityMonitor Class

Contains the core monitoring logic:

- **Metrics Collection**: Gathers log counts from Redis
- **Anomaly Detection**: Uses Exponential Moving Average (EMA) for statistical analysis
- **Data Persistence**: Stores metrics in MongoDB
- **Alert Generation**: Creates and sends alerts when anomalies are detected
- **Configuration Management**: Handles JSON-based configuration for frequency and thresholds

### Data Flow

```flowchart
Redis (Real-time metrics) → LogActivityMonitor → MongoDB (Historical data)
                                    ↓
                            Anomaly Detection (EMA)
                                    ↓
                            RabbitMQ (Alerts) → Email Report System
```

## How It Works

### 1. Data Collection

The monitor collects metrics from Redis keys with the pattern `*rabbitmq_exchange-m.out*`. These keys contain:

- Source information (scalable role/sensor)
- Subsystem (e.g., os, db, app)
- Log count values

### 2. Data Processing

For each Redis key:

1. Extracts the scalable role from the key name
2. Queries MongoDB to determine application types for the source
3. Creates a unique log type identifier: `{scalable_role}_._{sub_system}_._{app_type}`
4. Updates the corresponding DataFrame with the new count

### 3. Anomaly Detection Algorithm

The system uses a dual-threshold approach combining **Exponential Moving Average (EMA)** with **custom thresholds**:

**EMA-Based Detection:**

- **Window Size**: 14 days worth of data points
- **EMA Calculation**: `ewm(span=WINDOW_SIZE, adjust=False).mean().shift(1)`
- **Bounds Calculation**:
  - Lower bound: `EMA - 2 × standard_deviation`

**Threshold-Based Detection:**

- **Custom Thresholds**: Per-log-type minimum acceptable counts (configured in JSON)
- **Default Threshold**: -1 (disabled) for new log types

**Anomaly Conditions:**

- Count falls below EMA lower bound, OR
- Count falls below the custom threshold (if threshold > -1)

### 4. Configuration Management

The system supports JSON-based configuration through `log_activity_monitor.json`:

**Auto-Generation:**

- If no configuration file exists, the system scans Redis and MongoDB to create one
- Discovers all log types and sets default thresholds to -1 (disabled)
- Sets default frequency to 1440 minutes (24 hours)

**Configuration Structure:**

```json
{
  "frequency": 1440,
  "threshold": {
    "sensor1_._os_._windows": 100,
    "sensor2_._db_._sql": 50,
    "sensor3_._app_._unknown": -1
  }
}
```

### 5. Alert Generation

When anomalies are detected:

1. Formats timestamp and count information (UTC+8 timezone)
2. Creates a detailed alert message indicating log drop
3. Publishes to RabbitMQ exchange `email_report` with type `SYS_ALR`
4. Marks the data points as checked to prevent duplicate alerts

**Alert Message Format:**

- Includes specific log counts for each detected timestamp
- Clearly indicates it's a "drop in received logs"
- Provides source, application type, and subsystem information

### 6. Scheduling

The monitor runs on a configurable schedule:

- **Metrics Update**: Configurable frequency (default: every 24 hours / 1440 minutes)
- **Data Persistence**: Adaptive based on frequency (minimum: every hour)
- **Anomaly Check**: Daily at 3:00 AM

**Frequency Configuration:**

- Controlled via JSON configuration file
- Affects both update interval and window size calculation
- Default setting optimized for daily monitoring

## Configuration

### Constants

```python
PIKA_EXCHANGE_OUT = "email_report"    # RabbitMQ exchange for alerts
LOCK = threading.Lock()               # Thread synchronization
```

### JSON Configuration File

**Location**: `algos/log_activity_monitor/log_activity_monitor.json`

**Structure**:

```json
{
  "frequency": 1440,
  "threshold": {
    "sensor-name_._subsystem_._app-type": threshold_value,
    "example-server_._os_._windows": 100,
    "db-server_._db_._sql": 50,
    "new-sensor_._app_._unknown": -1
  }
}
```

**Parameters**:

- `frequency`: Update interval in minutes (default: 1440 = 24 hours)
- `threshold`: Per-log-type minimum acceptable counts
  - Value > 0: Custom threshold (alert if count drops below this)
  - Value = -1: Threshold disabled (only EMA-based detection)

**Auto-Generation**: If the file doesn't exist, it's automatically created with:

- Default frequency of 1440 minutes (1 day)
- All discovered log types with threshold = -1

### MongoDB Collections

- **log_activity_monitor**: Stores historical metrics data
  - `log_type`: Unique identifier for the log source
  - `epoch`: Array of timestamps
  - `count_list`: Array of log counts
  - `checked`: Array of boolean flags indicating processed status

- **raw_{subsystem}_res**: Contains application type mapping data

### Redis Keys

Pattern: `archiver-events_log-{scalable_role}-line{line_number}.{subsystem}`

Examples:

- `archiver-events_log-server1-line0.os`
- `archiver-events_log-dbserver-line1.db`
- `archiver-events_log-webserver-line0.app`

- Contains integer values representing cumulative log counts
- Values are aggregated by timestamp for each log type

## Installation and Setup

### Prerequisites

- Python 3.x
- Required packages: `pandas`, `redis`, `pymongo`, `pika`, `apscheduler`, `rubymarshal`
- MongoDB instance
- Redis instance
- RabbitMQ instance

### Environment Setup

The monitor uses the `env_helper` module for configuration:

- MongoDB connection settings
- Redis connection settings
- RabbitMQ connection settings
- Logging configuration

## Usage

### Starting the Monitor

#### Using the Algorithm Framework

```bash
cd /home/bitnami/casw
./algo.rb start log_activity_monitor log_activity_monitor.py
```

### Configuring Thresholds

1. **Locate the configuration file**: `algos/log_activity_monitor/log_activity_monitor.json`
2. **Edit thresholds**: Set custom minimum log counts for specific log types
3. **Restart the service**: Changes take effect on next startup

**Getting Log Types**: If you don't know the available log types in your system:

1. **Let the script run once** to auto-generate the JSON file with all discovered log types
2. **Check the generated file** at `algos/log_activity_monitor/log_activity_monitor.json`
3. **Edit the thresholds** for the log types you want to monitor
4. **Restart the script** by killing it and starting again:

   ```bash
   pkill -f log_activity_monitor.py
   ```

**Example threshold configuration:**

```json
{
  "frequency": 1440,
  "threshold": {
    "critical-server_._os_._windows": 100,
    "db-primary_._db_._sql": 50,
    "web-server_._app_._unknown": 10,
    "test-sensor_._os_._linux": -1
  }
}
```

**Threshold Guidelines:**

- Set positive values for critical systems that should maintain minimum log volumes
- Use -1 to disable threshold checking (EMA-only detection)
- Consider normal log volumes when setting thresholds

#### Monit Service Management

The service is managed by Monit with the following configuration:

```monitrc
check process log_activity_monitor matching "log_activity_monitor.py"
    start program = "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/algo.rb start log_activity_monitor log_activity_monitor.py &>>/home/bitnami/casw/nohup-`hostname`.out'" with timeout 5 seconds
    stop program  = "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/algo.rb stop log_activity_monitor log_activity_monitor.py &>>/home/bitnami/casw/nohup-`hostname`.out'"
    if memory > 5% for 2 cycles then exec "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/scripts/log_usage.rb log_activity_monitor.py memory 5%'"
    if cpu > 95% for 40 cycles then exec "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/scripts/log_usage.rb log_activity_monitor.py cpu 95%'"
    if memory > 1 GB for 2 cycles then restart
```

### Stopping the Monitor

```bash
./algo.rb stop log_activity_monitor log_activity_monitor.py
```

Then remove the process from Monit in `algos_main.monit`.

### Monitoring the Service

```bash
# Check service status
monit status log_activity_monitor

# View logs
tail -f /home/bitnami/casw/nohup-$(hostname).out | grep log_activity_monitor
tail -f /home/bitnami/casw/log/log_activity_monitor-$(hostname).log
```

## Historical Data Access

### MongoDB Query Examples

**View all log types being monitored:**

```mongodb
db.log_activity_monitor.find({}, {log_type: 1, _id: 0})
```

**Check data for a specific log type:**

```mongodb
db.log_activity_monitor.findOne({log_type: "sensor-name_._os_._windows"})
```

**View recent data points for all log types:**

```mongodb
db.log_activity_monitor.find({}, {
  log_type: 1,
  count_list: {$slice: -10},
  epoch: {$slice: -10},
  _id: 0
})
```

**Find log types with recent anomalies (unchecked data):**

```mongodb
db.log_activity_monitor.find({
  "checked": {$elemMatch: {$eq: false}}
}, {log_type: 1, _id: 0})
```

**Count total data points per log type:**

```mongodb
db.log_activity_monitor.aggregate([
  {$project: {
    log_type: 1,
    data_points: {$size: "$count_list"}
  }}
])
```

### Data Structure in MongoDB

Each document in the `log_activity_monitor` collection contains:

- **log_type**: String identifier (format: `scalable_role_._subsystem_._app_type`)
- **epoch**: Array of Unix timestamps
- **count_list**: Array of log counts corresponding to each timestamp
- **checked**: Array of boolean flags indicating if anomaly detection has been performed

**Example Document:**

```json
{
  "log_type": "webserver-01_._os_._linux",
  "epoch": [1642723200, 1642726800, 1642730400],
  "count_list": [150, 145, 160],
  "checked": [true, true, false]
}
```

## Testing

### Test Script

A comprehensive test script is available at:
`tests/fast/algos/log_activity_monitor/test_log_activity_monitor.py`

### Test Features

1. **Dummy Data Generation**: Creates test data with known anomalies
2. **Multiple Scenarios**: Tests different log types and patterns
3. **Simple Patterns**: Creates basic test cases (e.g., 5, 5, 5, 1000)
4. **Data Visualization**: Displays generated data for verification
5. **Cleanup Utilities**: Removes test data from MongoDB

### Running Tests

```bash
cd /home/bitnami/casw/tests/fast/algos/log_activity_monitor
python3 test_log_activity_monitor.py
```

### Test Menu Options

1. Create simple anomaly pattern (5, 5, 5, 1000)
2. Create comprehensive test scenarios
3. Test the monitor with current data
4. View generated data
5. Cleanup test data
6. Exit

## Alert Integration

### Email Report Integration

The monitor integrates with the email reporting system (`email_report.rb`) by publishing messages to the `email_report` RabbitMQ exchange.

### Alert Message Format

```ruby
{
  "lang": "PYTHON",
  "entity": scalable_role,
  "systime": epoch_list,
  "report_type": "SYS_ALR",
  "other_information": app_type,
  "sub_system": sub_system,
  "body": formatted_alert_message
}
```

### Alert Content

The alert includes:

- **Alert Type**: "We have received a drop in received logs for this log source"
- Source information (scalable role)
- Application type
- Subsystem
- **Detailed Detection Information**: Timestamp and exact log count for each anomaly
- Format: "18 Jul 2025 14:30:00: 5 logs"

## Troubleshooting

### Common Issues

1. **Insufficient Data**: Monitor requires 14 days of data for accurate EMA calculation
2. **Redis Connection**: Ensure Redis is accessible and contains expected `archiver-events_log*` keys
3. **MongoDB Connection**: Verify MongoDB connectivity and collection permissions
4. **RabbitMQ Issues**: Check RabbitMQ exchange configuration and connectivity
5. **Configuration Issues**: Verify JSON configuration file format and permissions
6. **Frequency Settings**: Ensure frequency setting is appropriate for your monitoring needs

### Log Locations

- Main logs: `/home/bitnami/casw/nohup-$(hostname).out`
- Monitor-specific logs: Check logger output in the main log file

### Performance Monitoring

- Memory usage should stay below 5% of system memory
- CPU usage should remain below 95%
- Automatic restart if memory exceeds 1GB

## Future Enhancements

1. **Adaptive Thresholds**: Dynamic threshold adjustment based on historical patterns
2. **Machine Learning**: Integration of ML models for more sophisticated anomaly detection
3. **Real-time Dashboards**: Web-based monitoring interfaces
4. **Custom Alert Rules**: User-configurable anomaly detection rules
5. **Trend Analysis**: Long-term trend analysis and reporting

## Related Files

- **Main Implementation**: `algos/log_activity_monitor/log_activity_monitor.py`
- **Configuration File**: `algos/log_activity_monitor/log_activity_monitor.json`
- **Test Suite**: `tests/fast/algos/log_activity_monitor/test_log_activity_monitor.py`
- **Monit Configuration**: `monit/algos_main.monit`
- **Email Integration**: `algos/email_report/email_report.rb`
