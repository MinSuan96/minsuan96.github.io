# Resume Bullet Point Changes — InsiderSecurity

## Suggested Bullets

- **Core Risk Engine Optimization:** Led end-to-end performance overhaul (multiprocessing, code streamlining, cache redesign) achieving >= 140% throughput improvement.

- **Cloud & Hybrid Integration:** Extended product from on-prem only to hybrid/cloud by building Azure Event Hub and Blob Storage ingestion pipelines (with managed-identity auth and PGP decryption), AWS CloudWatch readers, and a sensorless log path -- enabling GCC compliance and eliminating the need for on-prem sensors.

- **Log Forwarding Framework:** Built and extended an external SOC forwarder supporting Windows, SSH, DNS, network device, and PowerShell log types with RFC 5424 syslog formatting, Redis metrics, UEBA alert forwarding, and UDP large-message handling.

- **Kubernetes Migration:** Led full migration of the on-premises codebase to a Kubernetes deployment, covering shared libraries, core daemons, alerting, and algorithm modules across hundreds of files with documented merge rules and environment reconciliation.

- **Database Activity Monitoring Expansion:** Added MariaDB audit-log ingestion (parser + ELK pipeline), RDS MySQL CE support via CloudWatch, Azure SQL monitoring via Event Hub and Log Analytics, and rewrote the SQL row-access anomaly detector from Ruby to Python with scheduled backfill and integration tests.

- **Sensor Feature Expansion (C++):** Added log rotation, wildcard file monitoring, Windows Credential Manager integration for secure passphrase storage, timezone-aware logging, XML event log collection, and self-service file monitoring configurable through the UI.

## Change Summary

| # | Before | After | Rationale |
|---|--------|-------|-----------|
| 1 | Core Risk Engine Optimization | Core Risk Engine Optimization | No change — strong and quantifiable. |
| 2 | Cloud Integration (generic) | Cloud & Hybrid Integration (merged with old bullet 3) | Combines two thin bullets into one specific one; frees a slot. |
| 3 | New Log Ingestion Pipeline (1 PR) | Log Forwarding Framework (11 PRs) | Replaces smallest feature with largest missing one. |
| 4 | Legacy Refactoring (generic) | Kubernetes Migration (8 PRs) | Replaces vaguest bullet with concrete, verifiable architectural work. |
| 5 | Sensor (unchanged scope) | Sensor (broader scope) | Folds in self-service file monitoring and credential manager. |
| 6 | Automated Sensor Config (1 PR) | DAM Expansion (multi-DB, rewrite) | Replaces smallest-scope bullet with substantial cross-platform DB work. |
