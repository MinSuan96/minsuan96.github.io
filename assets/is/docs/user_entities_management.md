---
Title: User Entities Management - Follow Server Tags Feature
Author: Teh Min Suan
Date: 28 January 2026
---

- [Overview](#overview)
  - [Key Concepts](#key-concepts)
    - [Tags](#tags)
    - [Subsystems](#subsystems)
    - [User-Server Mapping](#user-server-mapping)
  - [Server Entities Management](#server-entities-management)
    - [Server Tags Editor](#server-tags-editor)
    - [Follow Server Tags Checkbox](#follow-server-tags-checkbox)
      - [Behavior](#behavior)
      - [Persistence](#persistence)
  - [User Entities Management](#user-entities-management)
    - [User Tags Editor](#user-tags-editor)
      - [Restrictions](#restrictions)
  - [API Reference](#api-reference)
    - [Server Tag APIs](#server-tag-apis)
      - [`get_server_entities`](#get_server_entities)
      - [`update_server_entity`](#update_server_entity)
      - [`update_user_tag_with_server_tag`](#update_user_tag_with_server_tag)
    - [User Tag APIs](#user-tag-apis)
      - [`get_user_entities`](#get_user_entities)
      - [`update_user_entity`](#update_user_entity)
  - [Data Model](#data-model)
    - [User-Server Map Collection](#user-server-map-collection)
    - [Entity Card Collection (`visuals_entity_card`)](#entity-card-collection-visuals_entity_card)
  - [Background Job: visuals\_entity\_card](#background-job-visuals_entity_card)
    - [Tag Synchronization Flow](#tag-synchronization-flow)
  - [UI Components](#ui-components)
    - [Server Entities List](#server-entities-list)
    - [User Entities List](#user-entities-list)
  - [Examples](#examples)
    - [Users on the Same Server in Different Report Groups](#users-on-the-same-server-in-different-report-groups)
      - [Step 1: Create the Report Groups](#step-1-create-the-report-groups)
      - [Step 2: Ensure "Follow Server Tags" is Disabled](#step-2-ensure-follow-server-tags-is-disabled)
      - [Step 3: Assign Individual Tags to Each User](#step-3-assign-individual-tags-to-each-user)
      - [Result](#result)
      - [Contrast: Using Follow Server Tags](#contrast-using-follow-server-tags)
  - [Error Handling](#error-handling)

# Overview

The User Entities Management feature allows administrators to manage tags assigned to users across different subsystems (OS, DB, App). Tags are used to categorize users and associate them with report groups for compliance and monitoring purposes.

## Key Concepts

### Tags

- Tags are labels assigned to users and servers for categorization
- Every entity (user or server) is automatically assigned the `all` tag
- Tags determine which report groups a user belongs to

### Subsystems

- **OS**: Operating system users (Linux, Windows, Solaris)
- **DB**: Database users
- **App**: Application-specific users (custom subsystems)

### User-Server Mapping

Each user is mapped to the server(s) they have accessed. This mapping is stored in subsystem-specific collections:

- `os_user_server_map`
- `db_user_server_map`
- `<app>_user_server_map`

---

## Server Entities Management

### Server Tags Editor

The Server Tags Editor modal allows administrators to:

1. Add or remove tags from a server
2. Configure whether users on this server should follow the server's tags

### Follow Server Tags Checkbox

Located in the Server Tags Editor modal, there is a checkbox labeled:

> **"All users from this server follow this server's tags"**

#### Behavior

When **enabled**:

- All users associated with this server will automatically inherit the server's tags
- Users cannot manually edit their own tags (the User Tags Editor will display an error message)
- When server tags are updated, user tags are synchronized during the next `visuals_entity_card` job run
- The `follow_server_tags` field is set to `true` in the user-server mapping collection

When **disabled**:

- Users can have their own independent tags
- Users' tags are not affected by changes to the server's tags
- The `follow_server_tags` field is set to `false` in the user-server mapping collection

#### Persistence

The checkbox state is persisted in the database and will remain consistent when:

- Refreshing the page
- Navigating between pages in the server entities table
- Opening the modal for different servers

---

## User Entities Management

### User Tags Editor

The User Tags Editor modal allows administrators to add or remove tags from individual users.

#### Restrictions

If a user's server has **"Follow Server Tags"** enabled:

- The user cannot manually edit their tags
- An error message will be displayed: *"This user is configured to follow their server's tags."*
- To modify the user's tags, the administrator must either:
  1. Disable the "Follow Server Tags" option on the server, OR
  2. Edit the server's tags (which will propagate to all users on that server)

---

## API Reference

### Server Tag APIs

#### `get_server_entities`

Returns a list of all server entities with their tags and follow_server_tags status.

**Parameters:**

| Parameter | Type | Required | Description |
| ----------- | ------ | ---------- | ------------- |
| `tags` | String | No | Filter servers by tag |
| `reportGroup` | String | No | Filter servers by report group |
| `server` | String | No | Filter by server role/name |

**Response:**

```json
[
  {
    "sub_system": "OS",
    "role": "server-name",
    "tags": ["all", "production"],
    "report_groups": ["Daily Report"],
    "follow_server_tags": true
  }
]
```

#### `update_server_entity`

Updates the tags for a server entity.

**Parameters:**

| Parameter | Type | Required | Description |
| ----------- | ------ | ---------- | ------------- |
| `role` | String | Yes | Server role/name |
| `sub_system` | String | Yes | Subsystem (OS, DB, etc.) |
| `tags` | String | Yes | Comma-separated list of tags |

#### `update_user_tag_with_server_tag`

Enables or disables the "Follow Server Tags" feature for all users on a server.

**Parameters:**

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `role` | String | Yes | Server role/name |
| `sub_system` | String | Yes | Subsystem (OS, DB, etc.) |
| `enabled` | String | Yes | `"true"` or `"false"` |

---

### User Tag APIs

#### `get_user_entities`

Returns a list of all user entities with their tags.

**Response:**

```json
[
  {
    "username": "john.doe",
    "sub_system": "OS",
    "server": "server-name",
    "tags": ["all", "production"],
    "report_groups": ["Daily Report"]
  }
]
```

#### `update_user_entity`

Updates the tags for a user entity.

**Parameters:**

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `username` | String | Yes | Username |
| `sub_system` | String | Yes | Subsystem (OS, DB, etc.) |
| `server` | String | Yes | Server role/name |
| `tags` | String | Yes | Comma-separated list of tags |

**Error Response (when follow_server_tags is enabled):**

```json
{
  "err": true,
  "msg": "This user is configured to follow their server's tags."
}
```

---

## Data Model

### User-Server Map Collection

Each subsystem has a user-server map collection (e.g., `os_user_server_map`) with the following schema:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `user` | String | Username |
| `server` | String | Server role/name |
| `server_tags` | Array | Tags assigned to the server |
| `follow_server_tags` | Boolean | Whether user follows server tags |

### Entity Card Collection (`visuals_entity_card`)

| Field | Type | Description |
| ----- | ---- | ----------- |
| `entity` | String | User or server name |
| `sub_system` | String | Subsystem (OS, DB, etc.) |
| `user_or_server` | String | Entity type (`user` or `server`) |
| `type` | String | Entity type (duplicate for compatibility) |
| `tags` | Array | List of assigned tags |
| `risk_score` | Number | Current risk score |
| `past_risk_score` | Array | Historical risk scores |

---

## Background Job: visuals_entity_card

The `visuals_entity_card.rb` script runs periodically (every 5 minutes) to:

1. **Populate user-server mappings**: Creates entries in the user-server map collection for each user-server relationship
2. **Sync server tags**: Updates the `server_tags` field in user-server mappings
3. **Apply follow_server_tags**: For users with `follow_server_tags: true`, copies the server's tags to the user's entity card

### Tag Synchronization Flow

```flowchart
Server tags updated
        ↓
visuals_entity_card job runs
        ↓
Updates server_tags in user-server map
        ↓
For users with follow_server_tags=true:
        ↓
Copies server_tags to user's entity card
```

---

## UI Components

### Server Entities List

**File:** `settings_server_entities_list/`

| Component | Description |
| --------- | ----------- |
| `ServerEntitiesList.vue` | Main container component |
| `ServerEntitiesListTable.vue` | Table displaying server entities |
| `ServerEntitiesActionTableCell.vue` | Edit action cell with modal trigger |
| `TagsEditor/TagsEditor.vue` | Modal for editing server tags |

### User Entities List

**File:** `settings_user_entities_list/`

| Component | Description |
| ----------- | ------------- |
| `UserEntitiesList.vue` | Main container component |
| `UserEntitiesListTable.vue` | Table displaying user entities |
| `TagsEditor/TagsEditor.vue` | Modal for editing user tags |

---

## Examples

### Users on the Same Server in Different Report Groups

This example demonstrates how two users on the same server can each belong to a different report group, with neither user appearing in the other's group.

**Scenario:** `web-server-01` has two OS users — `alice` and `bob`. Alice belongs to the finance team and Bob belongs to HR. Each team has its own report group, and each user should appear in only their respective group.

#### Step 1: Create the Report Groups

In **Settings → Report Groups**, create two report groups with distinct tags:

| Report Group | Tag |
| ------------ | --- |
| Finance Report | `finance` |
| HR Report | `hr` |

Each report group is associated with a tag. Users who carry that tag will be included in the corresponding report group.

#### Step 2: Ensure "Follow Server Tags" is Disabled

Open the **Server Tags Editor** for `web-server-01` and verify that the **"All users from this server follow this server's tags"** checkbox is **unchecked**.

This allows each user to maintain independent tags rather than inheriting the server's tags.

> If "Follow Server Tags" is enabled, all users on the server share the same tags and will appear in the same report groups. Disable it first before assigning individual user tags.

#### Step 3: Assign Individual Tags to Each User

Open the **User Tags Editor** for each user and assign their respective tags:

| Username | Server | Tags | Resulting Report Groups |
| -------- | ------ | ---- | ----------------------- |
| `alice` | `web-server-01` | `all`, `finance` | Finance Report |
| `bob` | `web-server-01` | `all`, `hr` | HR Report |

Both users share the mandatory `all` tag but differ in their department tag, which determines their report group membership.

#### Result

After saving:

- `alice` appears **only** in the **Finance Report** group
- `bob` appears **only** in the **HR Report** group
- Neither user appears in the other's report group
- Both users remain under `web-server-01` in the User Entities List

The `get_user_entities` API will reflect this:

```json
[
  {
    "username": "alice",
    "sub_system": "OS",
    "server": "web-server-01",
    "tags": ["all", "finance"],
    "report_groups": ["Finance Report"]
  },
  {
    "username": "bob",
    "sub_system": "OS",
    "server": "web-server-01",
    "tags": ["all", "hr"],
    "report_groups": ["HR Report"]
  }
]
```

#### Contrast: Using Follow Server Tags

If instead "Follow Server Tags" were **enabled** on `web-server-01` with tags `["all", "finance", "hr"]`, both `alice` and `bob` would inherit those tags and appear in **both** Finance Report and HR Report. Individual tag assignment is the correct approach when users on the same server need to belong to different report groups.

---

## Error Handling

| Scenario | Error Message |
| -------- | ------------- |
| User tries to edit tags when follow_server_tags is enabled | "This user is configured to follow their server's tags." |
| Network error during save | "Changes not saved due to network error, please try again later." |
| Failed to update follow_server_tags setting | "Failed to update setting, please try again later." |
