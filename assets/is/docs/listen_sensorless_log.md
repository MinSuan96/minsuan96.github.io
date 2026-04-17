---
Title: Listen Sensorless Log
Author: Teh Min Suan
Date: 15 May 2025
---

- [Overview](#overview)
- [Purpose](#purpose)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
  - [Data Flow](#data-flow)
  - [Agent Management](#agent-management)
- [Implementation Details](#implementation-details)
  - [Key Components](#key-components)
  - [Message Processing Pipeline](#message-processing-pipeline)
- [Usage](#usage)
  - [Integration Requirements](#integration-requirements)
  - [Extending Functionality](#extending-functionality)
  - [Configuration](#configuration)
- [Development](#development)
  - [Adding New Source Types](#adding-new-source-types)
- [Troubleshooting](#troubleshooting)
- [Conclusion](#conclusion)


## Overview

The `listen_sensorless_log.py` script is a critical component of the sensorless log processing pipeline. It's designed to receive log messages from various data sources that don't have traditional sensors attached to them, process these messages, and route them to appropriate destinations for further analysis.

## Purpose

This script serves as a bridge between raw sensorless log sources and the main log processing infrastructure. It:

1. Consumes messages from a dedicated RabbitMQ exchange
2. Processes and normalizes the incoming data
3. Associates the data with appropriate agent IDs
4. Routes the processed data to standard log processing channels
5. Manages agent initialization and tracking

## Architecture

The script integrates with:

- **RabbitMQ**: For message queuing and routing
- **MongoDB**: For persistent storage of agent information and customer preferences
- **Grok**: For pattern matching and data extraction

## How It Works

### Data Flow

1. External connectors send sensorless logs to the `received_sensorless_log` RabbitMQ exchange
2. The script consumes these messages using a queue bound to this exchange
3. Each message is processed to extract source information and determine a scalable role
4. An agent ID is either retrieved or created for the identified role
5. The processed message is forwarded to the `received_log` exchange with an updated routing key that includes the agent ID

### Agent Management

The script maintains agent information in MongoDB:

- Tracks which agents are associated with which roles
- Manages agent types (normal, shared, or auto-scaling)
- Updates "last active" timestamps for agents
- Handles initialization of new agents when previously unseen data sources appear

## Implementation Details

### Key Components

- **Initialization Functions**: Set up connections to RabbitMQ and MongoDB
- **Message Processing**: Extract relevant data and determine routing
- **Agent Management**: Create and update agent information
- **Background Thread**: Periodically update agent activity timestamps

### Message Processing Pipeline

When a message arrives:

1. The source type is extracted from the routing key
2. The `process_source_type()` function extracts identifying information from the message
3. An agent ID is obtained via the `get_agent()` function
4. The `process_body()` function handles the actual routing based on the message type

## Usage

### Integration Requirements

To integrate a new sensorless data source with this system:

1. Configure your connector/listener to send logs to the `received_sensorless_log` RabbitMQ exchange
2. Use appropriate routing keys to identify the source type (e.g., `azure_sql`, `aurora`, `rds`)
3. Ensure your message format is compatible with the processing logic

### Extending Functionality

To add support for new data sources:

1. Update the `SOURCE_TYPE` dictionary with the new source type
2. Add a corresponding Grok pattern in the `initialize_grok()` function
3. Implement specific processing logic in the `process_source_type()` function
4. Update the `process_body()` function to handle the new routing key pattern

### Configuration

The script uses several constants that can be adjusted:

- `AGENT_ACTIVE_UPDATE_INTERVAL`: How often to update agent activity (default: 60 seconds)
- `MAX_RESTART_HISTORY`: Number of restart events to track per agent (default: 5)
- `MSG_TTL_MS`: Message time-to-live in milliseconds (default: 10 minutes)
- `MAX_QUEUE_LENGTH`: Maximum number of messages in the queue (default: 10,000)

## Development

### Adding New Source Types

To implement processing for a new source type:

1. Add a new Grok pattern in `initialize_grok()`:

   ```python
   grok_patterns = {
       'existing_patterns': ...,
       'new_source_type': Grok(r'your_pattern_here')
   }
   ```

2. Update the `process_source_type()` function to handle the new source type:

   ```python
   elif source_type == 'new_source_type':
       # Extract scalable_role from the data
       scalable_role = extract_role_from_data(data)
   ```

3. Update the `process_body()` function to handle routing for the new source type:

   ```python
   elif 'new_source_type' in routing_key:
       # Process and route the message
       pika_channel_out.basic_publish(
           exchange=PIKA_EXCHANGE_OUT,
           routing_key=routing_key,
           body=process_the_body(body)
       )
   ```

## Troubleshooting

Common issues:

- Messages not being routed: Check that source connectors are using correct exchange and routing keys
- Missing agent IDs: Verify MongoDB connection and agent initialization process
- Pattern matching failures: Review Grok patterns against actual message formats

## Conclusion

The `listen_sensorless_log.py` script provides a flexible framework for incorporating sensorless data sources into the log processing pipeline. By standardizing the intake, processing, and routing of these logs, it enables consistent handling and analysis of data from diverse sources.
