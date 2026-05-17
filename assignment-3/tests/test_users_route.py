"""
Tests for /api/users routes.

All API calls are faked, so no real HTTP requests happen.
"""

from unittest.mock import patch

import pytest

from services.external_api_service import ExternalAPIError, ExternalAPINotFoundError
from tests.conftest import SAMPLE_USER, SAMPLE_TODOS

PATCH_TARGET = "routes.users.ExternalAPIService"


class TestListUsersRoute:
    def test_returns_200_with_users(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            MockSvc.return_value.get_users.return_value = [SAMPLE_USER]
            resp = client.get("/api/users/")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["email"] == SAMPLE_USER["email"]

    def test_returns_error_on_failure(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            MockSvc.return_value.get_users.side_effect = ExternalAPIError(
                "timeout", status_code=504
            )
            resp = client.get("/api/users/")

        assert resp.status_code == 504


class TestGetUserRoute:
    def test_returns_200_for_existing_user(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            MockSvc.return_value.get_user.return_value = SAMPLE_USER
            resp = client.get("/api/users/1")

        assert resp.status_code == 200
        assert resp.get_json()["username"] == "Bret"

    def test_returns_404_for_unknown_user(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            MockSvc.return_value.get_user.side_effect = ExternalAPINotFoundError(
                "https://test.invalid/users/99"
            )
            resp = client.get("/api/users/99")

        assert resp.status_code == 404


class TestGetUserTodosRoute:
    def test_returns_todos(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            MockSvc.return_value.get_user_todos.return_value = SAMPLE_TODOS
            resp = client.get("/api/users/1/todos")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 3
        assert data[1]["completed"] is True

    def test_returns_404_when_user_not_found(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            MockSvc.return_value.get_user_todos.side_effect = (
                ExternalAPINotFoundError("https://test.invalid/users/99/todos")
            )
            resp = client.get("/api/users/99/todos")

        assert resp.status_code == 404


class TestEnrichedUserRoute:
    def test_returns_enriched_payload(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_user.return_value = SAMPLE_USER
            instance.get_user_todos.return_value = SAMPLE_TODOS

            resp = client.get("/api/users/1/enriched")

        assert resp.status_code == 200
        data = resp.get_json()
        assert "user" in data
        assert "todo_stats" in data
        stats = data["todo_stats"]
        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 2
        assert stats["completion_rate_pct"] == pytest.approx(33.3)

    def test_returns_404_when_user_missing(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_user.side_effect = ExternalAPINotFoundError(
                "https://test.invalid/users/99"
            )
            resp = client.get("/api/users/99/enriched")

        assert resp.status_code == 404

    def test_handles_user_with_no_todos(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_user.return_value = SAMPLE_USER
            instance.get_user_todos.return_value = []

            resp = client.get("/api/users/1/enriched")

        assert resp.status_code == 200
        stats = resp.get_json()["todo_stats"]
        assert stats["total"] == 0
        assert stats["completion_rate_pct"] == 0.0
