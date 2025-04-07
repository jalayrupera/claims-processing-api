import argparse
import datetime
import json
import uuid
from pathlib import Path

# Define the target log file relative to the script location
LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "api.log"


def generate_log_entry(level: str, message: str, logger_name: str) -> str:
    """Generates a single log entry string in the expected JSON format."""
    log_entry = {
        "log": message,
        "event": message,
        "level": level.lower(),
        "logger": logger_name,
        # Use ISO format timestamp similar to structlog's default
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        # Add a unique request_id like the middleware does
        "request_id": str(uuid.uuid4()),
        # Add a marker to easily identify generated logs
        "source": "fake_log_generator",
        "error": {"message": message},
    }
    return json.dumps(log_entry)


def main():
    parser = argparse.ArgumentParser(description="Generate fake JSON logs for the API.")
    parser.add_argument(
        "--level",
        type=str,
        required=True,
        choices=[
            "info",
            "warning",
            "error",
            "critical",
            "fatal",
        ],  # fatal maps to critical
        help="Log level (info, warning, error, critical, fatal).",
    )
    parser.add_argument(
        "--message",
        type=str,
        default="This is a generated test log message.",
        help="The log message content.",
    )
    parser.add_argument(
        "--count", type=int, default=1, help="Number of log entries to generate."
    )
    parser.add_argument(
        "--logger",
        type=str,
        default="fake_generator",
        help="Name to use for the 'logger' field.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=str(LOG_FILE),
        help=f"Path to the log file to append to (default: {LOG_FILE}).",
    )

    args = parser.parse_args()

    log_level = args.level.lower()
    # Map 'fatal' to 'critical' if used
    if log_level == "fatal":
        log_level = "critical"

    log_file_path = Path(args.file)
    log_dir = log_file_path.parent

    # Ensure the log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(log_file_path, "a") as f:
            for i in range(args.count):
                log_line = generate_log_entry(log_level, args.message, args.logger)
                f.write(log_line + "\n")
                print(f"Appended log {i + 1}/{args.count} to {log_file_path}")
        print(f"Successfully generated {args.count} log entries.")
    except Exception as e:
        print(f"Error writing to log file {log_file_path}: {e}")
        exit(1)


if __name__ == "__main__":
    main()
