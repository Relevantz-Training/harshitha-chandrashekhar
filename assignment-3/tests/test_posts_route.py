"""
Tests for /api/posts routes.

All API calls are faked, so no real HTTP requests happen.
Tests check status codes and response data.
"""

from unittest.mock import patch, MagicMock

import pytest

from services.external_api_service import ExternalAPIError, ExternalAPINotFoundError
from tests.conftest import SAMPLE_POST

PATCH_TARGET = "routes.posts.ExternalAPIService"


class TestListPostsRoute:
    def test_returns_200_with_list(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_posts.return_value = [SAMPLE_POST]

            resp = client.get("/api/posts/")

        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["user_id"] == SAMPLE_POST["userId"]
        assert data[0]["title"] == SAMPLE_POST["title"]

    def test_returns_502_on_external_api_error(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_posts.side_effect = ExternalAPIError("upstream down")

            resp = client.get("/api/posts/")

        assert resp.status_code == 502
        assert "error" in resp.get_json()

    def test_returns_empty_list_when_no_posts(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_posts.return_value = []

            resp = client.get("/api/posts/")

        assert resp.status_code == 200
        assert resp.get_json() == []


class TestGetPostRoute:
    def test_returns_200_for_existing_post(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_post.return_value = SAMPLE_POST

            resp = client.get("/api/posts/1")

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == 1
        assert data["body"] == SAMPLE_POST["body"]

    def test_returns_404_for_missing_post(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_post.side_effect = ExternalAPINotFoundError(
                "https://test.invalid/posts/999"
            )

            resp = client.get("/api/posts/999")

        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_returns_error_status_on_upstream_failure(self, client):
        with patch(PATCH_TARGET) as MockSvc:
            instance = MockSvc.return_value
            instance.get_post.side_effect = ExternalAPIError(
                "Service Unavailable", status_code=503
            )

            resp = client.get("/api/posts/1")

        assert resp.status_code == 503
