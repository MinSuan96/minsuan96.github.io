---
Title: Azure Blob Storage Listener
Author: Teh Min Suan
Date: 26 August 2025
---

- [Azure Blob Storage Listener](#azure-blob-storage-listener)
  - [Overview](#overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Configuration](#configuration)
    - [Azure SDK Mode (connection\_string.json)](#azure-sdk-mode-connection_stringjson)
    - [SFTP Mode (sftp\_connections.json)](#sftp-mode-sftp_connectionsjson)
    - [Configuration Parameters](#configuration-parameters)
  - [Optional File Decryption (SFTP Mode)](#optional-file-decryption-sftp-mode)
  - [Installation and Running the Script](#installation-and-running-the-script)
  - [How It Works](#how-it-works)

# Azure Blob Storage Listener

## Overview

The Azure Blob Storage Listener consists of two Python scripts that automatically download files from Azure Storage accounts on a scheduled basis:

1. **`listen_azure_blob_storage.py`** — Uses Azure SDK to connect directly to Azure Blob Storage. **This script is outdated and no longer actively maintained; prefer the SFTP variant for new deployments.**
2. **`listen_azure_blob_storage_sftp.py`** — Uses SFTP protocol to connect to Azure Blob Storage SFTP endpoint. This is the actively maintained version.

## Features

- Connect to multiple Azure Blob Storage accounts via Azure SDK or SFTP
- Schedule downloads on specific days of the week
- Track last download time to only download new files
- Persist last run time in JSON file for service restarts
- Track downloaded file paths in a local log file
- Maintain directory structure that mirrors the container structure
- Comprehensive logging for monitoring and debugging
- Configurable download paths for different storage accounts
- File retention size management
- Support for both Azure SDK connection strings and SFTP authentication (password or private key)
- Optional per-file decryption using GPG keys stored in Azure Key Vault (SFTP mode)
- Supports RSA, Ed25519 and ECDSA private key formats for SFTP authentication
- Controlled large-file download concurrency to avoid Azure throttling (prefetch capped at 64)

## Requirements

- Required Python packages:
  - **For Azure SDK mode** (`listen_azure_blob_storage.py`):
    - azure-storage-blob
    - schedule
    - env_helper
  - **For SFTP mode** (`listen_azure_blob_storage_sftp.py`):
    - paramiko
    - schedule
    - env_helper
    - azure-identity
    - azure-keyvault-secrets
    - python-gnupg

## Configuration

There are two configuration modes depending on which script you use:

### Azure SDK Mode (connection_string.json)

The Azure SDK script (`listen_azure_blob_storage.py`) uses a JSON configuration file to store connection strings and schedule information. The configuration file should be named `connection_string.json` and placed in the same directory as the script.

**Connection String Sources:**
Connection strings can be obtained from the Azure portal using:

- **Access Keys**: Full access to the storage account (primary or secondary key)
- **Shared Access Signature (SAS)**: Time-limited, permission-scoped access

**Configuration Format:**

```json
[
    {
        "connection_string": "DefaultEndpointsProtocol=https;AccountName=account1;AccountKey=key1;EndpointSuffix=core.windows.net",
        "days": ["Sunday", "Wednesday"],
        "path": "/custom/download/path",
        "retention_size": 20,
        "output_file": "custom_download_log.txt"
    },
    {
        "connection_string": "DefaultEndpointsProtocol=https;AccountName=account2;AccountKey=key2;EndpointSuffix=core.windows.net",
        "days": ["Monday"],
        "retention_size": -1
    }
]
```

### SFTP Mode (sftp_connections.json)

The SFTP script (`listen_azure_blob_storage_sftp.py`) uses a separate JSON configuration file for SFTP connections. The configuration file should be named `sftp_connections.json` and placed in the same directory as the script.

**Prerequisites for SFTP Mode:**

- Azure Storage account must have ADLS Gen2 (hierarchical namespace) enabled
- SFTP endpoint must be enabled on the storage account
- Local users must be created for SFTP access

When creating a local user for SFTP, a connection string will be given in the format:
`<STORAGE_ACCOUNT>.<CONTAINER_NAME>.<LOCAL_USER>@<SFTP_ENDPOINT>`

For example: `test_account.testcontainer.test_user@test_account.blob.core.windows.net`

**Configuration Format:**

```json
[
    {
        "host": "test_account.blob.core.windows.net",
        "port": 22,
        "username": "test_account.testcontainer.test_user",
        "password": "secure-password-here",
        "root_paths": ["/container-a", "/container-b/subpath"],
        "days": ["Monday", "Thursday"],
        "path": "/custom/download/path",
        "retention_size": 500,
        "output_file": "downloaded_sftp_user1.txt"
    },
    {
        "host": "test_account.blob.core.windows.net",
        "port": 22,
        "username": "test_account.testcontainer.test_user",
        "private_key_path": "/path/to/private/key",
        "private_key_passphrase": "key-passphrase",
        "root_paths": ["/logs"],
        "days": ["Tuesday", "Friday"],
        "path": "./data/sftp-logs",
        "retention_size": 100,
        "output_file": "downloaded_logs.txt",
        "decryption_key": "keys/my_private_key.asc"
    }
]
```

### Configuration Parameters

**Common Parameters (both modes):**

- `days`: List of days when the download should run (valid values: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
- `path` (optional): Custom path where the files will be downloaded. If not specified, defaults to a "data" directory in the script's directory
- `retention_size` (optional): Maximum size in MB for each path. Default is 20MB.
  - If set to a positive number, the content of the folder exceeding this size will be deleted
  - If set to zero or a negative number (like -1), there will be no size limit (infinite retention)
- `output_file` (optional): Custom filename for recording newly downloaded files. If not specified, defaults to `downloaded_blobs_{connection_string}.txt` (Azure SDK) or `downloaded_sftp_{username}@{host}.txt` (SFTP)

**Azure SDK Mode Parameters:**

- `connection_string`: The Azure Storage connection string (can be obtained from the Azure portal via Access Keys or Shared Access Signature)

**SFTP Mode Parameters:**

- `host`: SFTP endpoint hostname (e.g., `myaccount.blob.core.windows.net`)
- `port` (optional): SFTP port number, defaults to 22
- `username`: SFTP username for authentication
- `password` (optional): Password for authentication (use either password or private key)
- `private_key_path` (optional): Path to private key file for authentication (use either password or private key)
- `private_key_passphrase` (optional): Passphrase for encrypted private key
- `root_paths` (optional): List of remote root paths to scan, defaults to `["/"]`
- `download_time` (optional): Time when downloads should run in HH:MM format, defaults to "01:00" (1:00 AM)
- `rotation_time` (optional): Time when data rotation/cleanup should run in HH:MM format, defaults to "00:00" (12:00 AM)
- `timeout` (optional): SSH/SFTP connection timeout in seconds (applies to initial handshake and auth). Defaults to 120. Increase this for slower networks or large key-based auth.
- `retries` (optional): Number of per-file download retry attempts if a transfer fails. Defaults to 3. Each retry re-establishes the SFTP session before attempting again.
- `vault_url` (optional): Azure Key Vault URL (e.g. `https://myvault.vault.azure.net/`). If provided, enables secret retrieval for GPG decryption.
- `secret_name` (optional): Name of the secret in Key Vault containing the ASCII-armored GPG private key or key material.
- `secret_passphrase` (optional): Passphrase used when importing/decrypting with the retrieved GPG key.
- `decryption_key` (optional): **Path** to a local ASCII-armored PGP private key file, relative to the script's directory (e.g. `"keys/my_private_key.asc"`). The file must reside inside the script's own directory; paths outside that directory are rejected for security. Used when Key Vault is not configured. Cannot be used together with `vault_url`/`secret_name` — vault takes priority when both are present.

If `vault_url` is specified but `secret_name` is missing, decryption is skipped. If Key Vault parameters are not provided, you can still decrypt by setting `decryption_key` to a path of a key file inside the script's directory; the script will read and import that local key instead of retrieving from vault. If decryption fails, the original encrypted file is retained.

**Large File Download Behavior (`max_concurrent_prefetch_requests`):**

The SFTP implementation uses Paramiko's optimized prefetch when calling `sftp.get(...)` with `max_concurrent_prefetch_requests=64`. This internal cap was added because without limiting concurrent prefetch chunk requests, downloading very large blobs can trigger Azure Storage's defensive heuristics which may treat the high-rate, unthrottled request pattern as abusive and forcibly close the connection. Setting the prefetch concurrency to 64 balances throughput and stability:

- Ensures large files can be fully downloaded without premature connection termination
- Avoids overwhelming the storage endpoint with excessive parallel range reads
- Provides efficient pipeline depth for high-latency links

This value is currently fixed (not user-configurable) and chosen as so to be aligned with OpenSSH's sftp internal limit; adjust only if future Azure guidance changes or performance measurements justify it.

## Optional File Decryption (SFTP Mode)

Decryption supports two key sources:

- **Azure Key Vault key**: provide `vault_url` + `secret_name` (and optionally `secret_passphrase`).
- **Local key file**: provide `decryption_key` as a path to a key file inside the script's directory (and optionally `secret_passphrase`).

When decryption is enabled, each successfully downloaded file will be processed as follows:

1. Load GPG key material from Key Vault (if `vault_url` + `secret_name` are configured) or from the local key file at `decryption_key` path.
2. Import the key via `python-gnupg`.
3. Decrypt the file, writing the output to the same path with the `.pgp` or `.gpg` extension stripped.
4. On success, the original encrypted file is deleted and only the decrypted file remains. On failure, the original encrypted file is retained (no retry loop — retries apply only to the SFTP download step, not to decryption).

Security considerations:

- Ensure least-privilege access for the Key Vault (limit secret scope, avoid broad RBAC roles).
- Rotate GPG keys periodically and update the stored secret.
- Prefer managed identities for Key Vault access instead of interactive credentials.
- Local key files must reside inside the script's directory; the script validates the resolved path and rejects any path outside that boundary to prevent arbitrary file reads.

If decryption is not required, omit both Key Vault parameters and `decryption_key`, and skip decryption-related packages.

## Installation and Running the Script

1. Install the required Python packages:

    **For Azure SDK mode:**

    ```bash
    # For systems with internet access:
    pip3 install azure-storage-blob

    # For offline/air-gapped systems:
    # First download packages on a system with internet:
    pip3 download azure-storage-blob -d offline_pkgs --python-version <PYTHON_VERSION> --only-binary=:all:

    # Then transfer the offline_pkgs folder to the air-gapped system and install:
    pip3 install --no-index --find-links=offline_pkgs offline_pkgs/*.whl
    ```

    **For SFTP mode:**

    ```bash
    # For systems with internet access:
    pip3 install paramiko azure-identity azure-keyvault-secrets python-gnupg

    # For offline/air-gapped systems:
    # First download packages on a system with internet:
    pip3 download paramiko azure-identity azure-keyvault-secrets python-gnupg -d offline_pkgs --python-version <PYTHON_VERSION> --only-binary=:all:

    # Then transfer the offline_pkgs folder to the air-gapped system and install:
    pip3 install --no-index --find-links=offline_pkgs offline_pkgs/*.whl
    ```

2. Update the appropriate script and configuration file:
   - For Azure SDK: `listen_azure_blob_storage.py` and `connection_string.json`
   - For SFTP: `listen_azure_blob_storage_sftp.py` and `sftp_connections.json`

3. Update the `algos_main.monit` monit file to monitor the chosen script.

4. Restart the monit service to apply the changes:

    ```bash
    monit_restart.sh
    ```

## How It Works

1. **Initialization**:
   - **Azure SDK mode**: Loads connection settings from `connection_string.json`
   - **SFTP mode**: Loads connection settings from `sftp_connections.json`
   - Sets up logging as defined in the environment helper
   - **Azure SDK mode**: Loads last run times from `last_run_time.json`
   - **SFTP mode**: Loads last run times from `last_run_time_sftp.json`

2. **Scheduling**:
   - For each connection, schedules:
     - **Azure SDK mode**: Data downloads at 1 AM on specified days (fixed time)
     - **SFTP mode**: Data downloads at configurable time (default 1:00 AM) on specified days
     - **Azure SDK mode**: Data rotation (folder cleanup) at 12 AM on the same days (fixed time)
     - **SFTP mode**: Data rotation (folder cleanup) at configurable time (default 12:00 AM) on the same days
   - No downloads or data rotation are run immediately upon script start in **Azure SDK mode**; all actions follow the schedule. In **SFTP mode**, all scheduled jobs can run once immediately on startup if line 527 is uncommented (`schedule.run_all()`) and then continue on their configured schedule.

**Downloading**:

- **Azure SDK mode**: Only downloads blobs created since the last recorded run (uses blob creation_time)
- **SFTP mode**: Only downloads files modified since the last recorded run (uses file mtime)
- Replicates the container/directory structure in the local filesystem
- **Azure SDK mode**: Saves to `data/container_name/blob_name` or custom path
- **SFTP mode**: Preserves directory structure relative to root_paths
- Logs all downloaded files in the specified output file
- Per-file retries (default 3) and session re-connect logic increase robustness against transient network drops
- Uses controlled parallel prefetch (`max_concurrent_prefetch_requests=64`) during SFTP transfers to safely sustain throughput for large blobs without triggering Azure anti-abuse connection resets
- Updates and persists the last run time after each successful download

**Data Management**:

Monitors and manages folder size according to the `retention_size` parameter:

- If the folder exceeds the retention size, its contents are deleted
- If under the limit, new content is added
- A `retention_size` of 0 or -1 disables size limits

**Monitoring**:

Logs key events and errors to help with monitoring and troubleshooting.

- All logs are written to the file specified by the environment helper

**Key Differences:**

- **Azure SDK mode**: Uses Azure blob creation_time for filtering, accesses all containers in storage account
- **SFTP mode**: Uses file modification time (mtime) for filtering, only accesses paths mapped to the SFTP user
- **SFTP mode**: Requires ADLS Gen2 storage account with SFTP endpoint enabled and local users configured
