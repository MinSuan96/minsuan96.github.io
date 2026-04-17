---
Title: Storing Windows Sensor Passphrase in Windows Credential Manager
author: Teh Min Suan
date: 5 December 2025
---

## `credential_manager.ps1`

The script at `infrastructure/provision/files/windows/sensor2-self-ip/zip/self/scripts/credential_manager.ps1` securely seeds the agent passphrase into Windows Credential Manager.

### Execution flow

- Accepts a single mandatory parameter (`$Passphrase`) supplied by the installer.
- Fixes the credential target to `CGAgentPassphrase`, matching the identifier referenced elsewhere in the agent configuration, and uses a placeholder username (`cgagent`).
- Creates a one-time scheduled task (`CGAgentCredentialManager`) that runs as `SYSTEM` and executes `cmdkey.exe` to register the generic credential.
- Immediately starts the scheduled task, waiting for the exit code reported by `schtasks`.
- Removes the helper scheduled task after execution so no artefacts are left behind.
- Exits with a non-zero status if any task creation or execution step fails, allowing callers to abort installation on error.

Because the task runs in the `SYSTEM` context, the resulting credential is stored where the sensor service can retrieve it without exposing the passphrase in plain text files.

## Usage within `installer.nsi`

During the Setup section of `infrastructure/provision/files/windows/sensor2-self-ip/installer.nsi`, the NSIS installer populates `$passphrase` when the operator provides a value:

```nsi
${If} $passphrase != ""
    nsExec::ExecToStack /TIMEOUT=15000 'powershell -inputformat none -ExecutionPolicy RemoteSigned -File "$INSTDIR\scripts\credential_manager.ps1" "$passphrase"'
    ...
${Else}
    !insertmacro write_to_console "Passphrase empty, skipping credential manager configuration"
${EndIf}
```

The `nsExec::ExecToStack` call runs the PowerShell script inside the staged installation directory. Any non-zero exit code bubbles up to the installer, which logs the failure, informs the user, and aborts the deployment. When the passphrase field is left blank, the installer deliberately skips credential creation.

## `agent_config.in` passphrase identifier

`infrastructure/provision/files/windows/sensor2-self-ip/zip/self/agent_config.in` now declares:

```ini
passphrase_identifier = CGAgentPassphrase
```

This value aligns the runtime agent with the Windows Credential Manager entry seeded by `credential_manager.ps1`. The agent resolves the stored secret by looking up the `passphrase_identifier`, so the consistent target name (`CGAgentPassphrase`) ensures the freshly installed credential is discovered at startup. Adjust this identifier only if both the script and configuration are updated together.

## Runtime retrieval inside the agent

- `sensor/windows2/cgagent/cgagent/config.cpp` reads `passphrase_identifier` while loading the INI configuration.
- When the identifier is present, `load_config` calls `retrieve_passphrase`, a helper that converts the UTF-8 identifier to UTF-16 and issues `CredReadW` with `CRED_TYPE_GENERIC`.
- On success the credential blob is copied back to UTF-8, logged at info level, and assigned to `config_struct->passphrase`. Failures are logged and the agent continues with an empty string.
- The passphrase is only pulled after the rest of the log configuration completes, ensuring Credential Manager is the single source of truth at runtime.

## Operational notes

- The installer and the PowerShell script must run with administrative privileges so they can register scheduled tasks under the `SYSTEM` account.
- If manual credential rotation is required, rerun `credential_manager.ps1` with the new passphrase to overwrite the existing `CGAgentPassphrase` entry.
- Installation logs emitted through `write_to_console` or the NSIS detail pane capture successes or failures from the credential provisioning step, aiding troubleshooting.
