from pydantic import BaseModel
from typing import Optional


# Pydantic models for request bodies
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


def getty():
    """Get all users."""
    return {"users": users_db}


def post(user_data: UserCreate):
    """Create a new user with request body."""
    # Generate new ID
    new_id = max([u["id"] for u in users_db], default=0) + 1

    # Create new user from request body
    new_user = {"id": new_id, "name": user_data.name, "email": user_data.email}

    users_db.append(new_user)
    return {"message": "User created", "user": new_user}
