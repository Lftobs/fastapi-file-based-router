def get():
    """Home page endpoint."""
    return {
        "message": "Welcome to the File-Based Router Demo!",
        "routes": [
            "GET / - This page",
            "GET /users - List users",
            "GET /users/{id} - Get user by ID",
            "POST /users - Create user",
            "GET /blog/{slug} - Get blog post by slug",
            "GET /files/{path} - Get file at path (catch-all)",
            "GET /api/v1/health - Health check",
        ],
    }
