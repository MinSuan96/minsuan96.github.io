---
Title: MariaDB Parser
Author: Teh Min Suan
Date: 21 January 2026
---

# MariaDB Parser

## Overview

The MariaDB Parser (`parser_mariadb.py`) is a Python-based message processing service that consumes MariaDB audit log messages from RabbitMQ, parses them into structured event data, and publishes the processed events to another RabbitMQ exchange for downstream consumption.

### Key Features

- Consumes MariaDB **server audit log** messages in CSV format
- Parses and normalizes database operations (CONNECT, DISCONNECT, QUERY, etc.)
- Classifies operations into security-relevant categories
- Publishes structured events with dynamic routing keys
- Includes retry logic for RabbitMQ connection failures
- Integrates with Redis for metrics tracking

### Difference from parser_mysql_slow.py

**Important:** This parser processes **MariaDB Server Audit Plugin logs**, which is fundamentally different from `parser_mysql_slow.py`:

| Aspect | parser_mariadb.py | parser_mysql_slow.py |
| -------- | ------------------- | ---------------------- |
| **Log Type** | Server Audit Logs | Slow Query Logs |
| **Databases** | MariaDB only | MySQL and MariaDB |
| **Purpose** | Security auditing, compliance | Performance monitoring |
| **Log Content** | All database operations (CONNECT, DISCONNECT, QUERY, etc.) | Only slow queries exceeding threshold |
| **Performance Details** | No query timing or optimization details | Query execution time, lock time, rows examined, etc. |
| **Capture Threshold** | All operations or filter by operation type | Only queries exceeding `long_query_time` |

**Note:** If MariaDB's `long_query_time` is set to `0`, the slow query log will capture all queries similar to audit logs. However:

- Slow query logs provide **additional performance metrics** (execution time, lock time, rows examined, rows sent)
- Audit logs capture **non-query operations** (connections, disconnections, administrative commands)
- Audit logs are designed for **security and compliance** use cases
- Slow query logs are designed for **performance analysis** use cases

Use `parser_mariadb.py` for comprehensive audit trails and security monitoring. Use `parser_mysql_slow.py` when you need detailed query performance information.

## Architecture

### Message Flow

```flow
Sensor
    ↓
Listener (listen_log.py)
    ↓
Adapter (adapter_sensor_syslog.rb)
    ↓
RabbitMQ (standard_raw_log)
    ↓
Queue: standard_log_mariadb_queue
    ↓
Parser (parser_mariadb.py)
    ↓ (processes & classifies)
RabbitMQ (events_log_db)
    ↓
Archiver (event_archiver.py)
```

### Components

1. **Message Consumer**: Listens to `standard_log_mariadb_queue`
2. **Message Parser**: Parses CSV-formatted audit logs
3. **Message Classifier**: Categorizes operations and determines resource types
4. **Message Publisher**: Publishes to `events_log_db` exchange with routing keys
5. **Redis Client**: Tracks processing metrics

## Input Format

### RabbitMQ Message Header

Messages arrive with a Grok-parsed header format:

```log
(role:<role>);&@&;ip:<app_ip>;&@&;time_log:<time_log>;&@&;time_received:<time_received>;&@&;msg:<message>
```

**Example:**

```log
role:mariadb-server;&@&;ip:192.168.1.100;&@&;time_log:1642780800;&@&;time_received:1642780801;&@&;msg:<CSV content>
```

### MariaDB Audit Log Format (CSV)

The `msg` field contains comma-separated values in the following format:

```csv
timestamp,serverhost,username,host,connectionid,queryid,operation,database,raw,retcode
```

**Fields:**

| Field | Description | Example |
| ------- | ------------- | --------- |
| `timestamp` | Log timestamp | `20260120 14:47:18` |
| `serverhost` | Server hostname | `mariadb-server` |
| `username` | Database user | `root` |
| `host` | Client host | `localhost` |
| `connectionid` | Connection ID | `3` |
| `queryid` | Query ID | `3` |
| `operation` | Operation type | `QUERY`, `CONNECT`, `DISCONNECT` |
| `database` | Database name | `bookstore` |
| `raw` | Raw SQL statement | `'SELECT * FROM users'` |
| `retcode` | Return code | `0` (success), non-zero (failure) |

**Example:**

```log
20260120 14:47:18,mariadb-server,root,localhost,3,3,QUERY,bookstore,'SELECT * FROM users WHERE id > 100',0
```

**Special Case:** SQL statements containing commas are properly handled by CSV parser:

```log
20260120 14:47:18,mariadb-server,root,localhost,3,3,QUERY,bookstore,'UPDATE users SET name='John, Doe' WHERE id=1',0
```

## Output Format

### Structured Event Message

The parser outputs msgpack-encoded messages with the following structure:

```python
{
    "app_type": "mariadb",
    "app_key": {
        "key": "mariadb-server",
        "type": "hostname"
    },
    "action_category": "res",          # or "login"
    "res_type": "rows",                # table, db, rows, etc.
    "action_type": "query",            # operation lowercase
    "action_result": "success",        # or "failure"
    "time_log": 1642780800,           # Unix timestamp
    "raw": "SELECT * FROM users WHERE id > 100",
    "user": "root",
    "user_host": "localhost",
    "app_id": "bookstore",
    "action_extra": {
        "connectionid": "3",
        "queryid": "3",
        "retcode": "0"
    }
}
```

### Routing Key Format

Published messages use dynamic routing keys:

```key
<source>.db.<category>.<res_type>.<result>.<action_type>
```

**Components:**

- `source`: Server hostname with `.` and `_` replaced by `-`
- `category`: `login` or `res`
- `res_type`: Resource type (db, rows, table, user, etc.)
- `result`: `success` or `failure`
- `action_type`: Operation name (lowercase)

**Examples:**

- `mariadb-server.db.res.rows.success.query`
- `db-replica.db.login.db.success.connect`
- `mariadb-server.db.res.table.success.create`

## Operation Classification

### Action Categories

| Operation | action_category | res_type | Description |
| --------- | -------------- | -------- | ----------- |
| `CONNECT` | `login` | `db` | Database connection |
| `DISCONNECT` | `login` | `db` | Database disconnection |
| `QUERY` | `res` | `rows` | Generic query |
| `READ` | `res` | `rows` | Read operation |
| `WRITE` | `res` | `rows` | Write operation |
| `CREATE` | `res` | `table` | Create table/object |
| `ALTER` | `res` | `table` | Alter table/object |
| `RENAME` | `res` | `table` | Rename table/object |
| `DROP` | `res` | `table` | Drop table/object |

### Action Result Determination

- `retcode == "0"` → `action_result = "success"`
- `retcode != "0"` → `action_result = "failure"`

## Functions

### Core Processing Functions

#### `onMessage(_ch, method, _properties, body)`

Main message callback function invoked by RabbitMQ consumer.

**Responsibilities:**

1. Decode message body
2. Parse header with Grok pattern
3. Extract and parse CSV message
4. Build routing key
5. Publish to output exchange
6. Handle errors and retries
7. Track metrics in Redis

**Error Handling:**

- Retries up to 3 times on publish failure
- Tracks dropped messages in Redis
- Logs all errors with stack traces

#### `parse_message(message)`

Parses CSV-formatted MariaDB audit log message.

**Parameters:**

- `message` (str): CSV-formatted audit log entry

**Returns:**

- `dict`: Structured event message
- `None`: If parsing fails

**Features:**

- Uses Python CSV parser for proper comma handling in SQL
- Validates field count and required fields
- Converts timestamp to Unix epoch
- Determines action categories and results
- Handles missing database names

#### `build_routing_key(message)`

Constructs RabbitMQ routing key from parsed message.

**Parameters:**

- `message` (dict): Parsed event message

**Returns:**

- `str`: Routing key in format `<source>.db.<category>.<res_type>.<result>.<action_type>`

**Features:**

- Sanitizes hostname (replaces `.` and `_` with `-`)
- Handles missing fields with defaults
- Returns lowercase routing key

#### `classify_res_type(operation)`

Maps MariaDB operation types to resource type categories.

**Parameters:**

- `operation` (str): MariaDB operation type

**Returns:**

- `str`: Resource type (db, rows, table, etc.)

**Mapping:**

- Connection operations → `db`
- Query operations → `rows`
- Schema operations → `table`
- Unknown operations → lowercase operation name

## Configuration

### RabbitMQ Configuration

```python
PIKA_EXCHANGE_IN = "standard_raw_log"
PIKA_QUEUE_IN = "standard_log_mariadb_queue"
PIKA_ROUTING_KEY_IN = '#.db_mariadb.mariadb.db.raw'
PIKA_EXCHANGE_OUT = "events_log_db"
```

**Connection Parameters:**

```python
pika_params = {
    "heartbeat": 600,
    "socket_timeout": 300
}
```

**Queue Parameters:**

```python
queue_arguments = {
    "x-message-ttl": 180000,  # 3 minutes
    "x-max-length": 5000
}
```

**QoS Settings:**

- `prefetch_count`: 10 messages

### Redis Configuration

```python
redis = RedisConn(
    buffer_capacity=10000,
    parser_name="mariadb"
)
```

### Logger Configuration

Logger is initialized through `ENV_HELPER.build_logger()` with default settings.

## Error Handling and Metrics

### Redis Metrics

The parser tracks the following metrics:

| Metric Key | Description | When Incremented |
| ------------ | ------------- | ------------------ |
| `line.line_event.parse-m.error.dropped` | Header or message parsing failed | Invalid format |
| `line.line_event.message_publishing-m.error.dropped` | Failed to publish after 3 retries | RabbitMQ errors |
| `line.line_event.processing-m.error.dropped` | General processing error | Exception caught |
| `line.line_event-m.out` | Successfully published message | Successful publish |

All metrics are tagged with `agent_id` extracted from routing key.

### Retry Logic

**RabbitMQ Publishing:**

- 3 retry attempts on `AMQPChannelError` or `AMQPConnectionError`
- Reconnects to RabbitMQ between retries
- Logs warnings on each retry attempt
- Increments error metric after final failure

### Error Scenarios

1. **Invalid Header Format**
   - Logs error
   - Increments parse error metric
   - Skips message

2. **Invalid CSV Format**
   - Logs error with exception details
   - Returns `None` from `parse_message()`
   - Increments parse error metric

3. **Invalid Timestamp**
   - Logs error
   - Returns `None` from `parse_message()`

4. **RabbitMQ Connection Failure**
   - Attempts reconnection
   - Retries up to 3 times
   - Logs warning and error details

## Usage

### Starting the Parser

```bash
cd algos/db_mariadb
python3 parser_mariadb.py
```

### Prerequisites

- Python 3.x
- Required packages: `msgpack`, `pika`, `pygrok`
- RabbitMQ server accessible via `ENV_HELPER`
- Redis server configured in environment

### Environment Variables

Configured through `env_helper.EnvHelper()`:

- RabbitMQ connection details
- Redis connection details
- Logging configuration

## Example Scenarios

### Scenario 1: Successful Query

**Input:**

```log
role:db-primary;&@&;ip:10.0.1.50;&@&;time_log:1642780800;&@&;time_received:1642780801;&@&;msg:20260120 14:47:18,db-primary,appuser,10.0.2.100,42,156,QUERY,ecommerce,'SELECT * FROM orders WHERE status='pending'',0
```

**Output Message:**

```python
{
    "app_type": "mariadb",
    "app_key": {"key": "db-primary", "type": "hostname"},
    "action_category": "res",
    "res_type": "rows",
    "action_type": "query",
    "action_result": "success",
    "time_log": 1642780800,
    "raw": "SELECT * FROM orders WHERE status='pending'",
    "user": "appuser",
    "user_host": "10.0.2.100",
    "app_id": "ecommerce",
    "action_extra": {
        "connectionid": "42",
        "queryid": "156",
        "retcode": "0"
    }
}
```

**Routing Key:**

```key
db-primary.db.res.rows.success.query
```

### Scenario 2: Failed Connection

**Input:**

```log
role:db-replica;&@&;ip:10.0.1.51;&@&;time_log:1642780900;&@&;time_received:1642780901;&@&;msg:20260120 14:48:20,db-replica,baduser,10.0.2.200,43,0,CONNECT,,,1045
```

**Output Message:**

```python
{
    "app_type": "mariadb",
    "app_key": {"key": "db-replica", "type": "hostname"},
    "action_category": "login",
    "res_type": "db",
    "action_type": "connect",
    "action_result": "failure",
    "time_log": 1642780900,
    "raw": "",
    "user": "baduser",
    "user_host": "10.0.2.200",
    "app_id": "-",
    "action_extra": {
        "connectionid": "43",
        "queryid": "0",
        "retcode": "1045"
    }
}
```

**Routing Key:**

```key
db-replica.db.login.db.failure.connect
```

### Scenario 3: Schema Modification

**Input:**

```log
role:mariadb-prod;&@&;ip:10.0.1.100;&@&;time_log:1642781000;&@&;time_received:1642781001;&@&;msg:20260120 14:50:00,mariadb-prod,dba,localhost,50,200,ALTER,mydb,'ALTER TABLE users ADD COLUMN email VARCHAR(255)',0
```

**Output Message:**

```python
{
    "app_type": "mariadb",
    "app_key": {"key": "mariadb-prod", "type": "hostname"},
    "action_category": "res",
    "res_type": "table",
    "action_type": "alter",
    "action_result": "success",
    "time_log": 1642781000,
    "raw": "ALTER TABLE users ADD COLUMN email VARCHAR(255)",
    "user": "dba",
    "user_host": "localhost",
    "app_id": "mydb",
    "action_extra": {
        "connectionid": "50",
        "queryid": "200",
        "retcode": "0"
    }
}
```

**Routing Key:**

```key
mariadb-prod.db.res.table.success.alter
```

## Troubleshooting

### Common Issues

1. Messages Not Being Consumed

   - Check RabbitMQ queue exists and has bindings
   - Verify routing key pattern matches incoming messages
   - Check queue permissions

2. Parsing Errors

   - Verify CSV format matches expected 10-field structure
   - Check for encoding issues (expecting UTF-8)
   - Review logs for specific parsing errors

3. Publishing Failures

   - Check RabbitMQ connection status
   - Verify output exchange exists
   - Review retry logic in logs

4. Timestamp Conversion Errors

   - Ensure timestamp format is `YYYYMMDD HH:MM:SS`
   - Check timezone considerations

### Debugging

Enable debug logging to see detailed processing:

```python
logger = ENV_HELPER.build_logger(file_name, loglevel="debug")
```

Debug logs include:

- Received raw messages
- Parsed message structures
- Routing key construction
- Publishing attempts

### Monitoring

Monitor Redis metrics for:

- Message throughput (`line.line_event-m.out`)
- Error rates (all `*.error.dropped` keys)
- Agent-specific performance by `agent_id`

## Related Components

- **MariaDB Audit Plugin**: Generates audit logs in CSV format (configured on MariaDB server)
- **Log Collector**: Forwards logs to RabbitMQ
- **parser_mysql_slow.py**: Separate parser for MySQL/MariaDB **slow query logs**
- **Downstream Consumers**: Process categorized events from `events_log_db`
- **Event Archiver**: Archives processed events for long-term storage and analysis

## Future Enhancements

1. **SQL Command Classification**: Parse raw SQL to provide more granular operation types (SELECT, INSERT, UPDATE, DELETE)
2. **Database Extraction**: Extract affected tables/resources from raw SQL
3. **Performance Metrics**: Track query execution time if available in logs
4. **Batch Processing**: Optimize for high-throughput scenarios
5. **Schema Validation**: Validate parsed messages against a schema before publishing
