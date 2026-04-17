---
Title: Storage Estimator Documentation
Author: Teh Min Suan
Date: 26 March 2025
---

- [Overview](#overview)
- [Dependencies](#dependencies)
- [Components](#components)
  - [storage\_estimator.py](#storage_estimatorpy)
  - [StorageEstimator.vue](#storageestimatorvue)
  - [Data Structure](#data-structure)
  - [API Endpoints](#api-endpoints)
  - [Error Handling](#error-handling)
  - [Usage](#usage)

## Overview

The Storage Estimator is a monitoring tool that tracks and predicts storage usage for MongoDB and Elasticsearch databases. It provides visual representations of historical storage usage and estimates when storage capacity might be reached based on current growth patterns.

- Uses Chart.js for visualizations
- Shows up to 30-day history of storage usage
- Provides weekly estimations one year in advance

## Dependencies

The following dependencies are required to run the Storage Estimator:

- `python`>=3.10
- `scikit-learn`>=1.3.0
- `numpy`>=1.19.5
- `elasticsearch`>=8.0.0
- `apscheduler`>=3.6.0
- `chart.js`>=3.0.0
- `rubymarshal`>=0.8.0

Note: The dependencies are listed in the `requirements3.txt` file and `package.json` file. Lower versions of the dependencies might work, but they are not tested.

## Components

### storage_estimator.py

The `storage_estimator.py` module is responsible for collecting and estimating storage usage data from MongoDB and Elasticsearch databases. It has the following properties:

- Runs daily at 1:00 AM
- Collects statistics from MongoDB and Elasticsearch databases
- Uses linear regression to estimate future storage usage
- Stores the data in `db.storage_stats`

### StorageEstimator.vue

The `StorageEstimator.vue` component is a Vue.js component that displays the storage usage data and estimates in a chart. It includes the following features:

- Separate sections for MongoDB and Elasticsearch
- Real-time updates every 5 minutes
- Line charts showing color-coded for different metrics:
  - Red: Total storage
  - Blue: Used storage
  - Green: Available storage
  - Dashed Blue: Estimated usage
  - Dashed Green: Estimated available storage
- Days to full capacity
- Date formatting on x-axis
- Storage values in GB on y-axis

### Data Structure

The `db.storage_stats` collection has the following structure:

```json
{
  "type": "mongo"|"elasticsearch",
  "total_storage": number,
  "used_storage": {
    "epoch_time": number,
  },
  "estimated_days_to_full": number,
  "estimation": {
    "epoch_time": number,
  }
}
```

### API Endpoints

The frontend communicates with the backend using the following API endpoints:

```http
GET /settings_storage_estimator
  ?action=get_graph_data
  &type=[mongo|elasticsearch]    // Returns storage usage and prediction data

GET /settings_storage_estimator
  ?action=get_days_to_full
  &type=[mongo|elasticsearch]    // Returns estimated days until storage is full
```

### Error Handling

The system includes several error handling mechanisms:

- Displays "Insufficient data" message when less than 2 data points are available
- Graceful handling of API failures
- Cleanup of chart instances to prevent memory leaks
- Fallback to zero values when data is unavailable

### Usage

To use the Storage Estimator, navigate to the Storage Estimator page in the settings menu.
