from fastapi import Body, Query, Header, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json


# Pydantic models
class PostData(BaseModel):
    title: str
    content: str
    tags: Optional[list] = []
    published: bool = False


class CommentData(BaseModel):
    author: str
    message: str


def get(
    # Query parameters
    limit: int = Query(10, description="Number of posts to return"),
    offset: int = Query(0, description="Number of posts to skip"),
    published_only: bool = Query(False, description="Only return published posts"),
):
    """Get posts with query parameters."""
    posts = [
        {"id": 1, "title": "Hello World", "published": True},
        {"id": 2, "title": "Draft Post", "published": False},
        {"id": 3, "title": "Another Post", "published": True},
    ]

    # Filter by published status
    if published_only:
        posts = [p for p in posts if p["published"]]

    # Apply pagination
    posts = posts[offset : offset + limit]

    return {
        "posts": posts,
        "pagination": {"limit": limit, "offset": offset},
        "filters": {"published_only": published_only},
    }


def post(
    # Request body (JSON)
    post_data: PostData,
    # Headers
    user_agent: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    # Query parameters
    draft: bool = Query(False, description="Save as draft"),
):
    """Create a new post with JSON body, headers, and query params."""
    new_post = {
        "id": 999,
        "title": post_data.title,
        "content": post_data.content,
        "tags": post_data.tags,
        "published": post_data.published and not draft,
        "metadata": {
            "user_agent": user_agent,
            "has_auth": authorization is not None,
            "is_draft": draft,
        },
    }

    return {"message": "Post created", "post": new_post}


def put(
    # Multiple request body types
    post_data: PostData = Body(...),
    comments: list[CommentData] = Body([]),
    metadata: Dict[str, Any] = Body({}),
):
    """Update post with multiple body parts."""
    return {
        "message": "Post updated with multiple body parts",
        "post": post_data.dict(),
        "comments": [c.dict() for c in comments],
        "metadata": metadata,
    }


async def patch(request: Request):
    """Handle raw request for custom processing."""
    # Get raw body
    body = await request.body()

    # Get headers
    headers = dict(request.headers)

    # Get query params
    query_params = dict(request.query_params)

    # Parse JSON if present
    try:
        json_data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        json_data = {"error": "Invalid JSON"}

    return {
        "message": "Raw request processed",
        "body_size": len(body),
        "headers_count": len(headers),
        "query_params": query_params,
        "json_data": json_data,
        "method": request.method,
        "url": str(request.url),
    }
