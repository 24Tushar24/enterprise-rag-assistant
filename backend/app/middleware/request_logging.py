import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        request_id = str(uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()

        logger.info(
            f"[{request_id}] Request started: "
            f"{request.method} {request.url.path}"
        )

        try:
            response = await call_next(request)

            duration = time.perf_counter() - start_time

            response.headers["X-Request-ID"] = request_id

            logger.info(
                f"[{request_id}] Request completed: "
                f"status={response.status_code}, "
                f"latency={duration:.4f}s"
            )

            return response

        except Exception as e:

            duration = time.perf_counter() - start_time

            logger.exception(
                f"[{request_id}] Request failed: "
                f"latency={duration:.4f}s, "
                f"error={str(e)}"
            )

            raise