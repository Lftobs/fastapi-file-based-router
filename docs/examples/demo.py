"""
Demo script for the FastAPI File-Based Router

This script demonstrates all the features of the file-based router without
needing to start a server. It shows how different route patterns work.
"""

from file_router import file_router
from fastapi.testclient import TestClient


def main():
    print("🚀 FastAPI File-Based Router Demo")
    print("=" * 50)

    # Create the router
    router = file_router("routes")
    client = TestClient(router.get_app())

    # Show registered routes
    print("\nRegistered routes:")
    routes = router.get_routes()
    for route in sorted(routes, key=lambda x: x["pattern"]):
        methods = ", ".join(route["methods"])
        print(f"  {route['pattern']:<30} [{methods}]")

    print("\nRoute examples:")
    print("-" * 30)

    # Test static routes
    print("\n📄 Static Routes:")
    response = client.get("/")
    print(f"GET / -> {response.status_code}")
    print(f"Response: {response.json()['message']}")

    response = client.get("/users")
    print(f"GET /users -> {response.status_code}")
    print(f"Found {len(response.json()['users'])} users")

    # Test dynamic routes with ID
    print("\n🔢 Dynamic Routes (ID):")
    response = client.get("/users/1")
    print(f"GET /users/1 -> {response.status_code}")
    print(f"User: {response.json()['user']['name']}")

    response = client.get("/users/999")
    print(f"GET /users/999 -> {response.status_code}")
    if response.status_code == 404:
        print("User not found (expected)")

    # Test slug routes
    print("\n📝 Slug Routes:")
    response = client.get("/blog/hello-world")
    print(f"GET /blog/hello-world -> {response.status_code}")
    print(f"Post: {response.json()['post']['title']}")

    response = client.get("/blog/nonexistent-post")
    print(f"GET /blog/nonexistent-post -> {response.status_code}")
    if response.status_code == 404:
        print("Post not found (expected)")

    # Test catch-all routes
    print("\n📁 Catch-all Routes:")
    response = client.get("/files/documents/readme.txt")
    print(f"GET /files/documents/readme.txt -> {response.status_code}")
    data = response.json()
    print(f"File: {data['filename']} in {data['directory']}")

    response = client.get("/files/images/photos/vacation.jpg")
    print(f"GET /files/images/photos/vacation.jpg -> {response.status_code}")
    data = response.json()
    print(f"File: {data['filename']}, Size: {data['size']} bytes")

    # Test API routes
    print("\n🔧 API Routes:")
    response = client.get("/api/v1/health")
    print(f"GET /api/v1/health -> {response.status_code}")
    print(f"Status: {response.json()['status']}")

    # Test POST request
    print("\n📤 POST Requests:")
    response = client.post("/users")
    print(f"POST /users -> {response.status_code}")
    print(f"Created: {response.json()['user']['name']}")

    print("\n✅ All route types working correctly!")
    print("\nTo run the live server:")
    print("  python server.py")
    print("  # Then visit http://localhost:8000")


if __name__ == "__main__":
    main()
