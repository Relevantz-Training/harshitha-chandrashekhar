"""
Unit tests for ExternalAPIService.

All HTTP calls are faked using the responses library, so no real network traffic happens.
Tests check for correct results and errors.
"""

import pytest
import responses as rsps_lib
import requests

from services.external_api_service import (
    ExternalAPIService,
    ExternalAPIError,
    ExternalAPINotFoundError,
)
from tests.conftest import SAMPLE_POST, SAMPLE_USER, SAMPLE_TODOS

BASE = "https://test.invalid"


def _make_service(**kwargs) -> ExternalAPIService:
    defaults = dict(
        base_url=BASE,
        api_key="",
        timeout=5,
        max_retries=2,
        retry_wait=0,
    )
    defaults.update(kwargs)
    return ExternalAPIService(**defaults)


# ── posts ─────────────────────────────────────────────────────────────────────


class TestGetPosts:
    @rsps_lib.activate
    def test_returns_list_of_posts(self):
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", json=[SAMPLE_POST], status=200)
        svc = _make_service()
        result = svc.get_posts()
        assert isinstance(result, list)
        assert result[0]["id"] == 1
        assert result[0]["title"] == SAMPLE_POST["title"]

    @rsps_lib.activate
    def test_raises_on_server_error(self):
        # Two 500 responses (matching max_retries=2).
        for _ in range(2):
            rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", status=500)
        svc = _make_service(max_retries=2)
        with pytest.raises(ExternalAPIError):
            svc.get_posts()


class TestGetPost:
    @rsps_lib.activate
    def test_returns_single_post(self):
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts/1", json=SAMPLE_POST, status=200)
        svc = _make_service()
        result = svc.get_post(1)
        assert result["id"] == 1

    @rsps_lib.activate
    def test_raises_not_found_for_404(self):
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts/999", json={}, status=404)
        svc = _make_service()
        with pytest.raises(ExternalAPINotFoundError):
            svc.get_post(999)

    @rsps_lib.activate
    def test_raises_external_api_error_for_non_2xx(self):
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts/1", status=403)
        svc = _make_service()
        with pytest.raises(ExternalAPIError) as exc_info:
            svc.get_post(1)
        assert exc_info.value.status_code == 403


# ── users ─────────────────────────────────────────────────────────────────────


class TestGetUsers:
    @rsps_lib.activate
    def test_returns_list_of_users(self):
        rsps_lib.add(rsps_lib.GET, f"{BASE}/users", json=[SAMPLE_USER], status=200)
        svc = _make_service()
        result = svc.get_users()
        assert len(result) == 1
        assert result[0]["email"] == SAMPLE_USER["email"]

    @rsps_lib.activate
    def test_raises_not_found_for_404(self):
        rsps_lib.add(rsps_lib.GET, f"{BASE}/users/99", json={}, status=404)
        svc = _make_service()
        with pytest.raises(ExternalAPINotFoundError):
            svc.get_user(99)


class TestGetUserTodos:
    @rsps_lib.activate
    def test_returns_todos(self):
        rsps_lib.add(
            rsps_lib.GET, f"{BASE}/users/1/todos", json=SAMPLE_TODOS, status=200
        )
        svc = _make_service()
        result = svc.get_user_todos(1)
        assert len(result) == 3
        assert result[1]["completed"] is True


# ── security ──────────────────────────────────────────────────────────────────


class TestAuthorizationHeader:
    @rsps_lib.activate
    def test_api_key_sent_as_bearer_token(self):
        """Verify the Authorization header is injected when api_key is set."""
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", json=[SAMPLE_POST], status=200)
        svc = _make_service(api_key="supersecrettoken")
        svc.get_posts()
        sent_headers = rsps_lib.calls[0].request.headers
        assert sent_headers["Authorization"] == "Bearer supersecrettoken"

    @rsps_lib.activate
    def test_no_authorization_header_when_key_empty(self):
        """No Authorization header should be added for public APIs."""
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", json=[SAMPLE_POST], status=200)
        svc = _make_service(api_key="")
        svc.get_posts()
        sent_headers = rsps_lib.calls[0].request.headers
        assert "Authorization" not in sent_headers


# ── retry behaviour ───────────────────────────────────────────────────────────


class TestRetry:
    @rsps_lib.activate
    def test_succeeds_after_transient_failure(self):
        """First call returns 500 (retried), second returns 200 (success)."""
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", status=500)
        rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", json=[SAMPLE_POST], status=200)
        svc = _make_service(max_retries=3, retry_wait=0)
        result = svc.get_posts()
        assert result[0]["id"] == 1

    @rsps_lib.activate
    def test_raises_after_all_retries_exhausted(self):
        for _ in range(3):
            rsps_lib.add(rsps_lib.GET, f"{BASE}/posts", status=500)
        svc = _make_service(max_retries=3, retry_wait=0)
        with pytest.raises(ExternalAPIError):
            svc.get_posts()
