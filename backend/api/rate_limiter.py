from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
import threading


class RateLimiter:
    """
    Basic in-memory rate limiter that tracks requests per IP address.

    For production use, consider using Redis or a database for persistence
    and distributed rate limiting across multiple server instances.
    """

    def __init__(self, max_requests: int = 5, window_hours: int = 24):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed per window
            window_hours: Time window in hours for rate limiting
        """
        self.max_requests = max_requests
        self.window_hours = window_hours
        self.requests: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request.
        Uses IP address as the identifier.
        """
        # Try to get real IP from headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in case of multiple proxies
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

    def _cleanup_expired_entries(self):
        """Remove expired entries from the requests dictionary."""
        current_time = datetime.now()
        expired_keys = []

        for client_id, data in self.requests.items():
            if current_time - data["window_start"] > timedelta(hours=self.window_hours):
                expired_keys.append(client_id)

        for key in expired_keys:
            del self.requests[key]

    def is_allowed(self, request: Request) -> bool:
        """
        Check if the request is allowed based on rate limiting rules.

        Args:
            request: FastAPI Request object

        Returns:
            bool: True if request is allowed, False otherwise
        """
        client_id = self._get_client_id(request)
        current_time = datetime.now()

        with self.lock:
            # Clean up expired entries
            self._cleanup_expired_entries()

            # Check if client exists in our tracking
            if client_id not in self.requests:
                # First request from this client
                self.requests[client_id] = {
                    "count": 1,
                    "window_start": current_time,
                    "last_request": current_time,
                }
                return True

            client_data = self.requests[client_id]

            # Check if we're still within the same window
            if current_time - client_data["window_start"] <= timedelta(
                hours=self.window_hours
            ):
                # Same window - check if limit exceeded
                if client_data["count"] >= self.max_requests:
                    return False
                else:
                    # Increment count and update last request time
                    client_data["count"] += 1
                    client_data["last_request"] = current_time
                    return True
            else:
                # New window - reset counter
                self.requests[client_id] = {
                    "count": 1,
                    "window_start": current_time,
                    "last_request": current_time,
                }
                return True

    def get_remaining_requests(self, request: Request) -> int:
        """
        Get the number of remaining requests for a client.

        Args:
            request: FastAPI Request object

        Returns:
            int: Number of remaining requests
        """
        client_id = self._get_client_id(request)
        current_time = datetime.now()

        with self.lock:
            if client_id not in self.requests:
                return self.max_requests

            client_data = self.requests[client_id]

            # Check if window has expired
            if current_time - client_data["window_start"] > timedelta(
                hours=self.window_hours
            ):
                return self.max_requests

            return max(0, self.max_requests - client_data["count"])

    def get_reset_time(self, request: Request) -> Optional[datetime]:
        """
        Get the time when the rate limit will reset for a client.

        Args:
            request: FastAPI Request object

        Returns:
            datetime: When the rate limit resets, or None if no limit applied
        """
        client_id = self._get_client_id(request)

        with self.lock:
            if client_id not in self.requests:
                return None

            client_data = self.requests[client_id]
            return client_data["window_start"] + timedelta(hours=self.window_hours)


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=5, window_hours=24)


def check_rate_limit(request: Request):
    """
    Dependency function to check rate limits.
    Raises HTTPException if rate limit is exceeded.

    Args:
        request: FastAPI Request object

    Raises:
        HTTPException: 429 status if rate limit exceeded
    """
    if not rate_limiter.is_allowed(request):
        remaining = rate_limiter.get_remaining_requests(request)
        reset_time = rate_limiter.get_reset_time(request)

        error_detail = {
            "error": "Rate limit exceeded",
            "message": f"Maximum {rate_limiter.max_requests} requests allowed per {rate_limiter.window_hours} hours",
            "remaining_requests": remaining,
            "reset_time": reset_time.isoformat() if reset_time else None,
        }

        raise HTTPException(
            status_code=429,
            detail=error_detail,
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": (
                    str(int(reset_time.timestamp())) if reset_time else "0"
                ),
                "Retry-After": (
                    str(int((reset_time - datetime.now()).total_seconds()))
                    if reset_time
                    else "86400"
                ),
            },
        )
