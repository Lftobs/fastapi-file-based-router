from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional


# Pydantic models for request/response bodies
class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


users_db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
]


def get(id: int):
    """Get user by ID."""
    user = next((u for u in users_db if u["id"] == id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


def put(id: int, user_data: UserUpdate):
    """Update user by ID with request body."""
    user = next((u for u in users_db if u["id"] == id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields from request body
    if user_data.name is not None:
        user["name"] = user_data.name
    if user_data.email is not None:
        user["email"] = user_data.email

    return {"message": "User updated", "user": user}


def delete(id: int):
    """Delete user by ID."""
    global users_db
    user = next((u for u in users_db if u["id"] == id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    users_db = [u for u in users_db if u["id"] != id]
    return {"message": "User deleted", "user": user}
