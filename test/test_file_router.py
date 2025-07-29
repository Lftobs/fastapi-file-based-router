import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from file_router import FileBasedRouter, create_file_router


class TestFileBasedRouter:
    def setup_method(self):
        """Set up test environment with temporary routes directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.routes_dir = Path(self.temp_dir) / "routes"
        self.routes_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)

    def create_route_file(self, path: str, content: str):
        """Helper to create route files."""
        file_path = self.routes_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path

    def test_parse_dynamic_segment(self):
        """Test parsing of dynamic route segments."""
        router = FileBasedRouter()

        # Simple parameter
        name, type_, is_catch_all = router._parse_dynamic_segment("[id]")
        assert name == "id"
        assert type_ == "str"
        assert is_catch_all == False

        # Typed parameter
        name, type_, is_catch_all = router._parse_dynamic_segment("[id:int]")
        assert name == "id"
        assert type_ == "int"
        assert is_catch_all == False

        # Slug parameter
        name, type_, is_catch_all = router._parse_dynamic_segment("[slug:]")
        assert name == "slug"
        assert type_ == "str"
        assert is_catch_all == False

        # Catch-all parameter
        name, type_, is_catch_all = router._parse_dynamic_segment("[...rest]")
        assert name == "rest"
        assert type_ == "str"
        assert is_catch_all == True

        # Non-dynamic segment
        name, type_, is_catch_all = router._parse_dynamic_segment("static")
        assert name == None
        assert type_ == None
        assert is_catch_all == False

    def test_convert_file_path_to_route(self):
        """Test conversion of file paths to route patterns."""
        router = FileBasedRouter(str(self.routes_dir))

        # Index route
        file_path = self.routes_dir / "index.py"
        pattern, params = router._convert_file_path_to_route(file_path)
        assert pattern == "/"
        assert params == {}

        # Simple nested route
        file_path = self.routes_dir / "users" / "index.py"
        pattern, params = router._convert_file_path_to_route(file_path)
        assert pattern == "/users"
        assert params == {}

        # Dynamic route with id
        file_path = self.routes_dir / "users" / "[id].py"
        pattern, params = router._convert_file_path_to_route(file_path)
        assert pattern == "/users/{id}"
        assert params == {"id": {"type": "str", "is_catch_all": False}}

        # Dynamic route with typed parameter
        file_path = self.routes_dir / "posts" / "[id:int].py"
        pattern, params = router._convert_file_path_to_route(file_path)
        assert pattern == "/posts/{id:int}"
        assert params == {"id": {"type": "int", "is_catch_all": False}}

        # Slug route
        file_path = self.routes_dir / "blog" / "[slug:].py"
        pattern, params = router._convert_file_path_to_route(file_path)
        assert pattern == "/blog/{slug}"
        assert params == {"slug": {"type": "str", "is_catch_all": False}}

        # Catch-all route
        file_path = self.routes_dir / "files" / "[...path].py"
        pattern, params = router._convert_file_path_to_route(file_path)
        assert pattern == "/files/{path:path}"
        assert params == {"path": {"type": "str", "is_catch_all": True}}

    def test_basic_route_registration(self):
        """Test basic route registration and handling."""
        # Create a simple route file
        self.create_route_file(
            "index.py",
            """
def get():
    return {"message": "Hello World"}

def post():
    return {"message": "Created"}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        # Test GET request
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

        # Test POST request
        response = client.post("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Created"}

    def test_nested_routes(self):
        """Test nested route structures."""
        # Create nested routes
        self.create_route_file(
            "users/index.py",
            """
def get():
    return {"users": []}
""",
        )

        self.create_route_file(
            "users/profile.py",
            """
def get():
    return {"profile": "user profile"}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == {"users": []}

        response = client.get("/users/profile")
        assert response.status_code == 200
        assert response.json() == {"profile": "user profile"}

    def test_dynamic_id_route(self):
        """Test dynamic routes with ID parameters."""
        self.create_route_file(
            "users/[id].py",
            """
def get(id):
    return {"user_id": id, "type": type(id).__name__}

def put(id):
    return {"updated_user": id}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        response = client.get("/users/123")
        assert response.status_code == 200
        assert response.json() == {"user_id": "123", "type": "str"}

        response = client.put("/users/456")
        assert response.status_code == 200
        assert response.json() == {"updated_user": "456"}

    def test_typed_dynamic_route(self):
        """Test dynamic routes with type constraints."""
        self.create_route_file(
            "posts/[id:int].py",
            """
def get(id):
    return {"post_id": id, "type": type(id).__name__}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        # Valid integer
        response = client.get("/posts/123")
        assert response.status_code == 200
        assert response.json() == {"post_id": 123, "type": "int"}

        # Invalid integer should return 404 (no route match) or 422 (validation error)
        response = client.get("/posts/abc")
        assert response.status_code in [404, 422]

    def test_slug_route(self):
        """Test slug-based routes."""
        self.create_route_file(
            "blog/[slug:].py",
            """
def get(slug):
    return {"slug": slug, "article": f"Content for {slug}"}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        response = client.get("/blog/my-awesome-post")
        assert response.status_code == 200
        assert response.json() == {
            "slug": "my-awesome-post",
            "article": "Content for my-awesome-post",
        }

    def test_catch_all_route(self):
        """Test catch-all routes."""
        self.create_route_file(
            "files/[...path].py",
            """
def get(path):
    return {"path": path, "segments": path.split("/")}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        response = client.get("/files/documents/reports/2023/report.pdf")
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "documents/reports/2023/report.pdf"
        assert data["segments"] == ["documents", "reports", "2023", "report.pdf"]

    def test_async_handlers(self):
        """Test async route handlers."""
        self.create_route_file(
            "async.py",
            """
import asyncio

async def get():
    await asyncio.sleep(0.01)  # Simulate async work
    return {"async": True}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        response = client.get("/async")
        assert response.status_code == 200
        assert response.json() == {"async": True}

    def test_multiple_dynamic_params(self):
        """Test routes with multiple dynamic parameters."""
        self.create_route_file(
            "users/[user_id]/posts/[post_id:int].py",
            """
def get(user_id, post_id):
    return {
        "user_id": user_id,
        "post_id": post_id,
        "post_id_type": type(post_id).__name__
    }
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        client = TestClient(router.get_app())

        response = client.get("/users/john/posts/42")
        assert response.status_code == 200
        assert response.json() == {
            "user_id": "john",
            "post_id": 42,
            "post_id_type": "int",
        }

    def test_route_info_retrieval(self):
        """Test getting information about registered routes."""
        self.create_route_file(
            "index.py",
            """
def get():
    return {}
""",
        )

        self.create_route_file(
            "users/[id].py",
            """
def get(id):
    return {}
def post(id):
    return {}
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        router.scan_routes()

        routes = router.get_routes()
        assert len(routes) == 2

        # Find the dynamic route
        dynamic_route = next(r for r in routes if "[id]" in r["file_path"])
        assert dynamic_route["pattern"] == "/users/{id}"
        assert "GET" in dynamic_route["methods"]
        assert "POST" in dynamic_route["methods"]
        assert dynamic_route["params"]["id"]["type"] == "str"

    def test_invalid_route_handling(self):
        """Test handling of invalid route files."""
        # Create a file with syntax error
        self.create_route_file(
            "invalid.py",
            """
def get(:
    return {}  # Syntax error
""",
        )

        # Create a file with no handlers
        self.create_route_file(
            "no_handlers.py",
            """
some_variable = "test"
""",
        )

        router = FileBasedRouter(str(self.routes_dir))
        # Should not raise exception
        router.scan_routes()

        # Should have no routes registered from invalid files
        routes = router.get_routes()
        assert all(
            "invalid" not in r["file_path"] and "no_handlers" not in r["file_path"]
            for r in routes
        )

    def test_create_file_router_function(self):
        """Test the convenience function for creating routers."""
        self.create_route_file(
            "test.py",
            """
def get():
    return {"test": True}
""",
        )

        router = create_file_router(str(self.routes_dir))
        client = TestClient(router.get_app())

        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"test": True}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
