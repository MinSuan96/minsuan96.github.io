---
Title: Azure Event Hub Forwarder (azure_event_hub_forwarder.py)
author: InsiderSecurity
date: 19 September 2025
---

# Table of Contents

- [Table of Contents](#table-of-contents)
- [Executive Summary](#executive-summary)
- [Architecture](#architecture)
- [Data Flow](#data-flow)
- [Configuration](#configuration)
  - [1. File Layout (`config.json`)](#1-file-layout-configjson)
  - [2. Required Parameters (Summary)](#2-required-parameters-summary)
  - [3. Network Prerequisites](#3-network-prerequisites)
- [Authentication](#authentication)
  - [1. CLI Identity Login](#1-cli-identity-login)
  - [2. Verification](#2-verification)
  - [3. Role Requirements](#3-role-requirements)
- [Deployment (Windows Service)](#deployment-windows-service)
  - [Prerequisites](#prerequisites)
  - [Service Installation](#service-installation)
    - [Install the Service](#install-the-service)
    - [Start the Service](#start-the-service)
    - [Stop the Service](#stop-the-service)
    - [Remove/Uninstall the Service](#removeuninstall-the-service)
  - [Service Management Commands](#service-management-commands)
  - [Troubleshooting](#troubleshooting)
    - [View Service Logs](#view-service-logs)
    - [Debug Mode](#debug-mode)
    - [Common Issues](#common-issues)
      - [Issue: "Access Denied" when installing](#issue-access-denied-when-installing)
      - [Issue: Service fails to start](#issue-service-fails-to-start)
      - [Issue: Service starts but doesn't work](#issue-service-starts-but-doesnt-work)
  - [Service Configuration](#service-configuration)
  - [Notes](#notes)

---

# Executive Summary

The Azure Event Hub Forwarder runs on an Azure Windows VM, consumes events from one or more Azure Event Hubs, and forwards them over an SSH channel to an external analytics platform outside Azure. It is designed for customers who cannot (or prefer not to) directly expose internal analytics ingestion endpoints to Azure services and instead use an intermediate controlled VM.

Core qualities:

- Pluggable: Supports multiple Event Hub sources (one thread per hub).
- Secure Transport: Uses SSH (private key authentication via Azure Key Vault) for outbound delivery.
- Resilient: Exponential backoff retry logic for SSH connections and log transmission; automatic thread restart on failure.
- Windows Service: Can run as a Windows service with auto-start on boot and service recovery options.
- Extensible: Future metrics, batching, checkpointing, and alternative transports.

---

# Architecture

| Component | Purpose |
|-----------|---------|
| `azure_event_hub_forwarder.py` | Main forwarder script (thread orchestration, ingestion, forwarding). |
| EventHubConsumerClient (per hub) | Receives events from configured Event Hubs. |
| SSH Transport (Paramiko) | Persistent channel to external analytics server. |
| Azure Key Vault | Secure storage for SSH private key. |
| Configuration File (`config.json`) | Declarative source for hub + SSH parameters. |
| Windows Service Wrapper | Ensures auto‑start and resilience on reboot. |

Threads:

- 1 main control thread (startup, health supervision, thread monitoring).
- N receiver threads (one per event hub configuration).

Graceful shutdown closes all Event Hub clients then tears down SSH transport. The service monitors thread health and automatically restarts failed threads. If Event Hub receiver threads exhaust all retry attempts, the service initiates a graceful shutdown.

---

# Data Flow

```flow
Azure Event Hub(s) --> EventHubConsumerClient (thread) --> process_event_data --> send_log_via_ssh --> Remote Analytics Server
```

Processing Steps:

1. Receive raw event (body bytes) from partition.
2. Decode (UTF‑8 / JSON).
3. Serialize outbound payload as JSON (newline‑delimited for streaming).
4. Transmit over persistent SSH channel.

Failure Handling: Log & retry with exponential backoff (bounded to MAX_RETRIES = 5).

Retry Strategy:

- SSH Connection: Exponential backoff with retry attempts (wait time: min(2^retry_count, 60) seconds, capped at 60 seconds)
- SSH Log Sending: Exponential backoff with retry attempts (wait time: min(2^retry_count, 30) seconds, capped at 30 seconds)
- Event Hub Receive Loop: Fixed 60-second intervals between retry attempts
- Service Exit: When Event Hub receiver threads exhaust all retries, the service signals for graceful shutdown


---

# Configuration

## 1. File Layout (`config.json`)

```json
{
   "event_hub_configs": [
      {
         "event_hub_namespace": "<event_hub_namespace>",
         "event_hub_name": "<event_hub_name>",
         "consumer_group": "<consumer_group>"
      }
   ],
   "ssh_config": {
      "hostname": "<hostname>",
      "port": 441,
      "username": "remote_cg_agent",
      "vault_url": "<vault_url>",
      "secret_name": "<secret_name>",
      "timeout": 30
   }
}
```

Guidelines:

- Add additional Event Hubs by appending objects to `event_hub_configs`.
- Store private keys in Azure Key Vault with appropriate access policies.
- Keep `config.json` in the same directory as the script (or pass full path of the file).
- Store the SSH private key as a secret in Azure Key Vault.
- Grant `Key Vault Secrets User` role to the managed identity running the service.

## 2. Required Parameters (Summary)

| Parameter | Description |
|-----------|-------------|
| Event Hub Namespace | Parent namespace of the hub. The format is: `<yournamespace>.servicebus.windows.net.` |
| Event Hub Name | Specific hub instance to consume. |
| Consumer Group | Independent offset view; use dedicated group for isolation. |
| SSH Hostname / Port | Destination analytics endpoint. |
| SSH Username | Remote account for log ingestion process. |
| Vault URL | Azure Key Vault URL where the SSH private key is stored (format: `https://<keyvault-name>.vault.azure.net/`). |
| Secret Name | Name of the secret in Azure Key Vault containing the SSH private key. |
| Timeout | SSH connection timeout (seconds). |

## 3. Network Prerequisites

| Direction | Purpose | Port(s) | Rule |
|-----------|---------|---------| --------- |
| Azure Event Hubs -> VM | Event ingestion | 443 (HTTPS) | Outbound and Inbound |
| VM -> Analytics Server | Log forwarding | 441 (SSH) | Outbound only |

Ensure the firewall permits the necessary traffic. Ensure that `listen_azure_event_hub.py` is running on the analytic server.

---

# Authentication

The forwarder must authenticate to Azure to read from Event Hubs.

## 1. CLI Identity Login

```powershell
az login --identity --client-id <client_id>
az login --identity --object-id <object_id>
az login --identity --resource-id <resource_id>
```

## 2. Verification

```powershell
az account show -o table
```

## 3. Role Requirements

| Purpose | Minimum Role | Scope |
|---------|--------------|-------|
| Consume events | Azure Event Hubs Data Receiver | Hub or Namespace |
| Access SSH private key | Key Vault Secrets User | Key Vault or specific secret |

> IMPORTANT: Without a valid Azure identity and proper role assignments, the forwarder cannot ingest events or access the SSH private key.

---

# Deployment (Windows Service)

## Prerequisites

1. Install Python 3.x on your Windows system
2. Install required dependencies:

   ```powershell
   pip install -r requirements3.txt
   ```

3. Make sure that Azure CLI is located on PATH.

## Service Installation

### Install the Service

Run the following command with administrator privileges:

```powershell
python azure_event_hub_forwarder.py install
```

### Start the Service

```powershell
python azure_event_hub_forwarder.py start
```

Or use Windows Services Manager:

- Press `Win + R`, type `services.msc`, and press Enter
- Find "Azure Event Hub Forwarder Service"
- Right-click and select "Start"

### Stop the Service

```powershell
python azure_event_hub_forwarder.py stop
```

Or use Windows Services Manager to stop the service.

### Remove/Uninstall the Service

```powershell
python azure_event_hub_forwarder.py remove
```

## Service Management Commands

| Command | Description |
|---------|-------------|
| `python azure_event_hub_forwarder.py install` | Install the service |
| `python azure_event_hub_forwarder.py start` | Start the service |
| `python azure_event_hub_forwarder.py stop` | Stop the service |
| `python azure_event_hub_forwarder.py restart` | Restart the service |
| `python azure_event_hub_forwarder.py remove` | Uninstall the service |
| `python azure_event_hub_forwarder.py debug` | Run in debug mode (console) |

## Troubleshooting

### View Service Logs

The service logs to:

1. `azure_event_hub_forwarder.log` in the script directory
2. Windows Event Viewer (Application logs)

To view the log file:

```powershell
Get-Content azure_event_hub_forwarder.log -Tail 50
```

To view Windows Event Logs:

- Press `Win + R`, type `eventvwr.msc`, and press Enter
- Navigate to Windows Logs → Application
- Look for events from "Azure Event Hub Forwarder"

### Debug Mode

Run the service in debug mode to see real-time output:

```powershell
python azure_event_hub_forwarder.py debug
```

This runs the service in the foreground with console output.

### Common Issues

#### Issue: "Access Denied" when installing

- Solution: Run PowerShell or Command Prompt as Administrator

#### Issue: Service fails to start

- Check the log file `azure_event_hub_forwarder.log`
- Ensure `config.json` is properly configured
- Verify all dependencies are installed
- Check Windows Event Viewer for error details

#### Issue: Service starts but doesn't work

- Run in debug mode to see real-time errors
- Verify Azure Event Hub configuration and network connectivity
- Check SSH connectivity to the remote server (ensure port 441 is accessible)
- Ensure Azure CLI authentication is configured (`az login --identity`)
- Verify the managed identity has proper role assignments:
  - `Azure Event Hubs Data Receiver` on Event Hub namespace
  - `Key Vault Secrets User` on Key Vault
- Check DNS resolution for Event Hub namespace (common error: `[Errno 11001] getaddrinfo failed`)
- Review firewall rules for outbound connectivity to Event Hub (port 443) and SSH server (port 441)

## Service Configuration

The service uses the same `config.json` file as the standalone script. Ensure it's properly configured before starting the service.

## Notes

- The service runs under the Local System account by default
- Ensure the account has necessary permissions to access:
  - Azure Event Hub (via managed identity with proper role assignment)
  - Azure Key Vault (to retrieve SSH private key)
  - Log file directory (write permissions)
- The service implements exponential backoff retry for SSH connections and log transmission
- Event Hub receiver threads retry with 60-second fixed intervals (MAX_RETRIES = 5)
- When all retry attempts are exhausted for Event Hub connections, the service initiates graceful shutdown
- Thread health monitoring automatically restarts failed threads
- Consider configuring service recovery options to automatically restart the service after failures
- Consider using a dedicated service account with minimal required permissions for production deployments
