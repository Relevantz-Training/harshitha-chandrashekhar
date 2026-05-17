
"""
external_api_service.py
----------------------
Handles all HTTP calls to the JSONPlaceholder API.
Adds timeouts, retries, and error handling for safety.
"""

import logging
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryError,
)

logger = logging.getLogger(__name__)

# ─── typed errors ────────────────────────────────────────────────────────────



# Custom error for any problem with the external API
class ExternalAPIError(Exception):
    """Something went wrong with the external API."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code



# Custom error for 404 not found from the external API
class ExternalAPINotFoundError(ExternalAPIError):
    """The requested resource was not found (404)."""

    def __init__(self, resource: str) -> None:
        super().__init__(f"Resource not found: {resource}", status_code=404)


# ─── service class ────────────────────────────────────────────────────────────



class ExternalAPIService:
    """
    Talks to the JSONPlaceholder API.
    Adds timeout, retry, and error handling.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout: int = 10,
        max_retries: int = 3,
        retry_wait: int = 1,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_wait = retry_wait

        # Set up a session for all HTTP requests
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        # Add Authorization header if api_key is given
        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"

    # ── private helpers ───────────────────────────────────────────────────

    def _get(self, path: str) -> Any:
        """
        Make a GET request to the API.
        Retries on network errors or 5xx. Raises clear errors for 404 or other problems.
        """
        url = f"{self._base_url}/{path.lstrip('/')}"

        @retry(
            retry=retry_if_exception_type(
                (requests.ConnectionError, requests.Timeout)
            ),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(
                multiplier=self._retry_wait, min=self._retry_wait, max=30
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        def _attempt() -> requests.Response:
            logger.debug("GET %s (timeout=%ss)", url, self._timeout)
            response = self._session.get(url, timeout=self._timeout)
            # Trigger retries for server-side transient errors.
            if response.status_code >= 500:
                raise requests.ConnectionError(
                    f"Server error {response.status_code} from {url}"
                )
            return response

        try:
            resp = _attempt()
        except RetryError as exc:
            raise ExternalAPIError(
                f"Max retries exceeded for {url}"
            ) from exc
        except requests.Timeout as exc:
            raise ExternalAPIError(
                f"Request timed out after {self._timeout}s: {url}"
            ) from exc
        except requests.RequestException as exc:
            raise ExternalAPIError(
                f"Network error while calling {url}: {exc}"
            ) from exc

        if resp.status_code == 404:
            raise ExternalAPINotFoundError(url)
        if not resp.ok:
            raise ExternalAPIError(
                f"Unexpected status {resp.status_code} from {url}",
                status_code=resp.status_code,
            )

        return resp.json()

    # ── public API ────────────────────────────────────────────────────────


    def get_posts(self) -> list[dict]:
        """Get all posts."""
        return self._get("/posts")


    def get_post(self, post_id: int) -> dict:
        """Get one post by its ID."""
        return self._get(f"/posts/{post_id}")


    def get_users(self) -> list[dict]:
        """Get all users."""
        return self._get("/users")


    def get_user(self, user_id: int) -> dict:
        """Get one user by their ID."""
        return self._get(f"/users/{user_id}")


    def get_user_todos(self, user_id: int) -> list[dict]:
        """Get all todos for a user."""
        return self._get(f"/users/{user_id}/todos")
