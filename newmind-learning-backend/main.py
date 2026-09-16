"""HTTP entrypoint for the NewMind backend container.

This module intentionally exposes a small backend health/status service without
serving the React frontend. The frontend lives in `newmind-learning-frontend/`
and will get its own Docker service.
"""

from __future__ import annotations

import json
import logging
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from config.settings import settings
from storage.oci_client import oci_storage


logger = logging.getLogger(__name__)


def build_health_payload() -> dict[str, Any]:
    """Return runtime health metadata for container checks."""
    return {
        "status": "ok",
        "service": "newmind-learning-backend",
        "environment": settings.APP_ENV,
        "oci_mode": "emulated" if oci_storage.is_emulated else "oci",
        "oci_namespace": oci_storage.namespace,
        "chroma_persist_dir": settings.CHROMA_PERSIST_DIR,
    }


class BackendRequestHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for backend status endpoints."""

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/health"}:
            self._write_json(HTTPStatus.OK, build_health_payload())
            return

        self._write_json(
            HTTPStatus.NOT_FOUND,
            {
                "status": "not_found",
                "message": "Use /health to check backend container status.",
            },
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        logger.info("%s - %s", self.address_string(), format % args)

    def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    """Start the backend HTTP entrypoint."""
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    server = ThreadingHTTPServer((host, port), BackendRequestHandler)
    logger.info("Starting backend entrypoint on %s:%s", host, port)
    server.serve_forever()


if __name__ == "__main__":
    run()
