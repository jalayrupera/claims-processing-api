#!/usr/bin/env python3
import argparse
import logging
import random
import time
from datetime import datetime

import requests

# Configure logging
logging.basicConfig(
    format='[%(asctime)s] "%(method)s %(path)s HTTP/1.1" %(status)d %(response_time)d ms',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# Set up custom logger
logger = logging.getLogger("api-error-generator")

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


def generate_log_entry(error_type="5xx", method=None):
    """Generate a fake log entry with error status code"""
    if method is None:
        method = random.choice(METHODS)

    path = random.choice(ENDPOINTS)

    if error_type == "4xx":
        status = random.choice(ERROR_STATUS_CODES["4xx"])
    elif error_type == "5xx":
        status = random.choice(ERROR_STATUS_CODES["5xx"])
    else:
        status = random.choice(ERROR_STATUS_CODES["4xx"] + ERROR_STATUS_CODES["5xx"])

    response_time = random.randint(50, 2000)

    # Log the entry
    log_dict = {
        "method": method,
        "path": path,
        "status": status,
        "response_time": response_time,
    }

    logger.info("", extra=log_dict)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "path": path,
        "status": status,
        "response_time": response_time,
    }


def send_to_api(log_entry, target_url=None):
    """Send the log entry to a target URL if provided"""
    if target_url:
        try:
            requests.post(target_url, json=log_entry, timeout=1)
        except requests.RequestException:
            pass


def main():
    parser = argparse.ArgumentParser(description="Generate fake API error logs")
    parser.add_argument(
        "-n",
        "--num-entries",
        type=int,
        default=100,
        help="Number of log entries to generate",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=0.1,
        help="Interval between logs in seconds",
    )
    parser.add_argument(
        "-t",
        "--error-type",
        choices=["4xx", "5xx", "both"],
        default="both",
        help="Type of errors to generate",
    )
    parser.add_argument("-u", "--target-url", help="Optional URL to send logs to")
    args = parser.parse_args()

    print(
        f"Generating {args.num_entries} error logs of type '{args.error_type}' with {args.interval}s interval"
    )

    for i in range(args.num_entries):
        log_entry = generate_log_entry(args.error_type)

        if args.target_url:
            send_to_api(log_entry, args.target_url)

        if i < args.num_entries - 1:  # Don't sleep after the last entry
            time.sleep(args.interval)

    print(f"Generated {args.num_entries} error logs")


if __name__ == "__main__":
    main()
