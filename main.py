"""
FastAPI File-Based Router Demo Server

This server demonstrates the file-based routing system with support for:
- Static routes (index.py -> /)
- Dynamic routes ([id].py -> /{id})
- Typed routes ([id:int].py -> /{id:int})
- Slug routes ([slug:].py -> /{slug})
- Catch-all routes ([...path].py -> /{path:path})

Usage:
    python server.py

Then visit http://localhost:8000 to see the demo in action.
"""

import uvicorn
from file_router import create_file_router

# Create the app at module level for uvicorn reload
router = create_file_router("routes")
app = router.get_app()


def main():
    # Add some middleware for better demo experience
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Print route information
    print("\n🚀 File-Based Router Demo Server")
    print("=" * 50)
    print("Server starting at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("Routes directory: routes/")
    print("\nRegistered routes:")

    routes = router.get_routes()
    for route in sorted(routes, key=lambda x: x["pattern"]):
        methods = ", ".join(route["methods"])
        print(f"  {route['pattern']:<30} [{methods}] -> {route['file_path']}")

    print("\nExample requests to try:")
    print("  curl http://localhost:8000/")
    print("  curl http://localhost:8000/users")
    print("  curl http://localhost:8000/users/1")
    print("  curl http://localhost:8000/blog/hello-world")
    print("  curl http://localhost:8000/files/documents/readme.txt")
    print("  curl http://localhost:8000/api/v1/health")
    print("\n" + "=" * 50)
    # Start the server
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["routes"]
    )


if __name__ == "__main__":
    main()
