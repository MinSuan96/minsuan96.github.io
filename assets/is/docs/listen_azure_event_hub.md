---
Title: Azure Event Hub Listener (listen_azure_event_hub.py)
author: InsiderSecurity
date: 19 September 2025
---

- [Overview](#overview)
- [Data Flow Detail](#data-flow-detail)
- [Configuration Management (`dbconfig_azure_event_hub.py`)](#configuration-management-dbconfig_azure_event_hubpy)
- [SSH Forwarder Integration](#ssh-forwarder-integration)
- [Runtime Parameters \& Constants](#runtime-parameters--constants)
- [Routing Key](#routing-key)
- [Operational Runbook](#operational-runbook)
- [Quick Reference](#quick-reference)
- [Appendix](#appendix)

# Overview

The Azure Event Hub Listener (`listen_azure_event_hub.py`) ingests log/event data from one or more Azure Event Hubs and republishes the normalized payloads into RabbitMQ under the exchange `received_sensorless_log`. Downstream processing components (notably `listen_sensorless_log.py`) subscribe to this exchange to enrich, classify, and ultimately route logs onward in the wider ContextGuard analytics pipeline.

This document describes the architecture, data flow, configuration management (via `dbconfig_azure_event_hub.py`), operational procedures, scaling approaches, observability touchpoints, and troubleshooting guidance for this ingestion layer.

Companion components:
* `listen_azure_event_hub.py` – Pulls from Azure Event Hubs, buffers, and publishes into RabbitMQ.
* `dbconfig_azure_event_hub.py` – Manages (add/delete/check) Event Hub connection configurations stored in MongoDB (`customer_pref` collection) under key `azure_event_hub`.
* `listen_sensorless_log.py` – Consumes from `received_sensorless_log` exchange and performs sensorless log classification, agent state handling, and re‑publishing.
* (Optional) `connectors/azure_event_hub/azure_event_hub_forwarder.py` – An alternate forwarder (SSH-based) intended for a Windows VM deployment scenario (separate design document `azure_event_hub_forwarder.md`).

---
# Data Flow Detail

1. Configuration Load: `customer_pref.find_one({"_key": "azure_event_hub"})` returns a document:
	 ```json
	 {
		 "_key": "azure_event_hub",
		 "configs": [
			 {
				 "connection_string": "<EH_CONNECTION_STRING>",
				 "event_hub_name": "security-logs",
				 "consumer_group": "$Default"
			 },
			 { /* ... additional hubs ... */ }
		 ]
	 }
	 ```
2. For each config, an `EventHubConsumerClient` is created (connection string + event hub name + consumer group). If misconfigured, initialization logs an error and skips that entry.
3. Each client spawns a receiver thread invoking `client.receive(on_event=process_event_data, ...)`.
4. `process_event_data()` parses `event_data` (Message body → typically JSON or UTF‑8 text). It constructs an internal log dict, adds metadata (e.g., `received_ts`, `src_type='event_hub'`, partition context, event hub name), and enqueues it in `buffer`.
5. `publish_logs()` runs in a dedicated thread: while alive it dequeues logs and publishes to RabbitMQ using exchange `received_sensorless_log` and a routing key computed by `get_routing_key()`.
6. `listen_sensorless_log.py` (separate process) binds queue `listen_sensorless_log` to the same exchange with routing key `#` (all), consumes, classifies, and repackages data to downstream exchanges `received_log` / `standard_raw_log`.

Backpressure handling:
* `buffer` is a bounded queue (size: `BUFFER_SIZE=100000`). If full, producer threads wait (`buffer_not_full.wait(BUFFER_CHECK_INTERVAL)`) before retrying enqueue.
* This prevents unbounded memory usage, at the cost of potential ingestion lag if downstream publishing slows.

Thread supervision:
* A main loop periodically verifies all receiver + publisher threads are alive (interval `THREAD_CHECK_INTERVAL=300s`). Non‑responsive threads can be logged and (future enhancement) restarted.

Graceful shutdown sequence (`exit_gracefully()`):
1. Log intent to shut down.
2. Close RabbitMQ channel & connection.
3. Close each Event Hub client.
4. Close Mongo client.
5. Shutdown logger and exit.

---
# Configuration Management (`dbconfig_azure_event_hub.py`)

The script `scripts/dbconfig_azure_event_hub.py` manages the MongoDB document containing Event Hub connection entries.

Supported actions:
* `add` – Interactively prompts user for `connection_string`, `event_hub_name`, `consumer_group` (defaults to `$Default`) and inserts (avoids duplicates).
* `delete` – Prompts for same triplet and removes if present.
* `check` – Lists all stored configurations.

Example (Linux / WSL / PowerShell):
```bash
python scripts/dbconfig_azure_event_hub.py --action add
```

Data schema per config:
```json
{
	"connection_string": "Endpoint=sb://<ns>.servicebus.windows.net/...;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=<event_hub_name>",
	"event_hub_name": "<event_hub_name>",
	"consumer_group": "$Default"
}
```

Operational notes:
* After modifying configs, restart the listener process so new clients initialize.
* Connection strings should be SAS policy scoped to least privileges (listen only).

# SSH Forwarder Integration

The Azure Event Hub listener can accept forwarded logs from remote forwarder instances over SSH connections. When using the companion forwarder (`azure_event_hub_forwarder`), the following SSH configuration is required:

**Connection Details:**
* SSH Port: `441`
* Username: `remote_cg_agent`
* Target Port: `1023` (localhost forwarding, handled by `azure_event_hub_forwarder`)

**Required SSH Server Configuration (`sshd_config`):**
```bash
Match User remote_cg_agent
   AllowTcpForwarding yes
   X11Forwarding no
   PermitTunnel no
   GatewayPorts no
   AllowAgentForwarding no
   PermitOpen localhost:1010 localhost:1011 localhost:1013 localhost:1018 localhost:1019 localhost:1022 localhost:1023
   ForceCommand echo 'This account can only be used for comms'
```

The `PermitOpen localhost:1023` directive is critical—it allows the forwarder to establish SSH channels that can send log data to the local listener on port 1023. Without this configuration, SSH connections from forwarder instances will be rejected or unable to establish the required data channel.

---
# Runtime Parameters & Constants

| Constant | Script | Purpose | Default |
|----------|--------|---------|---------|
| `BUFFER_SIZE` | listener | Max queued logs awaiting publish | `100000` |
| `BUFFER_CHECK_INTERVAL` | listener | Sleep (s) while buffer full | `5` |
| `THREAD_CHECK_INTERVAL` | listener & forwarder | Thread health interval | `300` |
| `PIKA_EXCHANGE_OUT` | listener | RabbitMQ topic exchange name | `received_sensorless_log` |
| `PIKA_EXCHANGE_IN` | sensorless consumer | Input exchange | `received_sensorless_log` |
| `PIKA_QUEUE_IN` | sensorless consumer | Queue binding to exchange | `listen_sensorless_log` |
| `RABBIT_MQ_PREFETCH_COUNT` | sensorless consumer | Fair dispatch window | `100` |
| `MSG_TTL_MS` | sensorless consumer | Queue message TTL | `600000` (10m) |

---
# Routing Key

Routing key logic (from `get_routing_key()`):
* Likely parses `resource_id` patterns to derive hierarchical routing keys (e.g., `event_hub.azure_sql.db.raw`). Logs without a determinable resource may use a fallback key such as `event_hub.unknown.unknown.raw`.

---
# Operational Runbook

| Task | Command / Action |
|------|------------------|
| List configs | `python scripts/dbconfig_azure_event_hub.py --action check` |
| Add config | `python scripts/dbconfig_azure_event_hub.py --action add` (interactive) |
| Delete config | `python scripts/dbconfig_azure_event_hub.py --action delete` (interactive) |
| Verify listener process | `ps aux | grep listen_azure_event_hub` |
| Tail logs | `tail -f log/listen_azure_event_hub-InsiderSecurity.log` (filename depends on hostname) |

---
# Quick Reference

```bash
# Check configs
python scripts/dbconfig_azure_event_hub.py --action check

# Add new Event Hub
python scripts/dbconfig_azure_event_hub.py --action add

# Start (dev)
algo.rb start core listen_azure_event_hub.py

# Restart (dev)
algo.rb restart core listen_azure_event_hub.py
```

---
# Appendix

* **Event Hub Client** – An `EventHubConsumerClient` tied to a specific hub + consumer group.
* **Consumer Group** – Independent position/state view over partitions; multiple groups permit parallel pipelines.
* **Routing Key** – Topic key used within RabbitMQ for selective subscription.
* **Sensorless Log** – Raw/ingested log prior to sensor/agent attribution & enrichment (handled by `listen_sensorless_log.py`).
