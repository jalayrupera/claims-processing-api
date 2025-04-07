#!/usr/bin/env python3
import argparse
import json
import random
import time
from datetime import datetime

import requests

# Loki push API endpoint
LOKI_URL = "http://localhost:3100/loki/api/v1/push"

# List of API endpoints to simulate
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/api/payments",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/search",
    "/api/settings",
    "/api/notifications",
    "/api/metrics",
]

# List of HTTP methods
METHODS = ["GET", "POST", "PUT", "DELETE"]

# Status code distributions
ERROR_STATUS_CODES = {
    "4xx": [400, 401, 403, 404, 429],  # Client errors
    "5xx": [500, 501, 502, 503, 504],  # Server errors
}


def generate_log_entry(error_type="5xx"):
    """Generate a fake log entry with error status code"""
    method = random.choice(METHODS)
    path = random.choice(ENDPOINTS)
    request_id = f"req-{random.randint(100000, 999999)}"

    if error_type == "4xx":
        status = random.choice(ERROR_STATUS_CODES["4xx"])
        level = "warning"
    elif error_type == "5xx":
        status = random.choice(ERROR_STATUS_CODES["5xx"])
        level = "error"
    else:
        status = random.choice(ERROR_STATUS_CODES["4xx"] + ERROR_STATUS_CODES["5xx"])
        level = "error" if status >= 500 else "warning"

    response_time = random.randint(50, 2000)

    # Create the log entry in JSON format that mimics the application logs
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    log_data = {
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status,
        "response_time_ms": response_time,
        "logger": "api",
        "level": level,
        "timestamp": timestamp,
        "event": "request_completed",
    }

    log_line = json.dumps(log_data)

    return {
        "log_line": log_line,
        "timestamp": int(time.time() * 1e9),  # Nanosecond timestamp for Loki
        "level": level,
        "status": status,
    }


def send_to_loki(log_entries, loki_url=LOKI_URL):
    """Send log entries to Loki"""
    # Group entries by level for proper labels
    entries_by_level = {}
    for entry in log_entries:
        level = entry["level"]
        if level not in entries_by_level:
            entries_by_level[level] = []
        entries_by_level[level].append(entry)

    streams = []
    for level, entries in entries_by_level.items():
        streams.append(
            {
                "stream": {
                    "job": "api",
                    "level": level,
                    "filename": "/var/log/api/api.log",
                },
                "values": [
                    [str(entry["timestamp"]), entry["log_line"]] for entry in entries
                ],
            }
        )

    payload = {"streams": streams}

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(loki_url, headers=headers, data=json.dumps(payload))
        if response.status_code >= 400:
            print(
                f"Error sending logs to Loki: {response.status_code} - {response.text}"
            )
        return response.status_code < 400
    except Exception as e:
        print(f"Exception while sending logs to Loki: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate and send error logs to Loki")
    parser.add_argument(
        "-n",
        "--num-entries",
        type=int,
        default=100,
        help="Number of log entries to generate",
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for sending logs to Loki",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=0.5,
        help="Interval between batches in seconds",
    )
    parser.add_argument(
        "-t",
        "--error-type",
        choices=["4xx", "5xx", "both"],
        default="5xx",
        help="Type of errors to generate",
    )
    parser.add_argument("-u", "--loki-url", default=LOKI_URL, help="Loki push API URL")
    args = parser.parse_args()

    print(
        f"Sending {args.num_entries} error logs of type '{args.error_type}' to Loki at {args.loki_url}"
    )
    print(
        f"Using batch size of {args.batch_size} with {args.interval}s interval between batches"
    )

    batches = args.num_entries // args.batch_size
    remaining = args.num_entries % args.batch_size

    for i in range(batches):
        batch_entries = [
            generate_log_entry(args.error_type) for _ in range(args.batch_size)
        ]
        success = send_to_loki(batch_entries, args.loki_url)

        if success:
            print(f"Sent batch {i + 1}/{batches} ({args.batch_size} logs)")
        else:
            print(f"Failed to send batch {i + 1}/{batches}")

        if (
            i < batches - 1 or remaining > 0
        ):  # Don't sleep after the last batch if no remaining
            time.sleep(args.interval)

    # Send remaining entries if any
    if remaining > 0:
        batch_entries = [generate_log_entry(args.error_type) for _ in range(remaining)]
        success = send_to_loki(batch_entries, args.loki_url)

        if success:
            print(f"Sent final batch ({remaining} logs)")
        else:
            print("Failed to send final batch")

    print(f"Completed sending {args.num_entries} error logs to Loki")


if __name__ == "__main__":
    main()
