---
Title: Handover - Minsuan
author: Teh Min Suan
date: 06 April 2026
---

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Handover Table](#handover-table)
- [1. Features](#1-features)
  - [1.1 BNWEngine Optimization](#11-bnwengine-optimization)
  - [1.2 Azure Event Hub Integration](#12-azure-event-hub-integration)
  - [1.3 External Forwarder to HTSOC](#13-external-forwarder-to-htsoc)
  - [1.4 MariaDB Support](#14-mariadb-support)
  - [1.5 Self Service File Monitoring](#15-self-service-file-monitoring)
  - [1.6 Sensor Log Rotation](#16-sensor-log-rotation)
  - [1.7 Windows Credential Manager](#17-windows-credential-manager)
  - [1.8 XML Forwarding](#18-xml-forwarding)
  - [1.9 Azure Blob Storage / Agentless Puller](#19-azure-blob-storage--agentless-puller)
  - [1.10 Storage Monitoring \& Alerting](#110-storage-monitoring--alerting)
  - [1.11 User \& Entities Management](#111-user--entities-management)
  - [1.12 Log Activity Monitoring](#112-log-activity-monitoring)
  - [1.13 Timezone-Aware Logging](#113-timezone-aware-logging)
  - [1.14 DB Row Access Anomaly Detection](#114-db-row-access-anomaly-detection)
  - [1.15 Sensorless Log / Server Entity](#115-sensorless-log--server-entity)
  - [1.16 DAM Support for RDS MySQL CE](#116-dam-support-for-rds-mysql-ce)
  - [1.17 Sensor Auto Role](#117-sensor-auto-role)
  - [1.18 Minor Features](#118-minor-features)
- [2. Bug Fixes](#2-bug-fixes)
- [3. Others](#3-others)
  - [3.1 casw → casw-kube Update](#31-casw--casw-kube-update)
    - [Sections Covered](#sections-covered)
    - [Established Merge Rules](#established-merge-rules)
    - [Pre-existing Issues (Deferred)](#pre-existing-issues-deferred)
    - [Pull Requests](#pull-requests)
  - [3.2 Minor Changes](#32-minor-changes)
  - [3.3 Reference Documentation](#33-reference-documentation)
  - [3.4 System Configuration Guides](#34-system-configuration-guides)
    - [MySQL (On-Premises)](#mysql-on-premises)
    - [PostgreSQL](#postgresql)
    - [OracleDB](#oracledb)
  - [3.5 Other Documents](#35-other-documents)

---

## Handover Table

| Section | Jason | Kevin | Shiu | Bel | Kah Yoong | YJ |
|---|---|---|---|---|---|---|
| 1.1 BNWEngine Optimization | | | X | X | X | X |
| 1.2 Azure Event Hub Integration | | X | | X | X | X |
| 1.3 External Forwarder to HTSOC | X | X | X | | X | X |
| 1.4 MariaDB Support | | X | | X | X | X |
| 1.5 Self Service File Monitoring | X | | X | X | | X |
| 1.6 Sensor Log Rotation | X | | X | X | X | X |
| 1.7 Windows Credential Manager | X | | X | X | X | X |
| 1.8 XML Forwarding | X | | X | | X | X |
| 1.9 Azure Blob Storage / Agentless Puller | | X | | X | X | X |
| 1.10 Storage Monitoring & Alerting | X | X | X | X | | X |
| 1.11 User & Entities Management | X | X | X | X | | X |
| 1.12 Log Activity Monitoring | X | X | X | X | | X |
| 1.13 Timezone-Aware Logging | X | | | X | X | X |
| 1.14 DB Row Access Anomaly Detection | X | | X | X | X | X |
| 1.15 Sensorless Log / Server Entity | | X | | X | X | X |
| 1.16 DAM Support for RDS MySQL CE | | X | | X | X | X |
| 1.17 Sensor Auto Role | | X | X | X | X | X |
| 1.18 Minor Features | X | X | X | X | X | X |
| 2. Bug Fixes | X | X | X | X | X | X |
| 3.1 casw→casw-kube Update | | X | X | X | X | |
| 3.2 Minor Changes | X | X | X | X | X | X |
| 3.3 Reference Documentation | X | X | | X | X | X |
| 3.4 System Configuration Guides | X | X | | X | X | X |
| 3.5 Other Documents | X | X | X | | X | X |

---

## 1. Features

### 1.1 BNWEngine Optimization

**Documentation:** `Handover - Minsuan/BNWEngine/`

| Item | File | Description |
|---|---|---|
| Version Difference Reference | `BNWEngine_Version_Difference.pdf` | PDF documenting the differences between BNWEngine versions. |
| Performance Analysis Notebook | `BNWEngineV4.ipynb` | Jupyter notebook benchmarking BNWEngineV4 against BNWEngineV2. Shows execution time vs. number of worker processes (1–8). BNWEngineV4 scales from ~7.2 s (1 worker) to ~3.9 s (8 workers), versus a flat ~14.6 s for V2 — roughly 50–80% faster depending on worker count. |
| Supporting Diagrams | `cache.png`, `codeLogic.png`, `final.png`, `workerProcesses.png` | Images used in the notebook and version difference document illustrating caching behaviour, code logic flow, and worker-process scaling. |

Rewrote and optimized the BNWEngine from V2 to V4. V4 uses multiprocessing workers and is 50–80% faster than V2. Also made Pika connections thread-safe.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2180](https://bitbucket.org/ins17/casw/pull-requests/2180) | casw | Feature/BNWEngine optimization | MERGED | 2024-10-14 | — |
| [#2294](https://bitbucket.org/ins17/casw/pull-requests/2294) | casw | Feature/thread safe pika in BNWEngineV4 | MERGED | 2025-10-22 | — |
| [#2247](https://bitbucket.org/ins17/casw/pull-requests/2247) | casw | Feature/UEBA-853 differentiating entities with the same name | DRAFT | 2025-08-11 | [UEBA-853](https://insidersecurity.atlassian.net/browse/UEBA-853) limitation of risk calculation for "root" or "system" account |

---

### 1.2 Azure Event Hub Integration

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Azure Event Hub Forwarder | `azure_event_hub_forwarder.md` | Forwarder running on an Azure Windows VM that consumes from one or more Azure Event Hubs and forwards logs over SSH to the analytics platform. Covers architecture, `config.json` layout, Azure managed identity auth, and Windows Service installation. |
| Azure Event Hub Listener | `listen_azure_event_hub.md` | Server-side listener (`listen_azure_event_hub.py`) that ingests from Azure Event Hubs and republishes payloads into RabbitMQ (`received_sensorless_log` exchange). Includes configuration management via `dbconfig_azure_event_hub.py` and operational runbook. |

**System Configuration Guides:** `Handover - Minsuan/System Configuration Guide/`

Covers both UEBA-1025 (Event Hub ingestion) and UEBA-835 (Log Analytics Workspace reader).

| Document | File(s) | Description |
|---|---|---|
| Azure SQL — Azure Portal Setup | `DB - Monitor Azure SQL Configuration (Azure Portal).md/.pdf` | Configures Azure SQL audit log routing to Event Hub — either directly or via a Log Analytics Workspace intermediary. Covers Event Hub namespace/hub creation, shared access policies, and SQL Server auditing settings. |
| Azure SQL — Analytic Server Config | `DB - Monitor Azure SQL Configuration (Analytic Server).md/.pdf` | Configures `dbconfig_azure_event_hub.py` to store the Event Hub connection in MongoDB, starts/verifies `listen_azure_event_hub.py` and `listen_sensorless_log.py`, and includes a troubleshooting runbook. |
| Azure SQL — Combined Guide | `DB - Monitor Azure SQL Configuration (Combined).md/.pdf` | End-to-end guide combining the Azure Portal and Analytic Server steps for deployments where the monitoring system runs on AWS. |

Three-part feature: (1) a server-side reader that pulls Azure SQL logs from a Log Analytics Workspace; (2) a Windows-side forwarder agent that reads from Azure Event Hubs and pushes logs over SSH; (3) a server-side listener that ingests those logs into RabbitMQ. Supports Azure managed identity authentication.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2217](https://bitbucket.org/ins17/casw/pull-requests/2217) | casw | Feature/UEBA-835 azure log analytic reader | MERGED | 2025-05-09 | [UEBA-835](https://insidersecurity.atlassian.net/browse/UEBA-835) [NP] Differentiating Database names/log sources forwarded from LAW |
| [#2269](https://bitbucket.org/ins17/casw/pull-requests/2269) | casw | Feature/UEBA-1025 azure event hub reader with forwarder | MERGED | 2025-09-19 | [UEBA-1025](https://insidersecurity.atlassian.net/browse/UEBA-1025) [BCA] Log Forwarder from Azure Event Hub to IS Analytic Server |
| [#110](https://bitbucket.org/ins17/connectors/pull-requests/110) | connectors | Feature/UEBA-1025 azure event hub forwarder | MERGED | 2025-09-19 | [UEBA-1025](https://insidersecurity.atlassian.net/browse/UEBA-1025) [BCA] Log Forwarder from Azure Event Hub to IS Analytic Server |

---

### 1.3 External Forwarder to HTSOC

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| External Forwarder Developer Guide | `external_forwarder.md` | Developer guide for setting up log forwarding. Covers the `MatchedAgent` class, forwarder core functions, Redis metrics, UEBA alert forwarding, database configuration (interactive and batch modes), and how to extend the forwarder to support additional log types. |

Built and extended the `forwarder_to_HTSOC.py` framework supporting multiple log types (Windows, SSH, DNS, Netdev, PowerShell). Includes RFC 5424 syslog formatting, Redis metrics tracking, UEBA alert forwarding, and UDP large-message handling.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2252](https://bitbucket.org/ins17/casw/pull-requests/2252) | casw | Feature/forwarder_to_HTSOC | MERGED | 2025-08-18 | — |
| [#2271](https://bitbucket.org/ins17/casw/pull-requests/2271) | casw | Feature/UEBA-986 netdev forwarder to HTSOC | MERGED | 2025-09-19 | [UEBA-986](https://insidersecurity.atlassian.net/browse/UEBA-986) [SCDF] HTSOC forwarding of network device logs |
| [#2275](https://bitbucket.org/ins17/casw/pull-requests/2275) | casw | Feature/UEBA-1011 powershell event forwarder to HTSOC | MERGED | 2025-09-23 | [UEBA-1011](https://insidersecurity.atlassian.net/browse/UEBA-1011) [SCDF] Sensor to forward 4104 logs on powershell scripting |
| [#2277](https://bitbucket.org/ins17/casw/pull-requests/2277) | casw | feature/UEBA-1107-windows-forwarder-in-rfc5424 | MERGED | 2025-09-30 | [UEBA-1107](https://insidersecurity.atlassian.net/browse/UEBA-1107) [ICON2] HTSOC Forwarder to support standard RFC5424 format |
| [#2283](https://bitbucket.org/ins17/casw/pull-requests/2283) | casw | Feature/UEBA-921 ssh logs forwarder | MERGED | 2025-10-03 | [UEBA-921](https://insidersecurity.atlassian.net/browse/UEBA-921) [SCDF] HTSOC Linux log forwarder required |
| [#2301](https://bitbucket.org/ins17/casw/pull-requests/2301) | casw | Feature/UEBA-1074 dns forwarder | MERGED | 2025-10-28 | [UEBA-1074](https://insidersecurity.atlassian.net/browse/UEBA-1074) [SCDF] DNS traffic forwarder to HTSOC |
| [#2335](https://bitbucket.org/ins17/casw/pull-requests/2335) | casw | fix/UEBA-1252-forwarder-failed-due-to-large-message-over-udp | MERGED | 2025-11-26 | [UEBA-1252](https://insidersecurity.atlassian.net/browse/UEBA-1252) [SCDF] HTSOC forwarding - high-login-count DAM alerts fail to forward |
| [#2417](https://bitbucket.org/ins17/casw/pull-requests/2417) | casw | Feature/UEBA-1409 better filtering for HTSOC forwarder | MERGED | 2026-02-09 | [UEBA-1409](https://insidersecurity.atlassian.net/browse/UEBA-1409) [SCDF] HTSOC forwarding of DAM alerts includes missing sensor feed alert |
| [#2418](https://bitbucket.org/ins17/casw/pull-requests/2418) | casw | fix/UEBA-1409-ruby-code-in-html-when-forwarding | MERGED | 2026-02-09 | [UEBA-1409](https://insidersecurity.atlassian.net/browse/UEBA-1409) [SCDF] HTSOC forwarding of DAM alerts includes missing sensor feed alert |
| [#2428](https://bitbucket.org/ins17/casw/pull-requests/2428) | casw | feature/UEBA-1331-redis-metrics-in-HTSOC-forwarder | OPEN | 2026-02-23 | [UEBA-1331](https://insidersecurity.atlassian.net/browse/UEBA-1331) [SCDF] HTSOC forwarder redis metrics on count for logs per source |
| [#2454](https://bitbucket.org/ins17/casw/pull-requests/2454) | casw | Fix/UEBA-1416 error decoding non-utf8 characters | MERGED | 2026-03-11 | [UEBA-1416](https://insidersecurity.atlassian.net/browse/UEBA-1416) [SCDF] Powershell_events error decoding payload |

---

### 1.4 MariaDB Support

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| MariaDB Parser | `parser_mariadb.md` | Design for the MariaDB log parser. |

**System Configuration Guides:** `Handover - Minsuan/System Configuration Guide/`

| Document | File(s) | Description |
|---|---|---|
| MariaDB — Linux | `DB - Monitor MariaDB Configuration (Linux).docx/.pdf` | Enables MariaDB audit logging on Linux for InsiderSecurity monitoring. |
| MariaDB — Windows | `DB - Monitor MariaDB Configuration (Windows).docx/.pdf` | Enables MariaDB audit logging on Windows. |
| MariaDB Community Audit Plugin Reference | `MariaDB Community Audit Plugin.md/.pdf` | Comprehensive reference for the `server_audit` plugin: installation, configuration variables, log settings (CONNECT/QUERY/TABLE/DDL/DML event types), log format, log rotation, and system variables. |

Added MariaDB log ingestion: a new parser and ELK storage pipeline to collect and index MariaDB audit/general logs.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2392](https://bitbucket.org/ins17/casw/pull-requests/2392) | casw | Feature/UEBA-1366 storing mariadb logs in elk | MERGED | 2026-01-21 | [UEBA-1366](https://insidersecurity.atlassian.net/browse/UEBA-1366) Able to ingest MariaDB logs into Kibana |
| [#2462](https://bitbucket.org/ins17/casw/pull-requests/2462) | casw | Feature/UEBA-1332 mariadb support | MERGED | 2026-03-16 | [UEBA-1332](https://insidersecurity.atlassian.net/browse/UEBA-1332) DAM support for MariaDB |

---

### 1.5 Self Service File Monitoring

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Settings File Monitoring | `settings_file_monitoring.md` | Design for monitoring settings/configuration files for changes. |
| File Read Frequency Analysis | `file_read_frequency_analysis.md` | Design for analysing how frequently log files are being read. |

Allows customers to configure their own file monitoring targets through the UI, with backend support in the server, sensor (wildcard path support), and infrastructure deployment configuration. Also includes Windows file change detection (UEBA-914).

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2229](https://bitbucket.org/ins17/casw/pull-requests/2229) | casw | Feature/UEBA-933 self service file monitoring | MERGED | 2025-06-11 | [UEBA-933](https://insidersecurity.atlassian.net/browse/UEBA-933) self-service file monitoring |
| [#2264](https://bitbucket.org/ins17/casw/pull-requests/2264) | casw | Feature/UEBA-997 self service file monitoring 2 | MERGED | 2025-08-28 | [UEBA-997](https://insidersecurity.atlassian.net/browse/UEBA-997) self service file monitoring 2 |
| [#2292](https://bitbucket.org/ins17/casw/pull-requests/2292) | casw | Feature/UEBA-1131 self service file monitoring 3 | MERGED | 2025-10-17 | [UEBA-1131](https://insidersecurity.atlassian.net/browse/UEBA-1131) Load testing using traffic generator for self service file monitoring |
| [#2209](https://bitbucket.org/ins17/casw/pull-requests/2209) | casw | Feature/UEBA-914 windows file change detection | MERGED | 2025-04-15 | [UEBA-914](https://insidersecurity.atlassian.net/browse/UEBA-914) Windows file change detection |
| [#129](https://bitbucket.org/ins17/sensor/pull-requests/129) | sensor | Feature/UEBA-933 self service file monitoring | MERGED | 2025-06-11 | [UEBA-933](https://insidersecurity.atlassian.net/browse/UEBA-933) self-service file monitoring |
| [#138](https://bitbucket.org/ins17/sensor/pull-requests/138) | sensor | Feature/UEBA-997 self service file monitoring 2 | MERGED | 2025-08-28 | [UEBA-997](https://insidersecurity.atlassian.net/browse/UEBA-997) self service file monitoring 2 |
| [#47](https://bitbucket.org/ins17/infrastructure/pull-requests/47) | infrastructure | Feature/UEBA-933 self service file monitoring | MERGED | 2025-06-11 | [UEBA-933](https://insidersecurity.atlassian.net/browse/UEBA-933) self-service file monitoring |
| [#51](https://bitbucket.org/ins17/infrastructure/pull-requests/51) | infrastructure | Feature/UEBA-997 self service file monitoring 2 | MERGED | 2025-08-28 | [UEBA-997](https://insidersecurity.atlassian.net/browse/UEBA-997) self service file monitoring 2 |

---

### 1.6 Sensor Log Rotation

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Sensor Log Rotation | `sensor_log_rotation.md` | Design for the sensor log rotation mechanism. |

Added log rotation support to the sensor agent, including log creation when the file does not exist and CHANGELOG updates.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#132](https://bitbucket.org/ins17/sensor/pull-requests/132) | sensor | Feature/UEBA-988 sensor to support wildcard in agent config | MERGED | 2025-07-22 | [UEBA-988](https://insidersecurity.atlassian.net/browse/UEBA-988) [SCDF] Windows Postgresql log rotation not working |
| [#137](https://bitbucket.org/ins17/sensor/pull-requests/137) | sensor | Feature/UEBA-988 sensor to support log rotate | MERGED | 2025-08-21 | [UEBA-988](https://insidersecurity.atlassian.net/browse/UEBA-988) [SCDF] Windows Postgresql log rotation not working |
| [#143](https://bitbucket.org/ins17/sensor/pull-requests/143) | sensor | omitted one of the code review changes for PR of UEBA-988 | MERGED | 2025-10-03 | [UEBA-988](https://insidersecurity.atlassian.net/browse/UEBA-988) [SCDF] Windows Postgresql log rotation not working |
| [#148](https://bitbucket.org/ins17/sensor/pull-requests/148) | sensor | Fix/UEBA-1152 sensor log not created if not exists | MERGED | 2025-10-27 | [UEBA-1152](https://insidersecurity.atlassian.net/browse/UEBA-1152) Sensor log file not register before creation |
| [#154](https://bitbucket.org/ins17/sensor/pull-requests/154) | sensor | include log rotate | MERGED | 2025-12-29 | — |

---

### 1.7 Windows Credential Manager

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Windows Credential Manager | `windows_credential_manager.md` | Design and usage guide for Windows Credential Manager integration in the agent. |

Integrated Windows Credential Manager into the sensor agent to securely store and retrieve passphrases, removing the need for plaintext credentials in configuration files.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#150](https://bitbucket.org/ins17/sensor/pull-requests/150) | sensor | Feature/UEBA-1157 storing passphrase in windows credential manager | MERGED | 2025-12-03 | [UEBA-1157](https://insidersecurity.atlassian.net/browse/UEBA-1157) [AGI] Storage/encryption of sensor ssh private keys |
| [#55](https://bitbucket.org/ins17/infrastructure/pull-requests/55) | infrastructure | Feature/UEBA-1157 storing passphrase in windows credential manager | MERGED | 2025-12-03 | [UEBA-1157](https://insidersecurity.atlassian.net/browse/UEBA-1157) [AGI] Storage/encryption of sensor ssh private keys |

---

### 1.8 XML Forwarding

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| XML Forwarder | `xml_forwarder.md` | Design for the XML event log forwarder that consumes from RabbitMQ and forwards via TCP/UDP syslog. |

Added support for forwarding Windows Event Logs in XML format over TCP/UDP syslog. Covers server-side consumer and sensor-side collection of XML events.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2189](https://bitbucket.org/ins17/casw/pull-requests/2189) | casw | Feature/UEBA-737 xml forwarder | MERGED | 2024-12-18 | [UEBA-737](https://insidersecurity.atlassian.net/browse/UEBA-737) [MFA] Forwarding of Windows Event Viewer logs in XML format |
| [#125](https://bitbucket.org/ins17/sensor/pull-requests/125) | sensor | Feature/UEBA-737 windows logs in XML format | MERGED | 2024-12-18 | [UEBA-737](https://insidersecurity.atlassian.net/browse/UEBA-737) [MFA] Forwarding of Windows Event Viewer logs in XML format |
| [#46](https://bitbucket.org/ins17/infrastructure/pull-requests/46) | infrastructure | Feature/xml forwarding | MERGED | 2025-02-19 | — |

---

### 1.9 Azure Blob Storage / Agentless Puller

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Azure Blob Storage Listener | `listen_azure_blob_storage.md` | Design for the Azure Blob Storage ingestion listener. |

Agentless puller that fetches log files directly from Azure Blob Storage, with optional PGP decryption before ingestion.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2261](https://bitbucket.org/ins17/casw/pull-requests/2261) | casw | Feature/UEBA-1024 azure storage blob puller sftp | MERGED | 2025-08-26 | [UEBA-1024](https://insidersecurity.atlassian.net/browse/UEBA-1024) [ASTAR] Adding SFTP Support for Agentless Puller |
| [#2323](https://bitbucket.org/ins17/casw/pull-requests/2323) | casw | feature/UEBA-1171-Adding Decryption to the Agentless Puller | MERGED | 2025-11-17 | [UEBA-1171](https://insidersecurity.atlassian.net/browse/UEBA-1171) [ASTAR] Adding Decryption to the Agentless Puller |
| [#2429](https://bitbucket.org/ins17/casw/pull-requests/2429) | casw | fix/UEBA-1401 remove pgp extension after decryption | MERGED | 2026-02-23 | [UEBA-1401](https://insidersecurity.atlassian.net/browse/UEBA-1401) [ASTAR] SFTP production setup for A*ERP, TTIMS, EDMS |

---

### 1.10 Storage Monitoring & Alerting

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Storage Alert | `storage_alert.md` | Design for storage usage alerting. |
| Storage Estimator | `storage_estimator.md` | Design for estimating storage consumption. |

Predictive alerting on storage consumption and a storage metrics collection pipeline to surface disk usage trends and trigger alerts before capacity is reached.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2191](https://bitbucket.org/ins17/casw/pull-requests/2191) | casw | Feature/UEBA-818 storage metrics | MERGED | 2025-02-10 | [UEBA-818](https://insidersecurity.atlassian.net/browse/UEBA-818) [IDEMIA] accurate and visible estimation of hard disk resource required |
| [#2202](https://bitbucket.org/ins17/casw/pull-requests/2202) | casw | feature/UEBA-882-predictive-alert-on-storage | MERGED | 2025-03-27 | [UEBA-882](https://insidersecurity.atlassian.net/browse/UEBA-882) Predictive alerts on mongo dataset becoming too large |

---

### 1.11 User & Entities Management

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| User & Entities Management | `user_entities_management.md` | Design for user and entity management within the platform. |

A new management page in the UEBA web UI for listing, editing, and managing user entities, including a bulk CSV upload flow.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2397](https://bitbucket.org/ins17/casw/pull-requests/2397) | casw | feature/UEBA-1088-user-entities-management-page | MERGED | 2026-01-23 | [UEBA-1088](https://insidersecurity.atlassian.net/browse/UEBA-1088) [SCDF] Configuration of sub report groups by users instead of server entities |

---

### 1.12 Log Activity Monitoring

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Log Activity Monitor | `log_activity_monitor.md` | Design for monitoring log collection activity and detecting stalls or gaps. |

Detects drops in application log rates to surface stalls or gaps in log collection early.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2236](https://bitbucket.org/ins17/casw/pull-requests/2236) | casw | Feature/UEBA-946 detect drop in application logs | MERGED | 2025-07-18 | [UEBA-946](https://insidersecurity.atlassian.net/browse/UEBA-946) [BCA] detect drop in application logs |

---

### 1.13 Timezone-Aware Logging

Adds timezone context to log timestamps across the server, sensor, and infrastructure components so that log times are consistently interpretable regardless of deployment locale.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2416](https://bitbucket.org/ins17/casw/pull-requests/2416) | casw | Feature/UEBA-1368 timezone aware log | OPEN | 2026-02-06 | [UEBA-1368](https://insidersecurity.atlassian.net/browse/UEBA-1368) MSSQL Logs dropped due to timezone |
| [#156](https://bitbucket.org/ins17/sensor/pull-requests/156) | sensor | feature/UEBA-1368-timezone-aware-log | OPEN | 2026-02-06 | [UEBA-1368](https://insidersecurity.atlassian.net/browse/UEBA-1368) MSSQL Logs dropped due to timezone |
| [#57](https://bitbucket.org/ins17/infrastructure/pull-requests/57) | infrastructure | Feature/UEBA-1368 timezone aware log | OPEN | 2026-02-06 | [UEBA-1368](https://insidersecurity.atlassian.net/browse/UEBA-1368) MSSQL Logs dropped due to timezone |

---

### 1.14 DB Row Access Anomaly Detection

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| DB Row Access Processor | `db_rowaccess_processor.md` | Documents `db_rowaccess_processor.py` — the Python rewrite of the legacy Ruby implementation. Explains anomaly detection for SQL row-access patterns, the `DBRowAccessMonitor` class, historical backfill support, APScheduler-based scheduling, and the integration test. |

Python rewrite of the legacy Ruby `db_rowaccess_processor`, adding APScheduler-based scheduling, historical backfill support, and an integration test suite.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2251](https://bitbucket.org/ins17/casw/pull-requests/2251) | casw | [UEBA-763] Fix/UEBA-763 sql access anomaly graph | MERGED | 2025-08-15 | [UEBA-763](https://insidersecurity.atlassian.net/browse/UEBA-763) [MAH] Report Anomaly not showing details when clicked on the red dot |
| [#2290](https://bitbucket.org/ins17/casw/pull-requests/2290) | casw | Fix/UEBA-763 sql access anomaly graph | MERGED | 2025-10-14 | [UEBA-763](https://insidersecurity.atlassian.net/browse/UEBA-763) [MAH] Report Anomaly not showing details when clicked on the red dot |

---

### 1.15 Sensorless Log / Server Entity

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Sensorless Log Listener | `listen_sensorless_log.md` | Design for `listen_sensorless_log.py`, which consumes from the `received_sensorless_log` exchange and routes logs to downstream queues. |

Added a server entity type for sensorless log sources (v2), allowing logs delivered without a deployed sensor to be correlated with a server entity in the UEBA platform.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2219](https://bitbucket.org/ins17/casw/pull-requests/2219) | casw | Feature/UEBA-870 UEBA-930 server entity for sensorless log v2 | MERGED | 2025-05-14 | [UEBA-870](https://insidersecurity.atlassian.net/browse/UEBA-870) Entity mapping for logs that are not from sensors · [UEBA-930](https://insidersecurity.atlassian.net/browse/UEBA-930) sensor page to differentiate between actual agents and agentless log sources |

---

### 1.16 DAM Support for RDS MySQL CE

**System Configuration Guides:** `Handover - Minsuan/System Configuration Guide/`

| Document | File(s) | Description |
|---|---|---|
| AWS MySQL — AWS Console Setup | `DB - Monitor AWS MySQL Listener Configuration (AWS Console).md/.pdf` | Creates an RDS/Aurora MySQL parameter group with slow-query and error logging enabled, exports logs to CloudWatch, and sets up the required IAM `CloudWatchReadOnlyAccess` policy. |
| AWS MySQL — Analytic Server Config | `DB - Monitor AWS MySQL Listener Configuration (Analytic Server).md/.pdf` | Configures `config_aws_mysql.py` on the analytics server to read MySQL logs from CloudWatch via boto3, and ensures `listen_sensorless_log.py` is running to create agents. |
| MySQL (AWS) Without RDS Creation | `DB - Monitor MySQL Configuration (AWS) Without RDS Creation.docx/.pdf` | Configures AWS MySQL monitoring when the RDS instance already exists (no new instance creation). |
| MySQL (AWS) | `DB - Monitor MySQL Configuration (AWS).pdf` | General AWS MySQL configuration guide (PDF only). |

Added DAM support for RDS for MySQL Community Edition running on AWS, reading slow-query and error logs from CloudWatch via boto3.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2199](https://bitbucket.org/ins17/casw/pull-requests/2199) | casw | Feature/UEBA-884-aws-mysql-ce-support | MERGED | 2025-03-21 | [UEBA-884](https://insidersecurity.atlassian.net/browse/UEBA-884) DAM support for RDS for MySQL CE |

---

### 1.17 Sensor Auto Role

| Handover Person | Handover Status | Handover Signature |
|---|---|---|
| Jason | | |

**Documentation:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Sensor Auto Role | `sensor_auto_role.md` | Design for the background service that automatically assigns roles and tags to sensors by inspecting Redis routing keys and evaluating regex-based filter rules stored in MongoDB. |

Background service (`sensor_auto_role.py`) that automatically assigns roles and tags to sensors. Inspects Redis routing keys to classify each sensor's system type (Windows, Linux, SharePoint, or DB), then writes detected roles back to MongoDB. Tag assignment applies customer-defined regex filter rules on a 2-minute APScheduler interval.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2166](https://bitbucket.org/ins17/casw/pull-requests/2166) | casw | Feature/UEBA-703 sensor auto role | MERGED | 2024-08-13 | [UEBA-703](https://insidersecurity.atlassian.net/browse/UEBA-703) Auto sensor role and tag assignment |

---

### 1.18 Minor Features

Miscellaneous features, refactors, and platform improvements spanning UI enhancements, algorithm rewrites, and tooling additions. No dedicated design documentation exists for these items.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2226](https://bitbucket.org/ins17/casw/pull-requests/2226) | casw | Feature/UEBA-910 refactor dns tunnel | MERGED | 2025-06-06 | [UEBA-910](https://insidersecurity.atlassian.net/browse/UEBA-910) refactor DNS tunnel |
| [#2123](https://bitbucket.org/ins17/casw/pull-requests/2123) | casw | Feature/UEBA-429 hdpnp split subsystem populatio | MERGED | 2024-05-17 | [UEBA-429](https://insidersecurity.atlassian.net/browse/UEBA-429) [HDP][NP] Split subsystem population into separate processes |
| [#2156](https://bitbucket.org/ins17/casw/pull-requests/2156) | casw | Feature/rewrite app time access analysis to python | MERGED | 2024-07-26 | — |
| [#2171](https://bitbucket.org/ins17/casw/pull-requests/2171) | casw | Feature/UEBA-248-csv-upload-feature | MERGED | 2024-09-06 | [UEBA-248](https://insidersecurity.atlassian.net/browse/UEBA-248) [HTA] A csv upload feature to transfer comments from csv to saved report |
| [#2194](https://bitbucket.org/ins17/casw/pull-requests/2194) | casw | manual generation and downloads of snapshot to PDF | MERGED | 2025-02-19 | — |
| [#2203](https://bitbucket.org/ins17/casw/pull-requests/2203) | casw | manual generation and downloads of snapshot to CSV | MERGED | 2025-04-02 | — |
| [#2270](https://bitbucket.org/ins17/casw/pull-requests/2270) | casw | Feature/UEBA-1075 flag for not dropping old logs | MERGED | 2025-09-19 | [UEBA-1075](https://insidersecurity.atlassian.net/browse/UEBA-1075) [ASTAR] Support for old app logs for event archiver |
| [#2116](https://bitbucket.org/ins17/casw/pull-requests/2116) | casw | added script to download from gridfs bucket | MERGED | 2024-05-10 | — |
| [#2210](https://bitbucket.org/ins17/casw/pull-requests/2210) | casw | Feature/UEBA-887 LGIS VSST support for parser azure sql | MERGED | 2025-04-18 | [UEBA-887](https://insidersecurity.atlassian.net/browse/UEBA-887) [NP] Support for DB login logs from LAW |
| [#2330](https://bitbucket.org/ins17/casw/pull-requests/2330) | casw | feature/timeline-page-limit-per-page | MERGED | 2025-11-21 | — |
| [#2206](https://bitbucket.org/ins17/casw/pull-requests/2206) | casw | Removal of "Known Beacon Traffic" aka "Beacon_OK" | MERGED | 2025-04-07 | — |
| [#2378](https://bitbucket.org/ins17/casw/pull-requests/2378) | casw | UEBA-1348 changes of timeline page vue files requested from code review | MERGED | 2026-01-13 | [UEBA-1348](https://insidersecurity.atlassian.net/browse/UEBA-1348) [ICA-MMBS] db_dml_analysis constantly restarting + timeline page optimisation |
| [#2370](https://bitbucket.org/ins17/casw/pull-requests/2370) | casw | feature/UEBA-1092-remove-semaphore-queue | MERGED | 2026-01-05 | [UEBA-1092](https://insidersecurity.atlassian.net/browse/UEBA-1092) Reevaluation of semaphore queue in golden image |
| [#2331](https://bitbucket.org/ins17/casw/pull-requests/2331) | casw | Feature/management-report-fix-wrong-api-argument | MERGED | 2025-11-24 | — |
| [#112](https://bitbucket.org/ins17/connectors/pull-requests/112) | connectors | fix/UEBA-855-unsupported-ps1-commands-in-CLM | MERGED | 2025-10-29 | [UEBA-855](https://insidersecurity.atlassian.net/browse/UEBA-855) [CNB & SCDF] Customers' Windows DB2 server experience performance issues |
| [#14](https://bitbucket.org/ins17/ueba-tests/pull-requests/14) | ueba-tests | Rename log_generator to v1 and v2, add linux and sharepoint generator v1 | MERGED | 2025-10-15 | — |
| [#13](https://bitbucket.org/ins17/ueba-tests/pull-requests/13) | ueba-tests | Add first version of Kevin's log generator (no longer being supported) | MERGED | 2025-10-15 | — |

---

## 2. Bug Fixes

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2456](https://bitbucket.org/ins17/casw/pull-requests/2456) | casw | Fix/UEBA-938 new ruby version causing argument error | MERGED | 2026-03-11 | [UEBA-938](https://insidersecurity.atlassian.net/browse/UEBA-938) creation of golden image (Ubuntu) |
| [#2455](https://bitbucket.org/ins17/casw/pull-requests/2455) | casw | fix/UEBA-938 new ruby version no longer allow hash argument as keyword argument | MERGED | 2026-03-11 | [UEBA-938](https://insidersecurity.atlassian.net/browse/UEBA-938) creation of golden image (Ubuntu) |
| [#2432](https://bitbucket.org/ins17/casw/pull-requests/2432) | casw | fix/UEBA-1428-port-scan4-bug | MERGED | 2026-02-25 | [UEBA-1428](https://insidersecurity.atlassian.net/browse/UEBA-1428) port_scan4 bug after refactoring |
| [#2430](https://bitbucket.org/ins17/casw/pull-requests/2430) | casw | fix/UEBA-953-event-id-6416-missing-riskscore | MERGED | 2026-02-25 | [UEBA-953](https://insidersecurity.atlassian.net/browse/UEBA-953) Urgent bug for Windows event IDs that are not monitored |
| [#2426](https://bitbucket.org/ins17/casw/pull-requests/2426) | casw | fix/UEBA-1417-management-report-api-code-issue | MERGED | 2026-02-23 | [UEBA-1417](https://insidersecurity.atlassian.net/browse/UEBA-1417) Thrown JS error prevents generation of management report |
| [#2419](https://bitbucket.org/ins17/casw/pull-requests/2419) | casw | fix/UEBA-1411-double-counting-in-api-login | MERGED | 2026-02-09 | [UEBA-1411](https://insidersecurity.atlassian.net/browse/UEBA-1411) [ASTAR] Potential double counting in api |
| [#2412](https://bitbucket.org/ins17/casw/pull-requests/2412) | casw | fix/UEBA-1389 | MERGED | 2026-02-04 | [UEBA-1389](https://insidersecurity.atlassian.net/browse/UEBA-1389) [SGI] Unable to receive any email alerts/notifications |
| [#2396](https://bitbucket.org/ins17/casw/pull-requests/2396) | casw | fix/UEBA-1328: 'none' as argument is no longer supported in newer version | MERGED | 2026-01-23 | [UEBA-1328](https://insidersecurity.atlassian.net/browse/UEBA-1328) [SP] SMTP conflict with updated Ruby version |
| [#2375](https://bitbucket.org/ins17/casw/pull-requests/2375) | casw | fix/UEBA-1334-UEBA-989-missing-logs-on-elk | MERGED | 2026-01-12 | [UEBA-1334](https://insidersecurity.atlassian.net/browse/UEBA-1334) [SP] "Hidden" alerts in dashboard · [UEBA-989](https://insidersecurity.atlassian.net/browse/UEBA-989) [STLOG] MSSQL not parsing logs correctly, leading to missing logs on ELK |
| [#2348](https://bitbucket.org/ins17/casw/pull-requests/2348) | casw | Fix/UEBA-1158-missing-alert-to-servicenow | MERGED | 2025-12-05 | [UEBA-1158](https://insidersecurity.atlassian.net/browse/UEBA-1158) [STLOG] Lack of forwarding of specific alert to servicenow |
| [#2339](https://bitbucket.org/ins17/casw/pull-requests/2339) | casw | fix/UEBA-1233-db-dml-analysis-crashing | MERGED | 2025-11-28 | [UEBA-1233](https://insidersecurity.atlassian.net/browse/UEBA-1233) [Sup Court] Data-first-access error |
| [#2322](https://bitbucket.org/ins17/casw/pull-requests/2322) | casw | fix/test-unit-6.3.x | MERGED | 2025-11-14 | — |
| [#2319](https://bitbucket.org/ins17/casw/pull-requests/2319) | casw | fix/sharepoint-parser-typo-fix | MERGED | 2025-11-13 | — |
| [#2316](https://bitbucket.org/ins17/casw/pull-requests/2316) | casw | fix/UEBA-1093-alertmanager-failed-to-find-ip | MERGED | 2025-11-10 | [UEBA-1093](https://insidersecurity.atlassian.net/browse/UEBA-1093) [NIE] Alertmanager restarting |
| [#2305](https://bitbucket.org/ins17/casw/pull-requests/2305) | casw | fix/UEBA-1148-sharepoint-parser-bug-fix | MERGED | 2025-11-03 | [UEBA-1148](https://insidersecurity.atlassian.net/browse/UEBA-1148) [NP] Sharepoint app privileged activity not triggering alerts |
| [#2291](https://bitbucket.org/ins17/casw/pull-requests/2291) | casw | Fix/UEBA-1035 fix pyDGAdetect bug | MERGED | 2025-10-14 | [UEBA-1035](https://insidersecurity.atlassian.net/browse/UEBA-1035) [ISEAS] SNOWTICKET alert link does not correctly reflect the IS alerts on timeline |
| [#2289](https://bitbucket.org/ins17/casw/pull-requests/2289) | casw | fix/UEBA-1126-wrong-scope-for-log | MERGED | 2025-10-09 | [UEBA-1126](https://insidersecurity.atlassian.net/browse/UEBA-1126) [SGI] listen_container_apache_logs.rb restarting due to NameError |
| [#2288](https://bitbucket.org/ins17/casw/pull-requests/2288) | casw | file is not defnied | MERGED | 2025-10-08 | — |
| [#2285](https://bitbucket.org/ins17/casw/pull-requests/2285) | casw | fix/UEBA-1069 High Risk Entities not appearing in First saved report | MERGED | 2025-10-06 | [UEBA-1069](https://insidersecurity.atlassian.net/browse/UEBA-1069) [ASTAR] High Risk Entities not appearing in First saved report |
| [#2244](https://bitbucket.org/ins17/casw/pull-requests/2244) | casw | UEBA-989-missing-logs-on-elk | MERGED | 2025-08-04 | [UEBA-989](https://insidersecurity.atlassian.net/browse/UEBA-989) [STLOG] MSSQL not parsing logs correctly, leading to missing logs on ELK |
| [#2239](https://bitbucket.org/ins17/casw/pull-requests/2239) | casw | fix/UEBA-1009-mongo-key-field-does-not-support-$ | MERGED | 2025-07-24 | [UEBA-1009](https://insidersecurity.atlassian.net/browse/UEBA-1009) entity starting with '$' character causing error for report snapshot |
| [#2238](https://bitbucket.org/ins17/casw/pull-requests/2238) | casw | fix/UEBA-991-python-is-not-syntax-error | MERGED | 2025-07-21 | [UEBA-991](https://insidersecurity.atlassian.net/browse/UEBA-991) parser_oracle_uni.py syntax warnings during boot up |
| [#2234](https://bitbucket.org/ins17/casw/pull-requests/2234) | casw | Fix/UEBA-972 timeline filtering pagination issue | MERGED | 2025-07-09 | [UEBA-972](https://insidersecurity.atlassian.net/browse/UEBA-972) [CNB] Filtered alerts not showing up on first page of paginated timeline |
| [#2225](https://bitbucket.org/ins17/casw/pull-requests/2225) | casw | Fix/UEBA-940 incorrect num days for report | MERGED | 2025-06-06 | [UEBA-940](https://insidersecurity.atlassian.net/browse/UEBA-940) [BCA] Failed Login graph in saved reports is empty |
| [#2221](https://bitbucket.org/ins17/casw/pull-requests/2221) | casw | fix/UEBA-928-suspicious-dns-traffic-timeline-issue | MERGED | 2025-05-16 | [UEBA-928](https://insidersecurity.atlassian.net/browse/UEBA-928) [ISEAS] Suspicious Dns Traffic alert missing timeline activity |
| [#2207](https://bitbucket.org/ins17/casw/pull-requests/2207) | casw | Fix/UEBA-895 dns tunnel timeline issue | MERGED | 2025-04-09 | [UEBA-895](https://insidersecurity.atlassian.net/browse/UEBA-895) [ISEAS] DNS Tunnel alerts not having any timeline activity |
| [#2204](https://bitbucket.org/ins17/casw/pull-requests/2204) | casw | UEBA-902-logs-filling-up-storage | MERGED | 2025-04-02 | [UEBA-902](https://insidersecurity.atlassian.net/browse/UEBA-902) [SCDF] System went down due to nohup logs filling up /home partition |
| [#2198](https://bitbucket.org/ins17/casw/pull-requests/2198) | casw | Fix/UEBA-857-duplicate-account-first-login | MERGED | 2025-03-21 | [UEBA-857](https://insidersecurity.atlassian.net/browse/UEBA-857) [Phillip Securities] Account First Login Alert Appearing Multiple Times |
| [#2192](https://bitbucket.org/ins17/casw/pull-requests/2192) | casw | UEBA-760-fix-invalid-ascii-characters | MERGED | 2025-02-10 | [UEBA-760](https://insidersecurity.atlassian.net/browse/UEBA-760) [ASTAR] non ASCII username bug in BNWengineV2 |
| [#2167](https://bitbucket.org/ins17/casw/pull-requests/2167) | casw | Fix/UEBA-179-incorrect-last-active-date | MERGED | 2024-08-14 | [UEBA-179](https://insidersecurity.atlassian.net/browse/UEBA-179) Sensor page last active date incorrectly mapped |
| [#2162](https://bitbucket.org/ins17/casw/pull-requests/2162) | casw | fix/UEBA-695-sharepoint-data-access-not-granular | MERGED | 2024-08-02 | [UEBA-695](https://insidersecurity.atlassian.net/browse/UEBA-695) [CPIB] Data access to site for Sharepoint not granular |
| [#2161](https://bitbucket.org/ins17/casw/pull-requests/2161) | casw | Fix/UEBA-441 sharepoint unusual time access not triggering | MERGED | 2024-07-31 | [UEBA-441](https://insidersecurity.atlassian.net/browse/UEBA-441) [CPIB] Sharepoint alerts for unusual time/access does not update dst_ip/dst_role |
| [#2160](https://bitbucket.org/ins17/casw/pull-requests/2160) | casw | Fix/UEBA-378 sensor down after 40 mins inactive of server and sensor | MERGED | 2024-07-31 | [UEBA-378](https://insidersecurity.atlassian.net/browse/UEBA-378) [CPIB] sensor down alert not sent for sensor >30mins down after server reboot |
| [#2155](https://bitbucket.org/ins17/casw/pull-requests/2155) | casw | Fix/Crashing of PyBeacon due to old library and heartbeat issue | MERGED | 2024-07-26 | — |
| [#2141](https://bitbucket.org/ins17/casw/pull-requests/2141) | casw | subsequent entity card cannot be loaded properly | MERGED | 2024-06-26 | — |
| [#2140](https://bitbucket.org/ins17/casw/pull-requests/2140) | casw | visuals_review_reports-crashing | MERGED | 2024-06-19 | — |
| [#2133](https://bitbucket.org/ins17/casw/pull-requests/2133) | casw | Fix/UEBA-286 pub saved report is blank white | MERGED | 2024-06-07 | [UEBA-286](https://insidersecurity.atlassian.net/browse/UEBA-286) [PUB] Saved report is blank white screen if tags no longer assigned to entities |
| [#127](https://bitbucket.org/ins17/sensor/pull-requests/127) | sensor | Fix/UEBA-865 ignore sensor log | MERGED | 2025-02-24 | [UEBA-865](https://insidersecurity.atlassian.net/browse/UEBA-865) sensor improvement to ignore its own log files |
| [#128](https://bitbucket.org/ins17/sensor/pull-requests/128) | sensor | bring missing changes from first merge | MERGED | 2025-05-28 | — |
| [#84](https://bitbucket.org/ins17/casw-kube/pull-requests/84) | casw-kube | Fix/UEBA-780 internal server error | MERGED | 2025-02-17 | [UEBA-780](https://insidersecurity.atlassian.net/browse/UEBA-780) [IDEMIA] internal server error |

---

## 3. Others

### 3.1 casw → casw-kube Update

**Documentation:** `Handover - Minsuan/Reports/casw-kube-merge-log.md` · `Handover - Minsuan/BNWEngine/BNWEngine_Version_Difference.pdf`

Full update of the on-premises `casw` codebase into `casw-kube` (Kubernetes). Covers shared libraries, core daemons, data forwarding, alerting, notifications, and algorithm modules.

#### Sections Covered

| Section | Branch | Scope | Key Outcomes |
|---|---|---|---|
| 1 — Shared Library | `merge/casw-shared-lib` | `casw/lib/` → `casw-kube/app/SHARED/libs/` | 16 new files added; 21 overwritten; 6 merged (casw logic + kube ENV paths); 4 kept as kube (K8s rewrites); ~68 identical. |
| 2a — Data Collection | `merge/casw-core-daemons` | `casw/core/` → `app/data_collection/` | 2 overwritten; 1 merged; 4 kept kube; 12 new feature files added (Azure Event Hub listener, sensorless log listener, Oracle Cloud integration). 4 new services need Dockerfile/build.sh/deploy/ stubs. |
| 2b — Data Forwarding | same branch | `casw/core/` → `app/data_forwarding/` | 1 overwritten; 2 identical; 2 new files (`forwarder_to_HTSOC.py`, `xml_forwarder.py`). |
| 2c — Alerting | same branch | `casw/core/` + `casw/algos/` → `app/alerting/` (+ notifications, web) | 54 files handled. `alerts_worker.rb` gained SNMP and HTSOC forwarding, non-ASCII patching. All 7 ERB templates updated across 3 locations. |
| 2d — Notifications | same branch | `casw/core/` → `app/notifications/` | `mail_worker.rb` overwritten (onprem env guard, proper OpenSSL constants, no-reply sender). |
| 2e — Excluded core/ files | — | `casw/core/` unmapped | 20 files deliberately excluded (stallers, workers, maintenance tooling). |
| 3a — Generic Processing | `merge/casw-algorithms` | `casw/algos/` → `app/data_processing/GENERIC/` | 49 files handled. Notable: `bypass_drop` feature in event_archiver, `role` tracking in app_time_access_analysis, `port_scan4` OOP refactor. |
| 3b — Domain Parsers | same branch | `casw/algos/` → `app/data_processing/<domain>/` | 19 files. SharePoint parser bug fixes (type guard, broken grok tag). |
| 3c-DB — Database | same branch | `casw/algos/db_*/` → `app/data_processing/database/` | 41 files. 6 new files (MongoDB Atlas puller/parser, Oracle RDS, listen_aws_mysql, MariaDB parser, Python db_rowaccess_processor). |
| 3c-Netflow | same branch | `casw/algos/` netflow dirs → `app/data_processing/netflow/` | 62 files. Major rewrites: port_scan4 OOP refactor, network_map METHOD 2. |
| 3c-Netdev | same branch | `casw/algos/netdev_monitoring/` → `app/data_processing/netdev/` | 17 files. 3 kube bug fixes preserved. |
| 3c-OS | same branch | `casw/algos/` OS dirs → `app/data_processing/os/` | Windows and Linux ERB templates updated; `win_login.py` merged. |

#### Established Merge Rules

These rules apply to all remaining merge sections:

1. **casw wins** by default when files differ (casw version overwrites kube), except for the cases below.
2. **Preserve ENV path references** — keep kube's `ENV['CG_HOME']`, `ENV['CG_DIR']`, `ENV['CG_CONFIG']`, `ENV['CG_LOG']` instead of casw's hardcoded `/home/bitnami/casw` paths.
3. **Keep K8s-rewritten files** — `env_helper.rb`, `py/env_helper.py`, and similar files substantially rewritten for containers must not be overwritten.
4. **Use `ENV_HELPER.redis_client`** — revert any `Redis.new` calls from casw back to kube's centralized client (SSL support).
5. **Strip hardcoded ENV assignments** — remove `ENV['CG_HOME'] = '/home/bitnami/casw'` lines from casw before applying to kube.
6. **Remove duplicate initializations** — e.g., duplicate `ENV_HELPER ||= EnvHelper.instance`.
7. **Skip `__pycache__/*.pyc`** — do not copy compiled bytecode.
8. **Leave kube-only files untouched** — files that exist only in casw-kube are not deleted.
9. **Keep watchdog threads commented out** — K8s liveness probes handle health checking externally.

#### Pre-existing Issues (Deferred)

The following were noted but not fixed during the merge:

- `forwarder_splunk.rb:181` — hardcoded `/home/bitnami/casw/log/` path (both repos).
- `forwarder_syslog_to_rabbit.py` — hardcoded paths and `redis.Redis()` instead of `ENV_HELPER` (both repos).
- `forwarder_to_GCSOC.py:20` — hardcoded `sys.path.append('/home/bitnami/casw/algos/win_dhcp')` (both repos).
- `archive_download.rb` — `DIR_UPLOADS` hardcoded path (both repos).
- `parser_cohesity.py` / `parser_ils.py` — raw `pika.BlockingConnection()` instead of `ENV_HELPER.rabbitmq_client()` (both repos).
- `sharepoint_user_processor.rb` — hardcoded `ENV["CG_DIR"]` paths (both repos).
- `poller_cohesity_log_analytics.py` — hardcoded MongoDB URL and bare Pika connection (both repos).
- `forwarder_to_HTSOC.py:810` — typo `'incldues'` preserved from casw source.

#### Pull Requests

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#141](https://bitbucket.org/ins17/casw-kube/pull-requests/141) | casw-kube | UEBA-1405 Merge/casw package requirements | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#140](https://bitbucket.org/ins17/casw-kube/pull-requests/140) | casw-kube | UEBA-1405 Merge/casw monit | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#139](https://bitbucket.org/ins17/casw-kube/pull-requests/139) | casw-kube | UEBA-1405 Merge/casw shared lib | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#138](https://bitbucket.org/ins17/casw-kube/pull-requests/138) | casw-kube | UEBA-1405 Merge/casw core daemons | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#137](https://bitbucket.org/ins17/casw-kube/pull-requests/137) | casw-kube | UEBA-1405 Merge/casw provisioning | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#136](https://bitbucket.org/ins17/casw-kube/pull-requests/136) | casw-kube | UEBA-1405 Merge/casw tooling | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#135](https://bitbucket.org/ins17/casw-kube/pull-requests/135) | casw-kube | UEBA-1405 Merge/casw kubernetes | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |
| [#133](https://bitbucket.org/ins17/casw-kube/pull-requests/133) | casw-kube | UEBA-1405 Merge/casw algorithms | OPEN | 2026-04-02 | [UEBA-1405](https://insidersecurity.atlassian.net/browse/UEBA-1405) update kube casw to rc6.3 |

---

### 3.2 Minor Changes

Small administrative and maintenance PRs — repository hygiene, changelog updates, tooling configuration, and binary version bumps — with no direct feature or bug-fix scope.

| PR | Repo | Title | State | Date | Ticket |
|---|---|---|---|---|---|
| [#2394](https://bitbucket.org/ins17/casw/pull-requests/2394) | casw | Feature/UEBA-1248 devserver provisioning patched | MERGED | 2026-01-23 | [UEBA-1248](https://insidersecurity.atlassian.net/browse/UEBA-1248) preparation of standard development environment |
| [#2300](https://bitbucket.org/ins17/casw/pull-requests/2300) | casw | remove githooks | MERGED | 2025-10-27 | — |
| [#2313](https://bitbucket.org/ins17/casw/pull-requests/2313) | casw | remove vscode settings.json | MERGED | 2025-11-07 | — |
| [#2303](https://bitbucket.org/ins17/casw/pull-requests/2303) | casw | fix/UEBA-1165-update-test-unit-for-listen_sensorless_log | MERGED | 2025-10-31 | [UEBA-1165](https://insidersecurity.atlassian.net/browse/UEBA-1165) minor sync up repo and add docker for development |
| [#144](https://bitbucket.org/ins17/sensor/pull-requests/144) | sensor | CHANGELOG.md edited for merging UEBA-988, UEBA-997, UEBA-1045 | MERGED | 2025-10-03 | — |
| [#145](https://bitbucket.org/ins17/sensor/pull-requests/145) | sensor | CHANGELOG.md formatting change | MERGED | 2025-10-03 | — |
| [#54](https://bitbucket.org/ins17/infrastructure/pull-requests/54) | infrastructure | update sensor binary to 2.4.2.0 | MERGED | 2025-10-03 | — |
| [#53](https://bitbucket.org/ins17/infrastructure/pull-requests/53) | infrastructure | CHANGELOG.md edited for PR of UEBA-933, UEBA-997 | MERGED | 2025-10-03 | — |
| [#48](https://bitbucket.org/ins17/infrastructure/pull-requests/48) | infrastructure | remove ssh key | MERGED | 2025-06-16 | — |

---

### 3.3 Reference Documentation

Design and reference documents with no directly associated pull request.

**Location:** `Handover - Minsuan/Design Documentation/`

| Document | File | Description |
|---|---|---|
| Windows Agent Config | `windows_agent_config.md` | Reference for every INI configuration key in the Windows sensor agent (`cgagent/config.cpp`). Covers sections `[local agent]`, `[logs]`, `[log_rotate_path]`, `[log_rotate_size]`, `[auth]`, Windows Event Log sections, and troubleshooting tips. |
| Manual Retroactive Processing | `manual_retroactive.md` | Guide for manually triggering retroactive/backfill processing runs. |
| TLS vs SSH | `tls_vs_ssh.md` | Comparison and guidance on TLS vs SSH transport options for log forwarding. |
| CASW Parsing Architecture & SREF | `CASW-Parsing Architecture and Standard Raw Event Format (SREF)-120326-084009.pdf` | PDF specification of the overall CASW parsing architecture and the Standard Raw Event Format (SREF) that all parsers must produce. |

---

### 3.4 System Configuration Guides

Customer-facing configuration guides for databases where monitoring was pre-existing functionality rather than a newly developed feature.

**Location:** `Handover - Minsuan/System Configuration Guide/`

#### MySQL (On-Premises)

| Document | File(s) | Description |
|---|---|---|
| MySQL — Linux | `DB - Monitor MySQL Configuration (Linux) v1.1.docx` | Enables MySQL slow-query and general logging on a Linux host for InsiderSecurity monitoring. |
| MySQL — Linux (Syslog Forwarding) | `DB - Monitor MySQL Configuration (Linux) (Forwarding with Syslog).pdf` | Variant for forwarding MySQL logs via syslog on Linux (PDF only). |
| MySQL — Windows | `DB - Monitor MySQL Configuration (Windows).docx/.pdf` | Enables MySQL logging on a Windows host. |

#### PostgreSQL

| Document | File(s) | Description |
|---|---|---|
| PostgreSQL — Linux | `DB - Monitor PostgreSQL Configuration (Linux).docx/.pdf` | Enables PostgreSQL logging on Linux for InsiderSecurity monitoring. |
| PostgreSQL — Windows | `DB - Monitor PostgreSQL Configuration (Windows).docx/.pdf` | Enables PostgreSQL logging on Windows. |

#### OracleDB

| Document | File(s) | Description |
|---|---|---|
| OracleDB — Windows | `DB - Monitor OracleDB Configuration (Windows).docx/.pdf` | Enables OracleDB audit logging on Windows for InsiderSecurity monitoring. |

---

### 3.5 Other Documents

| Document | File | Description |
|---|---|---|
| Mail Config for Dev Server | `Handover - Minsuan/Reports/mail_config_for_dev_server.md` | Snippet for `mail_worker.rb` to bypass the MongoDB config lookup and send emails directly via the InsiderSecurity SMTP relay (`sg-smtp-svr15.insidersecurity.co:2525`). Useful when testing email functionality on a dev server where `mail_config` is not available from MongoDB. |
| AI-Assisted Coding Workflow | `Handover - Minsuan/Reports/AI_Assisted_Coding_Workflow_InsiderSecurity.md` | Evaluation of AI-assisted coding tools for InsiderSecurity. Covers IDE tools (GitHub Copilot, Cursor, Google Antigravity), CLI agents (GitHub Copilot CLI, opencode, Claude Code, Rovodev), and code review tools (Aikido, Qodo). Includes hands-on test results from the casw→casw-kube migration and UEBA-853, and a feature comparison of Rovo Dev CLI vs opencode vs Claude Code. Recommended workflow: VS Code + GitHub Copilot for daily coding, opencode for agentic tasks and pre-PR review, Aikido for security scanning. |
