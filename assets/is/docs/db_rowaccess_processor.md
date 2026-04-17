---
Title: db_rowaccess_processor
author: Teh Min Suan
date: 15 August 2025
---

- [DB Row Access Processor](#db-row-access-processor)
  - [Overview](#overview)
  - [How the Python processor works](#how-the-python-processor-works)
  - [What changed from the Ruby version](#what-changed-from-the-ruby-version)
  - [How to run](#how-to-run)
    - [Via Monit](#via-monit)
    - [Manually via algo.rb](#manually-via-algorb)
  - [Integration test](#integration-test)
  - [Troubleshooting](#troubleshooting)

# DB Row Access Processor

This document explains how `db_rowaccess_processor.py` works, what changed from the legacy Ruby implementation (`db_rowaccess_processor.rb`), and how to run the service and its integration test.

---

## Overview

The DB Row Access Processor detects anomalous SQL row-access behavior by learning historical patterns of rows returned per user against database server roles. When a user’s recent activity deviates from the baseline, an anomaly is recorded in MongoDB and an alert is published.

Data and outputs:

- Input collection: `raw_db_res` (docs with `res_type: "rows"` and `action_extra.row_sent`)
- Model state storage: `pro_db_dml_rowsstats`
- Feedback (labels): `algo_db_feedback` (type `db_rowsent`)
- Visualization: `anomaly_graph`
- Alerts (outbound): RabbitMQ fanout exchange `email`

---

## How the Python processor works

Components

- ResourceManager
  - Initializes logger, MongoDB client (DB typically `contextguard`), and RabbitMQ connection/channel via `env_helper`.
  - Declares the `email` exchange for outbound alerts.
  - Cleans up connections and logger on shutdown.

- DBRowAccessMonitor
  - Tracks one or more intervals (default as 24 hours) and processes `raw_db_res` in windowed batches from `start_times[interval]` to `start+interval`.
  - Loads existing model state from Mongo on startup and persists it periodically using APScheduler (`BackgroundScheduler`).
  - Accepts a custom `start_time` (epoch seconds). If provided, the monitor backfills from `start_time` up to now and can generate alerts for that historical period. By default, `start_time` is the current time (real-time monitoring only).
  - For each interval run:
    1) `_update_model(interval)` reads `raw_db_res` for `[start, end)`, aggregates row counts per user↔role, updates in-memory models, and advances the `start_times` cursor.
    2) `_check_anomaly(interval, keys)` compares recent counts against the baseline/statistics to find spikes.
    3) Schedules the next run for the interval.
  - Uses a global lock to guard shared structures during model updates and reporting.

- report_anomaly(user, server_role, interval, timestamp)
  - Ensures a feedback document exists in `algo_db_feedback` for `ANOMALY_TYPE='db_rowsent'`.
  - Builds a time-series graph string and details payload from the model window.
  - Inserts a document into `anomaly_graph` (title like `SQL Access Anomaly (<interval> interval)`, `text` = user).
  - Publishes an alert to the RabbitMQ `email` exchange for downstream mailers/handlers.

Important constants

- `ANOMALY_TYPE = 'db_rowsent'`
- `PIKA_EXCHANGE_OUT = 'email'`

Key collections (typical fields)

- `raw_db_res`: `res_type`, `time_received`, `time_log`, `user`, `app_key.key` (server role), `action_extra.row_sent`, `raw`
- `algo_db_feedback`: `_key="<user>|@|<role>|@|db_rowsent"`, `user_name`, `role`, `type`, `isGood`
- `anomaly_graph`: `title`, `text` (user), `graph`, `details`, `x_label`, `y_label`, `graph_type`
- `pro_db_dml_rowsstats`: model summaries/statistics by interval

---

## What changed from the Ruby version

Modernization while preserving core behavior:

- Language/runtime
  - Ruby threads and custom data stores → Python 3 with APScheduler and a dedicated `ResourceManager`.
- Scheduling and persistence
  - Ruby used ad hoc worker threads (5 min / 1 hr) and in-memory caches.
  - Python schedules per interval and adds a daily persistence job to Mongo.
- Concurrency
  - Python uses an explicit lock for thread-safe access to shared model/reporting state.
- Outputs and feedback
  - Same destinations as Ruby (`algo_db_feedback`, `anomaly_graph`, `email` exchange), with standardized keys and payloads.
- Structure and testability
  - Clear separation of concerns (resource init, model update, anomaly check, reporting, persistence) and easier integration testing.
- Historical backfill
  - Python adds the `start_time` parameter to `DBRowAccessMonitor`. This enables backfilling from an arbitrary epoch to now. The Ruby version primarily focused on live, ongoing processing.

Functional parity

- Detects spikes in `row_sent` per user↔role and records visualizations plus alerts as before.
- Consistent x‑axis bucket size per interval. For a given interval (e.g., 5 minutes, 1 hour, 24 hours), the Python version emits uniform time buckets in the graph, ensuring a consistent x‑axis. The Ruby version could produce uneven bucket widths (e.g., 5, 23, 55 minutes).
- Alert point behavior: the Ruby version only considered the last data point in the window as the alert point. The Python version can flag any bucket that breaches the threshold, so multiple points in the same window can independently trigger alerts.

---

## How to run

### Via Monit

Monit supervises the processor so it starts automatically and is restarted if unhealthy. See `monit/algos_dbmon.monit`:

- Excerpt: `check process db_rowaccess_processor matching "db_rowaccess_processor.py"`

### Manually via algo.rb

You can start/stop the processor directly using the orchestration wrapper:

```bash
./algo.rb start db_rowaccess_processor db_rowaccess_processor.py
./algo.rb stop  db_rowaccess_processor db_rowaccess_processor.py
```

Notes

- Ensure `env_helper` is configured for MongoDB and RabbitMQ connectivity.
- Logs are configured via the logger created in `ResourceManager`.

Backfill (custom start_time)

- To process historical windows instead of only real-time, start the script with a custom start epoch (example: 10 days ago):

```python
start = int(time.time()) - 10 * 24 * 3600

def main():
    resources = ResourceManager()
    resources.initialize_all()
    monitor = DBRowAccessMonitor(resources, start_time=start)
    try:
        monitor.run()
    except Exception as e:
        resources.logger.error(f"Error processing DB row access: {e}")
    finally:
        resources.terminate_all()
```

---

## Integration test

Location: `tests/fast/algos/db_monitoring/test_integration_db_rowaccess_processor.py`

What it does

- Inserts realistic synthetic entries into `raw_db_res` for a test user/server over multiple days.
- Always creates one anomaly for “yesterday”; if `days_back >= 8`, also creates a second anomaly “8 days ago”.
- Runs `DBRowAccessMonitor` over 24-hour windows until current time.
- Verifies anomalies in `anomaly_graph` and prints any `algo_db_feedback` entries.
- Cleans up test artifacts (`raw_db_res`, `anomaly_graph`, `algo_db_feedback`) at the end for idempotent runs.

Important reminder

- The “test server” used in generated logs must be under monitoring of the user’s report group; otherwise, the anomaly may not appear in your expected reports/review flows. Adjust `test_user` and `test_server` if needed.

How to run

- With pytest (preferred): use your workspace test task or run `pytest` filtered to that file.
- Directly: `python tests/fast/algos/db_monitoring/test_integration_db_rowaccess_processor.py`

Tunable parameters

- `days_back`: `>= 8` → two anomalies (yesterday + 8 days ago), otherwise one anomaly.
- `test_user` / `test_server`: set to entities visible in your report group’s monitoring scope.

Expected results

- Console output shows inserted log counts, anomaly detection summary, and any `anomaly_graph` IDs.
- Cleanup summary shows how many documents were removed from each collection.

---

## Troubleshooting

- Missing imports (`env_helper`, `db_rowaccess_processor`)
  - Run on the appliance or ensure `PYTHONPATH` includes CASW library and algorithm paths.
- No anomalies detected
  - Confirm the monitor’s start time covers the generated data window.
  - Use `days_back >= 8` if you expect two anomalies.
  - Ensure the test server is monitored by your report group.
- No outbound alerts
  - Verify RabbitMQ connectivity and Monit status for the email/alerting pipeline.
