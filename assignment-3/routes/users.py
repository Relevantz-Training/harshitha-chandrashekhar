"""
routes/users.py
----------------
Flask blueprint exposing a façade over the JSONPlaceholder /users resource,
including an enriched endpoint that appends the user's todo summary.

Endpoints
---------
GET /api/users                       → list of all users
GET /api/users/<user_id>             → single user
GET /api/users/<user_id>/todos       → todos for a user
GET /api/users/<user_id>/enriched    → user + todo stats (demonstrates enrichment pattern)
"""

import logging

from flask import Blueprint, jsonify, current_app

from models.schemas import User, Todo
from services.external_api_service import (
    ExternalAPIService,
    ExternalAPIError,
    ExternalAPINotFoundError,
)

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _get_service() -> ExternalAPIService:
    cfg = current_app.config
    return ExternalAPIService(
        base_url=cfg["JSONPLACEHOLDER_BASE_URL"],
        api_key=cfg.get("JSONPLACEHOLDER_API_KEY", ""),
        timeout=cfg["REQUEST_TIMEOUT_SECONDS"],
        max_retries=cfg["MAX_RETRY_ATTEMPTS"],
        retry_wait=cfg["RETRY_WAIT_SECONDS"],
    )


@users_bp.get("/")
def list_users():
    """
    List all users.

    Response 200::

        [
          {
            "id": 1,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "Sincere@april.biz",
            "phone": "1-770-736-8031 x56442",
            "website": "hildegard.org",
            "address": {
              "street": "Kulas Light",
              "suite": "Apt. 556",
              "city": "Gwenborough",
              "zipcode": "92998-3874"
            }
          },
          ...
        ]
    """
    try:
        raw = _get_service().get_users()
        users = [User.from_api(u).to_dict() for u in raw]
        logger.info("Fetched %d users from external API", len(users))
        return jsonify(users), 200
    except ExternalAPIError as exc:
        logger.error("Failed to fetch users: %s", exc)
        return jsonify({"error": str(exc)}), exc.status_code


@users_bp.get("/<int:user_id>")
def get_user(user_id: int):
    """
    Retrieve a single user by ID.

    Response 200: single user object (see list_users for shape).
    Response 404: ``{"error": "Resource not found: ..."}``
    """
    try:
        raw = _get_service().get_user(user_id)
        return jsonify(User.from_api(raw).to_dict()), 200
    except ExternalAPINotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@users_bp.get("/<int:user_id>/todos")
def get_user_todos(user_id: int):
    """
    Get all todos for one user.

    Returns a list of todo items for the user.
    Each item has id, user_id, title, and completed.
    """
    try:
        raw = _get_service().get_user_todos(user_id)
        todos = [Todo.from_api(t).to_dict() for t in raw]
        return jsonify(todos), 200
    except ExternalAPINotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@users_bp.get("/<int:user_id>/enriched")
def get_enriched_user(user_id: int):
    """
    Get a user with extra todo stats.

    This combines user info and their todo stats in one response.
    Shows total, completed, pending, and percent done.
    """
    try:
        svc = _get_service()
        user_raw = svc.get_user(user_id)
        todos_raw = svc.get_user_todos(user_id)
    except ExternalAPINotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), exc.status_code

    # Make todo objects from API data
    todos = [Todo.from_api(t) for t in todos_raw]
    total = len(todos)  # Total todos
    completed = sum(1 for t in todos if t.completed)  # Todos done
    pending = total - completed  # Todos not done
    rate = round((completed / total * 100), 1) if total else 0.0  # Percent done

    return jsonify(
        {
            "user": User.from_api(user_raw).to_dict(),
            "todo_stats": {
                "total": total,
                "completed": completed,
                "pending": pending,
                "completion_rate_pct": rate,
            },
        }
    ), 200
