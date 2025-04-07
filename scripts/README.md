# API Error Log Generation Scripts

These scripts are designed to generate fake API error logs that can be used to test monitoring and alerting systems. They're useful for simulating production incidents and testing your alert configuration.

## Setup

Ensure you have Python 3 installed with the required packages:

```bash
pip install requests
```

## Scripts Overview

### 1. generate_error_logs.py

This script generates fake API error logs and outputs them to standard output. Useful for local testing or when you need logs in plain text format.

**Usage:**

```bash
./generate_error_logs.py [OPTIONS]
```

**Options:**

- `-n, --num-entries`: Number of log entries to generate (default: 100)
- `-i, --interval`: Interval between logs in seconds (default: 0.1)
- `-t, --error-type`: Type of errors to generate (choices: 4xx, 5xx, both; default: both)
- `-u, --target-url`: Optional URL to send logs to

**Example:**

```bash
# Generate 200 mixed error logs with 0.05s interval
./generate_error_logs.py -n 200 -i 0.05
```

### 2. flood_loki_with_errors.py

This script generates fake API error logs and sends them directly to Loki with the proper labels for alerting. This is the preferred script for testing Prometheus/Loki alerts.

**Usage:**

```bash
./flood_loki_with_errors.py [OPTIONS]
```

**Options:**

- `-n, --num-entries`: Number of log entries to generate (default: 100)
- `-b, --batch-size`: Batch size for sending logs to Loki (default: 10)
- `-i, --interval`: Interval between batches in seconds (default: 0.5)
- `-t, --error-type`: Type of errors to generate (choices: 4xx, 5xx, both; default: 5xx)
- `-u, --loki-url`: Loki push API URL (default: http://localhost:3100/loki/api/v1/push)

**Example:**

```bash
# Generate 500 5xx errors in batches of 20 with 0.1s interval
./flood_loki_with_errors.py -n 500 -b 20 -i 0.1 -t 5xx
```

## Triggering Email Alerts

To trigger email alerts configured in Prometheus/Alertmanager, use the `flood_loki_with_errors.py` script with a high volume of errors:

```bash
# Generate enough 5xx errors to trigger the High5xxErrors alert
./flood_loki_with_errors.py -n 1000 -b 50 -i 0.1 -t 5xx
```

This will generate a high rate of server errors, which should trigger the following alerts:
- High5xxErrors: Triggered when error rate exceeds 5 errors per second over 2 minutes
- High4xxErrors: Triggered when warning rate exceeds 10 errors per second over 5 minutes (if using error-type 4xx)

## Simulating Different Scenarios

You can use these scripts to simulate different error scenarios:

1. **Sudden spike in errors:**
   ```bash
   ./flood_loki_with_errors.py -n 500 -b 100 -i 0.05 -t 5xx
   ```

2. **Sustained lower-level errors:**
   ```bash
   ./flood_loki_with_errors.py -n 2000 -b 10 -i 0.5 -t 5xx
   ```

3. **Mix of client and server errors:**
   ```bash
   ./flood_loki_with_errors.py -n 1000 -b 50 -i 0.1 -t both
   ```

4. **Client-side errors only:**
   ```bash
   ./flood_loki_with_errors.py -n 1000 -b 50 -i 0.1 -t 4xx
   ```

## Integration with Monitoring Stack

These scripts are designed to work with our Prometheus, Loki, and Grafana monitoring stack. The logs are sent with the correct labels and format to be properly visualized in Grafana dashboards and to trigger Prometheus alerts. 