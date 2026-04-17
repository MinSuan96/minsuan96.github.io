---
Title: Storage Alert System Documentation
Author: Teh Min Suan
Date: 27 March 2025
---

- [Storage Alert System](#storage-alert-system)
  - [Overview](#overview)
  - [Features](#features)
  - [Configuration](#configuration)
    - [Configuration Parameters](#configuration-parameters)
    - [Configuration Steps (Using MongoDB Shell)](#configuration-steps-using-mongodb-shell)
  - [System Components](#system-components)
    - [Storage Alert Script (`storage_alert.py`)](#storage-alert-script-storage_alertpy)
      - [Initialization Functions](#initialization-functions)
      - [Monitoring Functions](#monitoring-functions)
      - [Main Function](#main-function)
    - [Threading Model](#threading-model)
  - [Alert Types](#alert-types)
    - [Database Storage Alert](#database-storage-alert)
    - [Collection Storage Alert](#collection-storage-alert)
    - [Elasticsearch Storage Alert](#elasticsearch-storage-alert)
    - [Alert Rate Warning](#alert-rate-warning)
  - [Alert Message Format](#alert-message-format)
  - [Usage Guidelines](#usage-guidelines)
    - [Setup and Installation](#setup-and-installation)
    - [Running the Monitoring System](#running-the-monitoring-system)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Logging](#logging)

# Storage Alert System

## Overview

The Storage Alert System is a monitoring solution designed to track storage usage metrics for MongoDB and Elasticsearch databases, as well as alert rates in Redis. It sends notifications once per day when predefined thresholds are exceeded, helping to prevent storage-related issues before they become critical.

## Features

- **MongoDB Storage Monitoring**: Checks overall database storage and individual collection sizes
- **Elasticsearch Storage Monitoring**: Monitors Elasticsearch cluster storage usage
- **Alert Rate Monitoring**: Tracks the rate of alerts being generated in Redis
- **Configurable Thresholds**: All thresholds and check intervals are configurable via JSON
- **Alert Notifications**: Sends detailed HTML-formatted alert messages via RabbitMQ

## Configuration

The system uses a JSON configuration file (`storage_alert.json`) to define thresholds and monitoring parameters:

```json
{
    "alert_rate_threshold": 10000000,
    "alert_check_interval": 300,
    "mongo_threshold": 0.7,
    "es_threshold": 0.7,
    "collections": {
        "raw_os_res": 100000000000000
    }
}
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `alert_rate_threshold` | float | Maximum number of alerts per minute before triggering a rate alert |
| `alert_check_interval` | integer | Interval in seconds between alert rate checks |
| `mongo_threshold` | float | MongoDB storage threshold as a ratio (e.g., 0.7 = 70%) |
| `es_threshold` | float | Elasticsearch storage threshold as a ratio (e.g., 0.7 = 70%) |
| `collections` | object | Collection-specific thresholds in GB |

For the `collections` object, each key represents a collection name, and the value represents the threshold in GB for that specific collection.

> **Note**: It is recommended to keep the `mongo_threshold` and `es_threshold` values at 0.7 (70%) as this provides a good balance between early warning and reducing false alarms. Other parameters should be configured according to your specific system requirements. For instance, `alert_rate_threshold` and `alert_check_interval` can be adjusted based on your system's normal alert volume and responsiveness needs.

### Configuration Steps (Using MongoDB Shell)

To properly configure the Storage Alert System with appropriate collection thresholds:

1. **Identify Large Collections**:

   ```MongoDB
   mongo
   use contextguard
   db.runCommand({ listCollections: 1 })
   ```

2. **Check Collection Sizes**:

   ```MongoDB
   mongo
   use contextguard
   db.collection_name.stats()
   ```

   Look for `storageSize` and `totalIndexSize` values, which together represent the total size.

3. **Configure Collection Thresholds**:
   - Open `storage_alert.json` in a text editor
   - Under the `collections` object, add entries for collections you want to monitor:

     ```json
     "collections": {
       "collection_name": threshold_in_bytes
     }
     ```

   - Use a value approximately 20-30% higher than the current size

4. **Verify Configuration**:
   - Ensure the JSON file is valid with no syntax errors
   - Use a JSON validator if needed
   - Check file permissions (needs to be readable by the Storage Alert service)

5. **Apply Changes**:
   - The Storage Alert system will automatically load the configuration on next restart
   - No need to restart MongoDB

## System Components

### Storage Alert Script (`storage_alert.py`)

The main script that implements the monitoring system. It consists of several modules:

#### Initialization Functions

- `initialize_logger`: Sets up the application logger
- `load_config_from_json`: Loads configuration settings from the JSON file
- `initialize_mongo`: Connects to MongoDB
- `initialize_elasticsearch`: Connects to Elasticsearch
- `initialize_pika`: Sets up RabbitMQ connection
- `initialize_redis`: Connects to Redis

#### Monitoring Functions

- `check_mongo`: Monitors MongoDB storage usage
- `check_elasticsearch`: Monitors Elasticsearch storage usage
- `checkAnomaly`: Generic function to check if storage exceeds a threshold
- `monitor_alert_rate`: Continuously monitors alert rates in Redis

#### Main Function

- `run`: Main execution function that calls individual monitoring checks

### Threading Model

The system uses a multi-threaded approach:

1. **Main Thread**: Handles MongoDB and Elasticsearch monitoring, scheduled to run daily
2. **Alert Rate Thread**: Continuously monitors alert rates in Redis at configurable intervals

## Alert Types

The system can generate the following types of alerts:

### Database Storage Alert

Triggered when overall MongoDB storage exceeds the configured threshold.

### Collection Storage Alert

Triggered when a specific MongoDB collection exceeds its size threshold.

### Elasticsearch Storage Alert

Triggered when Elasticsearch storage usage exceeds the configured threshold.

### Alert Rate Warning

Triggered when the system detects an abnormal rate of alerts being generated.

## Alert Message Format

All alerts are sent via RabbitMQ in HTML format with the following structure:

```html
<html>
<body>
    <h2>[Alert Type]</h2>
    <p>[Alert Description]</p>
    <ul>
        <li><strong>[Metric Name]:</strong> [Metric Value]</li>
        <!-- Additional metrics -->
    </ul>
    <p>Please contact InsiderSecurity staff to prevent storage issues.</p>
</body>
</html>
```

## Usage Guidelines

### Setup and Installation

1. Update the relevant files in the target environment
2. Create a `storage_alert.json` configuration file in the same directory
3. Configure thresholds according to your system's specifications
4. Make sure that `System Alerts` is enabled in the dashboard notification settings.

### Running the Monitoring System

The script will be run by monit.

When executed, it will:

1. Load configuration from the JSON file
2. Initialize connections to MongoDB, Elasticsearch, and Redis
3. Start a background thread to monitor alert rates
4. Perform an immediate check of storage metrics
5. Schedule daily checks at 1:00 AM

## Troubleshooting

### Common Issues

1. **Missing Configuration File**: Ensure `storage_alert.json` exists in the script directory
2. **Invalid JSON Format**: Verify JSON syntax is correct
3. **Connection Failures**: Check that MongoDB, Elasticsearch, and Redis are accessible
4. **Threshold Too Low**: If receiving too many alerts, adjust thresholds upward

### Logging

The script logs information, warnings, and errors using the `env_helper` logger. Check log files for detailed information about the system's operation.
