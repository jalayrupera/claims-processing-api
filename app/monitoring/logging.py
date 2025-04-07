import json
import logging
import os
import sys
import uuid

import requests
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings


class LokiHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}/loki/api/v1/push"
        self.buffer = []
        self.max_buffer_size = 100

    def emit(self, record):
        try:
            log_entry = json.loads(self.format(record))

            labels = {
                "level": record.levelname.lower(),
                "logger": record.name,
                "application": "api",
            }

            for key in [
                "request_id",
                "method",
                "path",
                "status_code",
                "client_ip",
                "user_id",
            ]:
                if key in log_entry:
                    labels[key] = str(log_entry[key])

            ts_ns = int(record.created * 1_000_000_000)
            loki_payload = {
                "streams": [
                    {"stream": labels, "values": [[str(ts_ns), json.dumps(log_entry)]]}
                ]
            }

            self.buffer.append(loki_payload)

            if len(self.buffer) >= self.max_buffer_size:
                self.flush()

        except Exception as e:
            print(f"Error formatting log for Loki: {str(e)}")

    def flush(self):
        if not self.buffer:
            return

        combined_payload = {"streams": []}
        for payload in self.buffer:
            combined_payload["streams"].extend(payload["streams"])

        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.url, headers=headers, json=combined_payload)
            if response.status_code >= 400:
                print(f"Error sending logs to Loki: {response.text}")
        except Exception as e:
            print(f"Exception sending logs to Loki: {str(e)}")

        self.buffer = []


def setup_logging_handler():
    handler = LokiHandler(host=settings.LOKI_HOST, port=settings.LOKI_PORT)
    return handler


class LokiProcessor:
    def __call__(self, logger, method_name, event_dict):
        return event_dict


def request_id_processor(_, __, event_dict):
    event_dict["request_id"] = str(uuid.uuid4())
    return event_dict


def setup_logging():
    log_dir = "/var/log/api"
    os.makedirs(log_dir, exist_ok=True)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            request_id_processor,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    file_handler = logging.FileHandler(f"{log_dir}/api.log")
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str):
    return structlog.get_logger(name)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("api")

    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())

        self.logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host,
        )

        try:
            response = await call_next(request)

            self.logger.info(
                "request_completed",
                request_id=request_id,
                status_code=response.status_code,
            )

            return response
        except Exception as e:
            self.logger.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
