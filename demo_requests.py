"""
Demo script showing how to handle request bodies in the file-based router.
"""

from file_router import create_file_router
from fastapi.testclient import TestClient
import json


def main():
    print("🔄 Request Body Handling Demo")
    print("=" * 50)

    # Create the router
    router = create_file_router("routes")
    client = TestClient(router.get_app())

    print("\n1. 📤 JSON Request Body (POST /users)")
    print("-" * 30)
    user_data = {"name": "John Doe", "email": "john@example.com"}
    response = client.post("/users", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(user_data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n2. 🔄 JSON Request Body (PUT /users/1)")
    print("-" * 30)
    update_data = {"name": "John Smith", "email": "john.smith@example.com"}
    response = client.put("/users/1", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(update_data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n3. 🔍 Query Parameters (GET /posts)")
    print("-" * 30)
    params = {"limit": 5, "offset": 0, "published_only": True}
    response = client.get("/posts", params=params)
    print(f"Status: {response.status_code}")
    print(f"Query params: {params}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n4. 📝 Complex POST with Headers (POST /posts)")
    print("-" * 30)
    post_data = {
        "title": "My Awesome Post",
        "content": "This is the content of my post",
        "tags": ["python", "fastapi", "tutorial"],
        "published": True,
    }
    headers = {
        "User-Agent": "FileRouter-Demo/1.0",
        "Authorization": "Bearer fake-token",
    }
    params = {"draft": False}

    response = client.post("/posts", json=post_data, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Body: {json.dumps(post_data, indent=2)}")
    print(f"Headers: {headers}")
    print(f"Query: {params}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n5. 🔀 Multiple Body Parts (PUT /posts)")
    print("-" * 30)
    complex_data = {
        "post_data": {
            "title": "Updated Post",
            "content": "Updated content",
            "tags": ["updated"],
            "published": True,
        },
        "comments": [
            {"author": "Alice", "message": "Great post!"},
            {"author": "Bob", "message": "Very helpful, thanks!"},
        ],
        "metadata": {"editor": "John Doe", "last_modified": "2023-07-29T10:00:00Z"},
    }

    response = client.put("/posts", json=complex_data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(complex_data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n6. 🔍 Raw Request Processing (PATCH /posts)")
    print("-" * 30)
    raw_data = {"custom": "data", "numbers": [1, 2, 3]}
    headers = {"X-Custom-Header": "custom-value"}
    params = {"debug": "true"}

    response = client.patch("/posts", json=raw_data, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n✅ All request body types handled successfully!")


if __name__ == "__main__":
    main()
