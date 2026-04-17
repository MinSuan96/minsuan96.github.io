---
Title: XML Forwarder Documentation
Author: Teh Min Suan
Date: 20 December 2024
---

- [Overview](#overview)
- [xml\_forwarder.py](#xml_forwarderpy)
  - [Description](#description)
  - [Modules](#modules)
  - [Functions](#functions)
  - [Classes](#classes)
  - [How It Works](#how-it-works)
  - [Usage](#usage)
- [xml\_forwarder\_dbconfig.py](#xml_forwarder_dbconfigpy)
  - [Description](#description-1)
  - [Modules](#modules-1)
  - [Functions](#functions-1)
  - [Usage](#usage-1)
    - [Example](#example)
- [Winevent.cpp](#wineventcpp)
  - [Description](#description-2)
  - [Modules](#modules-2)
  - [Functions](#functions-2)
    - [Initialization](#initialization)
    - [Event Log Reading](#event-log-reading)
    - [Message Formatting](#message-formatting)
    - [Base64 Encoding](#base64-encoding)
    - [Forwarding](#forwarding)
  - [How It Works](#how-it-works-1)
  - [Usage](#usage-2)
    - [Example](#example-1)

## Overview

The XML Forwarder system consists of three main scripts: `xml_forwarder.py`, `xml_forwarder_dbconfig.py`, and `winevent.cpp`. Together, these scripts facilitate the collection, processing, and forwarding of XML logs from various sources to specified targets.

- **xml_forwarder.py**: This script consumes messages from a RabbitMQ queue, processes them, and forwards them to specified targets. It handles the initialization of RabbitMQ connections, logging, pattern matching, and sender configurations. The script is designed to manage and forward XML logs efficiently.

- **xml_forwarder_dbconfig.py**: This script manages the database configuration for the XML Forwarder. It interacts with MongoDB to retrieve and update configuration settings, ensuring that the XML Forwarder has the necessary information to operate correctly.

- **winevent.cpp**: This C++ script reads and processes Windows Event Logs. It captures event log entries, formats them, encodes them in Base64, and forwards them to the XML Forwarder. The program supports different versions of Windows, including XP, Vista, and newer versions.

Together, these scripts provide a comprehensive solution for handling XML logs, from capturing and processing event logs on Windows systems to forwarding them to designated targets for further analysis and storage.

## xml_forwarder.py

### Description

This script is responsible for consuming messages from a RabbitMQ queue, processing them, and forwarding them to specified targets. It uses various modules for handling different tasks such as logging, message parsing, and network communication.

### Modules

- `socket`: Provides access to the BSD socket interface.
- `env_helper`: Custom module for environment-specific helper functions.
- `logging`: Provides a flexible framework for emitting log messages from Python programs.
- `os`: Provides a way of using operating system dependent functionality.
- `msgpack`: Provides MessagePack (de)serialization.
- `pygrok`: Provides Grok pattern matching.
- `pybase64`: Provides Base64 encoding and decoding.

### Functions

- `initialize_pika()`: Initializes the RabbitMQ connection and channel, declares the exchange and queue, and binds the queue to routing keys.
- `terminate_pika()`: Closes the RabbitMQ channel and connection.
- `initialize_logger()`: Initializes the logger using the environment helper.
- `terminate_logger()`: Shuts down the logger.
- `initialize_pattern()`: Initializes the Grok pattern for parsing message headers.
- `initialize_targets()`: Initializes the targets from the MongoDB configuration.
- `initialize_senders_array()`: Initializes the array of senders based on the targets.
- `initialize_sender(target, identifier)`: Initializes a sender for a given target.
- `onExit()`: Terminates Pika and logger, then exits the program.
- `onMessage(_ch, _method, _properties, msg)`: Callback function for processing messages from the RabbitMQ queue.
- `parse_payload(payload)`: Parses and decodes the payload from the message.

### Classes

- `SfTcpSyslogHandler`: Custom SysLogHandler to handle TCP syslog messages without appending a null character.

### How It Works

1. **Initialization**: The script initializes various components such as RabbitMQ connection, logger, Grok pattern, and targets from MongoDB.
2. **Message Consumption**: It consumes messages from the RabbitMQ queue using the `onMessage` callback function.
3. **Message Processing**: The `onMessage` function processes the messages by parsing the payload and extracting relevant information.
4. **Forwarding**: The processed messages are then forwarded to the specified targets using the initialized senders.

### Usage

Run the script to start consuming messages from the RabbitMQ queue and forwarding them to the specified targets.

## xml_forwarder_dbconfig.py

### Description

This script is responsible for managing the database configuration for the XML Forwarder. It interacts with MongoDB to retrieve and update the configuration settings for the XML Forwarder.

### Modules

- `pymongo`: Provides tools for working with MongoDB.
- `env_helper`: Custom module for environment-specific helper functions.

### Functions

- `get_db_config()`: Retrieves the database configuration for the XML Forwarder from MongoDB.
- `update_db_config(config)`: Updates the database configuration for the XML Forwarder in MongoDB.

### Usage

Use this script to manage the database configuration for the XML Forwarder. It allows you to retrieve and update the configuration settings stored in MongoDB.

#### Example

To run the XML Forwarder, execute the `xml_forwarder.py` script. Ensure that the database configuration is properly set up using the `xml_forwarder_dbconfig.py` script.

```bash
To add a new configuration:
python xml_forwarder_dbconfig.py --action add --ip_address 192.168.1.1 --port 8080 --socket_type TCP

To delete an existing configuration:
python xml_forwarder_dbconfig.py --action delete --ip_address 192.168.1.1 --port 8080 --socket_type TCP

To check the current configurations:
python xml_forwarder_dbconfig.py --action check
```

## Winevent.cpp

### Description

`winevent.cpp` is a part of the sensor's code designed to read and process Windows Event Logs. It captures event log entries, processes them, and forwards them to a specified destination. The program supports different versions of Windows, including XP, Vista, and newer versions.

### Modules

- `stdafx.h`: Precompiled header file.
- `main.h`: Main header file.
- `log.h`: Header file for logging functions.
- `b64.h`: Header file for Base64 encoding functions.
- `winevent.h`: Header file for Windows Event Log functions.
- `log_forward.h`: Header file for log forwarding functions.
- `lastlogforward.h`: Header file for last log forwarding functions.

### Functions

#### Initialization

- `initWinEvent()`: Initializes event log handles and registry keys for reading event logs.

#### Event Log Reading

- `EventLogReaderXP()`: Reads and processes event log entries for Windows XP and 2003.
- `EventLogReaderVista()`: Reads and processes event log entries for Windows Vista and newer versions.
- `SeekToLastRecord()`: Seeks to the last record in the event log.
- `ReadRecord()`: Reads a single record from the event log.
- `GetLastRecordNumber()`: Gets the record number of the last record in the event log.

#### Message Formatting

- `EventIDTemplate()`: Formats event log messages using metadata and message templates.
- `GetMessageString()`: Retrieves the message string for an event log entry.
- `LoadMessageFilePaths()`: Loads message file paths from the registry.
- `AllocFormatMessage()`: Allocates memory for formatted messages.
- `LoadMessages()`: Loads messages from message files.
- `GetMaxPlaceHolder()`: Gets the maximum placeholder value in a message template.
- `ReplaceStrings()`: Replaces placeholders in a message template with actual values.
- `ReplaceParameters()`: Replaces placeholders in a message template with parameter strings.
- `ConcatStrings()`: Concatenates strings in an event log record.

#### Base64 Encoding

- `ToBase64Crypto()`: Encodes data in Base64 format using the `CryptBinaryToStringA` function.

#### Forwarding

- `processEvtConf()`: Processes event configuration.
- `Start_WinEventCapture()`: Starts capturing Windows Event Logs and forwarding them.

### How It Works

1. **Initialization**: The program initializes event log handles and registry keys for reading event logs.
2. **Event Log Reading**: It reads event log entries using the `ReadEventLog` function for raw format and the `EvtQuery` and `EvtNext` functions for XML format.
3. **Message Formatting**: The `EventIDTemplate` function formats event log messages using metadata and message templates. It retrieves the message template from the event log provider's metadata and formats the message accordingly.
4. **Base64 Encoding**: The `ToBase64Crypto` function encodes event log data in Base64 format using the `CryptBinaryToStringA` function.
5. **Forwarding**: The `processEvtConf` function processes event configuration, and the `Start_WinEventCapture` function starts capturing Windows Event Logs and forwarding them.

### Usage

Add XML forwarding to the sensor. Ensure that `agent_config` is configured with the `[extra_winevent_format]` section to use XML forwarding.

#### Example

To enable forwarding of `win_events`, `share_events` and `sys_events` in XML format, configure `agent_config` as follows:

```ini
[logs]
win_events_xml = C:\cgagent\logs\sec_xml.log
share_events_xml = C:\cgagent\logs\share_xml.log
sys_events_xml = C:\cgagent\logs\sys_xml.log

[winevent_security]
win_events_xml = 4740,4728,4732,4756,4720,4722,4735,4625,4648,4624,4634,1102,4768,4769,4672,4725,4698,4699
share_events_xml = 5140,5142,5143,5144,5145

[winevent_system]
sys_events_xml = 7040,7045,104,1074

[extra_winevent_format]
win_events_xml = xml
share_events_xml = xml
sys_events_xml = xml
```
