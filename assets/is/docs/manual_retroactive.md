---
Title: Manual Retroactive Visuals Review Reports
Author: Teh Min Suan
Date: 10 December 2024
---

- [Introduction](#introduction)
- [Report Generation](#report-generation)
  - [manual_retroactive.rb](#manual_retroactiverb)
  - [visuals_entity_card.rb](#visuals_entity_cardrb)
  - [visuals_review_reports.rb](#visuals_review_reportsrb)
  - [The APIs](#the-apis)
    - [visuals_infrastructure_report/api.rb](#visuals_infrastructure_reportapirb)
    - [visuals_generic_reports/api.rb](#visuals_generic_reportsapirb)
    - [visuals_application_reports/api.rb](#visuals_application_reportsapirb)
    - [visuals_entity_card/api.rb](#visuals_entity_cardapirb)
- [DB.alerts population](#dbalerts-population)
  - [Storage of Old Logs](#storage-of-old-logs)
  - [alerts_db_populator.db](#alerts_db_populatordb)
  - [Requirement of Old Alert Generation](#requirement-of-old-alert-generation)
  - [Alert Count Manager Runner](#alert-count-manager-runner)
    - [How to Use alert_count_manager_runner.py](#how-to-use-alert_count_manager_runnerpy)
    - [What Happens When It Runs](#what-happens-when-it-runs)
- [Guide to Setup Manual Retroactive for Other Subsystem](#guide-to-setup-manual-retroactive-for-other-subsystem)
  - [System Type Selection and Message Handling](#system-type-selection-and-message-handling)

## Introduction

This document will describe the implementation of `manual_retroactive.rb` and `alerts_db_populator.rb`. `manual_retroactive.rb` is used to generate riskscore, populate relevant database and generate a report based on the given parameters. On the other hand, `alerts_db_populator.rb` is used for getting old logs from ELK and sending them to `BNWEngine` to populate `db.test_timeline`.

The code for this feature is available on the branch [`feature/UEBA-646-generate-retroactive-reports`](https://bitbucket.org/ins17/casw/branch/feature/UEBA-646-generate-retroactive-reports).

Note that this feature is currently available to OS subsystem only. An implementation guide for the other subsystem will be included in this document.

## Report Generation

### manual_retroactive.rb

`algos/visuals_review_reports/manual_retroactive.rb` is responsible for generating custom report. The script requires 3 arguments which are:

- start date of report, eg: 01-07-2024
- end date of report, eg: 01-08-2024
- name of report group, eg: test_group

Here is what the script does upon running:

1. The script will do some processing to get the epoch of start date and end date, as well as the id and subsystem of report group.
2. Then, The script will get some of the alerts in `db.alerts` and calculate the riskscore based on the alerts. To ensure consistency with `BNWEngine`, the alerts obtained are ranged from `end_date - 29 days` to `end_date`.
3. The calculated riskscore will be updated to `db.riskscore_compiler`. Depending on the end date of the alerts, the riskscore will be either updated in `adjusted_riskscore` or `user_riskscore_archive`.
4. After that, the populator function from `algos/visuals_entity_card/visuals_entity_card.rb` will be called by the script. This includes the system populator class and threat_populator class. The reason behind this step is to populate `db.visuals_entity_card` with the entities, tags and threats (alerts).
5. The script will now call `do_snapshot` from `algos/visuals_review_reports/visuals_review_reports.rb` to generate a report based on the given timerange. The timerange will be passed as `filter_time` and `filter_time_end` to the function. In which, the parameters will also be passed to the APIs to generate relevant data in the report. (For now, `visuals_generic_reports/api.rb` and `visuals_infrastructure_report/api.rb` will accept these parameters)
6. Lastly, the script will update the creation time of the report in `db.log_report_archive` so that the creation time will be changed to the end date of the report. This is to make sure that the report can be shown correctly in dashboard UI.

### visuals_entity_card.rb

As mentioned in the earlier section, the populator class will be called by `manual_retroactive.rb` to populate `db.visuals_entity_card`. A few changes have to be done before using the populator class in this script.

1. The `Populator` class and `Threat_Populator` class are given two additional class variables: `@filter_time` and `@filter_time_end`. All the queries that get/update data from/to the database have to include both of these class variables as part of the filter.
2. Functions involved include `init_empty_entities`, `populate_riskscore`, `_populate_tags` and `populate_threats_all`.
3. A new function called `set_time` is added to set the `@filter_time` and `@filter_time_end` class variables. This function will be called by the `manual_retroactive.rb` script to set the time range of the report.

### visuals_review_reports.rb

There is only a single function that needs to be changed in `visuals_review_reports.rb` which is `do_snapshot`.

1. Previously, the function requires only two arguments: `log` and `schedule_cron`. Now, it accepts four more optional arguments: `report_group_ids`, `filter_time`, `filter_time_end` and `notify`.
2. If `report_group_ids` is not given, then the function will use `schedule_cron` to get the id of report group to generate report. `filter_time` and `filter_time_end` have default values of `previous report time` and `current time`. If `notify` is not given, then the function will notify all the relevant entities in the report group.
3. Similar to `visuals_entity_card.rb`, all queries to the database need to include `filter_time` and `filter_time_end` as part of the filter. Hence, the parameters passed to the api by the function will also include these optional parameters.
4. If `notify` is given as `false`, then the function will not notify the entities in the report group. This is used when generating a retroactive report.

### The APIs

#### visuals_infrastructure_report/api.rb

When the api in `visuals_infrastructure_report` is called from `do_snapshot`, a variable, `params` will be passed to the function. Because of changes made in `do_snapshot`, `params` will now include two extra parameters which are `filter_time` and `filter_time_end`.

1. All of the functions that use `filter_time_end` or `filter_time` must now use both parameters.
2. All the functions involved in the changes above are: `get_report_group_entities_threats`, `get_user_list`, `get_datastore_access`, `get_top_login`, `get_logins_graph`, `get_risky_users`, `get_risky_servers`, `get_dormant_activity`, `get_install_activity`, `get_shutdown_activity`, `get_threat_status_count`, `retrieve_snapshot2` and `api`.
3. In order for the api to retrieve the riskscore of an entitiy based on a given time, some functions are modified to get the `past_risk_score` field or `user_riskscore_archive` field from the database.
4. Both of these fields contain the same list of riskscore with the only difference being `past_risk_score` is a field of `db.visuals_entity_card` while `user_riskscore_archive` is a field of `db.riskscore_compiler`. They contain the past riskscore of an entity in which the last element of the list is the riskscore of an entity from the previous day.
5. The difference between the target time and current time is calculated in term of days. Then, this value is used to retrieve the past riskscore of an entity from the mentioned list.
6. If the difference is 0, then the current riskscore will be used. On the other hand, if the difference is more than the length of the list, the entity will be ignored.
7. All the functions related to this are: `get_report_group_entities_threats`, `get_user_list` and `get_risky_servers`.

#### visuals_generic_reports/api.rb

1. All functions that use `filter_time_end` or `filter_time` must now include both parameters: `execute`, `entrypoint`, `get_events_count_stats`, `get_user_list`, `get_risky_servers_table`, `risky_entity?`, `get_entity_details` and `get_threat_status_count`.
2. Some functions are changed so that they can retrieve the past riskscore of an entity based on a given time: `get_risky_servers_table` and `get_entity_details`. The changes include getting the `past_risk_score` field or `user_riskscore_archive` field from the database. Hence, projections are added to the queries to get the mentioned fields.
3. `default_filter_time` and `default_filter_time_end` are set as the default of the filters used throughout the script.

#### visuals_application_reports/api.rb

1. All functions that use `filter_time_end` or `filter_time` must now include both parameters: `high_risk_users`, `high_risk_hosts` and `get_report_group_entities_threats`
2. Some functions are changed so that they can retrieve the past riskscore of an entity based on a given time: `high_risk_users`, `high_risk_hosts` and `get_report_group_entities_threats`. The changes include getting the `past_risk_score` field or `user_riskscore_archive` field from the database. Hence, projections are added to the queries to get the mentioned fields.
3. `default_filter_time` and `default_filter_time_end` are set as the default of the filters used throughout the script.

#### visuals_entity_card/api.rb

`visuals_entity_card/api.rb` requires minimal changes to retrieve the relevant entity details when querying the database.

1. `filter_time_start` (instead of `filter_time`) and `filter_time_end` are set as part of the filters used throughout the script when getting entity details.
2. All the functions that require this change are: `get_entity_details` and `get_threats`.

## DB.alerts population

### Storage of Old Logs

All of the logs that are sent to the analytic server will be picked up by `event_archiver_v2.py` or `event_archiver.py`. The scripts will store logs in `db.cache_archive_dump` after processing. In theory, we can retrieve any old logs from `db.cache_archive_dump` but this collection is purposely limited to 500MB in size. Hence, it is necessary to retrieve the old logs from Elasticsearch instead.

The data inside Elasticsearch is updated by Monstache which monitors various collections of the database. It has a configuration file located as `/etc/monstache/config_multi.toml`. As written inside the configuration file, the script that tells Monstache how to treat the data inside `db.cache_archive_dump` is located as `/etc/monstache/raw.category.app.js`.

For those that are interested in what the script does, you can read the script to understand it better.

The script stores logs with the following index patterns:

- Windows system logs: `is.raw.os.os_windows.*`
- Linux system logs: `is.raw.os.linux.*`
- MSSQL database logs: `is.raw.db.db_mssql.*`
- Azure SQL database logs: `is.raw.db.azure_sql.*`

### alerts_db_populator.db

`algos/visuals_review_reports/alerts_db_populator.rb` is responsible for importing logs. The script requires an argument which is the source of the logs. The source can be either `elk`, `csv` or `txt`.

- start date of logs, eg: 01-07-2024
- end date of logs, eg: 01-08-2024

Here is what the script does upon running:

1. If the source is `elk`, it will access Elasticsearch using the default user and password.
   1. The script will request the start date and end date of the logs from the user. For example, start date of logs: 01-07-2024 while end date of logs: 01-08-2024
   2. The script will request the system type from the user. The supported system types are:
      - `linux` - Retrieves Linux logs from index pattern 'is.raw.os.linux\*'
      - `windows` - Retrieves Windows logs from index pattern 'is.raw.os.os_windows\*'
      - `mssql` - Retrieves MSSQL logs from index pattern 'is.raw.db.db_mssql\*'
      - `azure_sql` - Retrieves Azure SQL logs from index pattern 'is.raw.db.azure_sql\*'
      - `all` - Retrieves all logs
   3. Then, it will build a routing key for each log according to the agent id of the log and send the logs to RabbitMQ `received_log` channel with the routing key.
2. If the source is `csv` or `txt`, it will read the logs from the file and send them to RabbitMQ `received_log` channel with a routing key built from the agent id of the log.
   1. The script will request the path of the file from the user and the name of sensor of the logs.
   2. For `csv`, the fields are processsed to be separated by `~~~~~`.
   3. For `txt`, the logs are directly read and sent to RabbitMQ.

### Requirement of Old Alert Generation

To enable `BNWEngine` to receive old logs from `alerts_db_populator.rb` and insert them into `db.test_timeline`, several modifications are required across scripts on the analytic server:

1. The `event_archiver_v2.py` or `event_archiver.py` script must be executed with an additional argument, `false`. For instance, if the current command is:

   > python3 event_archiver_v2.py os 0

   it should be updated to:

   > python3 event_archiver_v2.py os 0 false

   Note that `algos_os.monit` has to be modified to incorporate this change.

2. Any adapter, parser, or algorithm between `event_archiver_v2/event_archiver` and `listen_log` must explicitly process old logs instead of ignoring them. For example, the Windows algorithms—`win_login.py`, `win_application.py`, and `win_share.py`—each contain a function called `is_old_log`, which identifies whether a log has already been processed. To implement this feature, the `is_old_log` function must always return false.
3. Any old logs passed to `alerts_worker.db` must include the `time_event` field. For instance, logs originating from `os_activity_analysis.py` previously lacked this field. A minor modification has been made to this script to ensure the `time_event` field is added to the log.

### Alert Count Manager Runner

After using `alerts_db_populator.rb` to populate the alerts database with historical data, it is essential to run the `alert_count_manager_runner.py` script to properly process these alerts for the api of `visuals_entity_card`. This script is located in the `algos/visuals_review_reports` directory.

#### How to Use alert_count_manager_runner.py

The script should be executed after the `alerts_db_populator.rb` has finished populating the database with historical logs. It accepts date parameters in the DD-MM-YYYY format:

```bash
python alert_count_manager_runner.py <start_date> <end_date>
```

For example:

```bash
python alert_count_manager_runner.py 01-07-2024 01-08-2024
```

This will process alerts between July 1, 2024, and August 1, 2024.

#### What Happens When It Runs

1. The script converts the provided dates to epoch timestamps.
2. It calls `alert_count_manager()` to process regular alerts within the specified time range.
3. It calls `alert_count_manager_whitelisted()` to process whitelisted alerts (false positives).
4. The results are stored in the `alert_count_manager` and `alert_count_manager_whitelisted` collections.
5. These collections are later used by the api of `visuals_entity_card` to generate first seen of threats.

## Guide to Setup Manual Retroactive for Other Subsystem

There are only three main requirements for `manual_retroactive.rb` to support generating reports for other subsystems.

1. The first requirement is that the APIs of the respective subsystem must include `filter_time` and `filter_time_end` when querying the database. Usually, this change needs to be made to most queries to `db.visuals_entity_card`, `db.riskscore_compiler`, and `db.alerts`.
2. The second requirement is that the APIs of the respective subsystem should retrieve the riskscore of entities from `past_risk_score` and `user_riskscore_archive` if applicable. This change usually needs to be made for queries to `db.visuals_entity_card` and `db.riskscore_compiler`.
3. The third requirement is that the populator of the respective subsystem should be modified so that `filter_time` and `filter_time_end` are used when processing data. Then, it should be called when running `manual_retroactive.rb`.

As for `alerts_db_populator.rb`, the script requires three changes:

1. The index pattern used in `alerts_db_populator.rb` already supports multiple system types including:
   - Windows logs (`is.raw.os.os_windows.*`)
   - Linux logs (`is.raw.os.linux.*`)
   - MSSQL logs (`is.raw.db.db_mssql.*`)
   - Azure SQL logs (`is.raw.db.azure_sql.*`)

   For additional subsystems, add the appropriate index pattern and message handling code.

2. Ensure that the adapter, parser, algorithm and processor of the subsystem does not ignore old logs and includes the `time_event` field in the logs.

3. Ensure that `false` is included as part of the arguments of `event_archiver_v2/event_archiver` when running the script to process old logs.

### System Type Selection and Message Handling

The `alerts_db_populator.rb` script has been enhanced to handle different system types with specialized processing:

1. **System Type Prompt**: When running in ELK mode, the script now prompts users to specify which system type they want to retrieve logs for:

   ```bash
   Enter the system type (linux/windows/mssql/azure_sql/all):
   ```

2. **Specialized Message Formatting**: Each system type has its own formatting requirements:
   - **Windows logs**: Formatted with event categories, event IDs, and base64-encoded messages
   - **Linux logs**: Raw log content is preserved
   - **MSSQL logs**: Formatted with semicolon-separated key-value pairs
   - **Azure SQL logs**: Formatted as structured MessagePack data

3. **Sensorless Processing**: For certain log types like Azure SQL that don't correspond to a specific sensor, the script implements a sensorless message handling approach. These messages are sent directly to the message queue without being wrapped in the standard agent message format.

This modular approach makes it easy to add support for additional system types in the future.
