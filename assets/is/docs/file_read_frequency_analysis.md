---
Title: File Read Frequency Analysis Configuration Guide
Author: Teh Min Suan
Date: 21 April 2024
---

- [File Read Frequency Analysis Configuration Guide](#file-read-frequency-analysis-configuration-guide)
  - [Enabling Frequency Analysis](#enabling-frequency-analysis)
  - [Disabling Frequency Analysis](#disabling-frequency-analysis)
  - [Notes](#notes)

# File Read Frequency Analysis Configuration Guide

This guide explains how to enable or disable frequency analysis for file read operation. Refer to the pull request [here](https://bitbucket.org/ins17/casw/pull-requests/2209) for more details on the changes made.

## Enabling Frequency Analysis

Follow these steps to enable frequency analysis:

1. **Update Required Files**:
   - `frequency_analysis.py` - Configure with appropriate parameters
   - `apps/os.py` - Add list of actions to be monitored
   - `parser_win_security.py` - Update to include file name for frequency analysis
   - `setup_os_alerts.rb` - Ensure frequency analysis alerts are defined
   - `setup_os_riskscores.rb` - Setup risk scores for frequency analysis alerts
   - `algos_os.monit` - Add frequency analysis to the monitored processes

   **Configuration Options in os.py**:

   You can configure the file monitoring thresholds in os.py using these formats:

   ```python
   # Monitor a specific file for each user
   {"res_type": "file", "action_type": "read", "res_name": "C:\\path\\to\\the\\file\\secret.txt", "threshold": 20}

   # Monitor all files for each user
   {"res_type": "file", "action_type": "read", "threshold": 20}
   ```

   The first option monitors a specific file for each user, while the second option monitors all file read operations for each user. The threshold value determines how many accesses trigger an alert.

2. **Run Setup Scripts**:

   ```bash
   ruby setup_os_riskscores.rb
   ruby setup_os_alerts.rb
   ```

   This will update the database with required risk scores and alert definitions.

3. **Restart the Bayesian Network Engine and parser**:

   ```bash
   pkill -f BNWEngine
   pkill -f parser_win_security
   ```

   This terminates the Bayesian Network engine to allow it to restart with new configurations.

4. **Restart Monitoring Services**:

   ```bash
   ./monit_restart.sh
   ```

   This will restart all monitored services with the updated configurations.

5. **Verification**:
   - Check that the frequency analysis process is running:

   ```bash
   ps aux | grep frequency_analysis
   ```

   - Verify logs show it's operational:

   ```bash
   tail -f ./logs/frequency_analysis_os.log
   ```

## Disabling Frequency Analysis

If you need to disable frequency analysis and revert to traditional file read alerts:

1. **Comment Out Frequency Analysis in Monit Configuration**:
   - Edit `algos_os.monit` and comment out the frequency_analysis entry:

   ```monit
    check process os_frequency_analysis matching "frequency_analysis/frequency_analysis.py os"
        start program = "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/algo.rb start frequency_analysis frequency_analysis.py os &>>/home/bitnami/casw/nohup.out'" with timeout 5 seconds
        stop program  = "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/algo.rb stop frequency_analysis frequency_analysis.py os &>>/home/bitnami/casw/nohup.out'"
        if memory > 5% for 2 cycles then exec "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/scripts/log_usage.rb os_frequency_analysis memory 5%'"
        if cpu > 95% for 40 cycles then exec "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/scripts/log_usage.rb os_frequency_analysis cpu 95%'"
        if memory > 5% for 2 cycles then restart
   ```

2. **Restart Monit**:

   ```bash
   ./monit_restart.sh
   ```

   This will update the monitoring service to stop tracking the frequency analysis process.

3. **Manually Terminate the Frequency Analysis Process**:

   ```bash
   pkill -f "frequency_analysis os"
   ```

   This ensures that any running instances are terminated.

4. **Enable Standard File Read Alerts in win_login.py**:
   - Make sure that the win_login.py file is updated
   - Open the windows.monit file
   - Replace the win_login entry with the following:

   ```monit
    check process win_login matching "win_login.py 0 --monitor_file_read"
        start program = "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/algo.rb start win_login win_login.py 0 --monitor_file_read &>>/home/bitnami/casw/nohup-`hostname`.out'" with timeout 10 seconds
        stop program = "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/algo.rb stop win_login win_login.py 0 --monitor_file_read &>>/home/bitnami/casw/nohup-`hostname`.out'"
        if memory > 5% for 2 cycles then exec "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/scripts/log_usage.rb win_login memory 5%'"
        if cpu > 95% for 40 cycles then exec "/bin/bash -c 'source /usr/local/rvm/environments/default && /home/bitnami/casw/scripts/log_usage.rb win_login cpu 95%'"
        if memory > 1 GB for 2 cycles then restart
   ```

5. **Restart Monit and win_login.py**:

   ```bash
   ./monit_restart.sh
   pkill -f win_login.py
   ```

   The service will automatically restart with the updated configuration.

6. **Verification**:
   - Confirm frequency analysis is no longer running:

   ```bash
   ps aux | grep "frequency_analysis os"
   ```

   - Verify standard file read alerts are being generated in the logs.

## Notes

- Frequency analysis will generate alerts at 11.45pm on every Sunday.
- For standard file read alerts, the first action will trigger an alert per day for each user but have lower latency.
