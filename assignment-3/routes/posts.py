
"""
routes/posts.py
--------------
Defines the /api/posts endpoints for listing and getting posts.
Handles errors and returns clear JSON responses.
"""

import logging

from flask import Blueprint, jsonify, current_app

from models.schemas import Post
from services.external_api_service import (
    ExternalAPIService,
    ExternalAPIError,
    ExternalAPINotFoundError,
)

logger = logging.getLogger(__name__)

posts_bp = Blueprint("posts", __name__, url_prefix="/api/posts")



# Helper to get a service object with current config
def _get_service() -> ExternalAPIService:
    cfg = current_app.config
    return ExternalAPIService(
        base_url=cfg["JSONPLACEHOLDER_BASE_URL"],
        api_key=cfg.get("JSONPLACEHOLDER_API_KEY", ""),
        timeout=cfg["REQUEST_TIMEOUT_SECONDS"],
        max_retries=cfg["MAX_RETRY_ATTEMPTS"],
        retry_wait=cfg["RETRY_WAIT_SECONDS"],
    )


@posts_bp.get("/")
def list_posts():
    """
    Return a list of all posts as JSON.
    If the external API fails, return an error message.
    """
    try:
        raw = _get_service().get_posts()
        posts = [Post.from_api(p).to_dict() for p in raw]
        logger.info("Fetched %d posts from external API", len(posts))
        return jsonify(posts), 200
    except ExternalAPIError as exc:
        logger.error("Failed to fetch posts: %s", exc)
        return jsonify({"error": str(exc)}), exc.status_code


@posts_bp.get("/<int:post_id>")
def get_post(post_id: int):
    """
    Return one post by its ID as JSON.
    If not found, return a 404 error message.
    """
    try:
        raw = _get_service().get_post(post_id)
        post = Post.from_api(raw).to_dict()
        return jsonify(post), 200
    except ExternalAPINotFoundError as exc:
        logger.warning("Post %d not found: %s", post_id, exc)
        return jsonify({"error": str(exc)}), 404
    except ExternalAPIError as exc:
        logger.error("Failed to fetch post %d: %s", post_id, exc)
        return jsonify({"error": str(exc)}), exc.status_code
