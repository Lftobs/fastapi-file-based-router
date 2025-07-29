import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any, Callable
from fastapi import FastAPI
import inspect


class FileBasedRouter:
    def __init__(self, routes_dir: str = "routes"):
        self.routes_dir = Path(routes_dir)
        self.app = FastAPI()
        self._routes: List[Dict[str, Any]] = []

    def _parse_dynamic_segment(self, segment: str) -> Tuple[str, str, bool]:
        """
        Parse dynamic route segments.
        Returns: (param_name, param_type, is_catch_all)

        Supported formats:
        - [id] -> ('id', 'str', False)
        - [id:int] -> ('id', 'int', False)
        - [slug:] -> ('slug', 'str', False)
        - [...rest] -> ('rest', 'str', True)
        """
        if not segment.startswith("[") or not segment.endswith("]"):
            return None, None, False

        inner = segment[1:-1]

        # Catch-all route [...rest]
        if inner.startswith("..."):
            param_name = inner[3:]
            return param_name, "str", True

        # Typed parameter [id:int] or slug parameter [slug:]
        if ":" in inner:
            param_name, param_type = inner.split(":", 1)
            if param_type == "":
                param_type = "str"  # [slug:] defaults to string
            return param_name, param_type, False

        # Simple parameter [id]
        return inner, "str", False

    def _convert_file_path_to_route(
        self, file_path: Path
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Convert file path to FastAPI route pattern and extract parameters.

        Examples:
        - routes/users/index.py -> /users
        - routes/users/[id].py -> /users/{id}
        - routes/posts/[slug:].py -> /posts/{slug}
        - routes/files/[...path].py -> /files/{path:path}
        """
        # Get relative path from routes directory
        rel_path = file_path.relative_to(self.routes_dir)

        # Remove .py extension
        path_parts = list(rel_path.parts[:-1]) + [rel_path.stem]

        # Replace index with empty string
        if path_parts[-1] == "index":
            path_parts = path_parts[:-1]

        route_pattern = ""
        params = {}

        for part in path_parts:
            param_name, param_type, is_catch_all = self._parse_dynamic_segment(part)

            if param_name:
                if is_catch_all:
                    route_pattern += f"/{{{param_name}:path}}"
                else:
                    if param_type == "int":
                        route_pattern += f"/{{{param_name}:int}}"
                    else:
                        route_pattern += f"/{{{param_name}}}"

                params[param_name] = {"type": param_type, "is_catch_all": is_catch_all}
            else:
                route_pattern += f"/{part}"

        # Ensure route starts with /
        if not route_pattern:
            route_pattern = "/"
        elif not route_pattern.startswith("/"):
            route_pattern = "/" + route_pattern

        return route_pattern, params

    def _load_route_module(self, file_path: Path):
        """Load a Python module from file path."""
        module_name = f"route_{file_path.stem}_{hash(str(file_path))}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _extract_route_handlers(
        self, module, route_pattern: str, params: Dict[str, Any]
    ):
        """Extract HTTP method handlers from a route module."""
        handlers = {}

        # Common HTTP methods
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

        for method in methods:
            # Look for handler function (get, post, put, etc.)
            handler_name = method.lower()
            if hasattr(module, handler_name):
                handler = getattr(module, handler_name)
                if callable(handler):
                    handlers[method] = handler

        return handlers

    def _create_route_wrapper(self, handler: Callable, params: Dict[str, Any]):
        """Create a wrapper function that properly handles path parameters."""
        sig = inspect.signature(handler)

        if not params:
            # No path parameters - create simple wrapper that preserves signature
            # This allows FastAPI to handle request bodies, query params, headers, etc.
            if inspect.iscoroutinefunction(handler):

                async def wrapper(*args, **kwargs):
                    return await handler(*args, **kwargs)
            else:

                def wrapper(*args, **kwargs):
                    return handler(*args, **kwargs)

            # Preserve the original signature for FastAPI dependency injection
            wrapper.__signature__ = sig
            return wrapper

        # For routes with path parameters, we need to ensure the signature is correct
        # but still let FastAPI handle other parameter types (Body, Query, Header, etc.)

        # Get all parameter names and their information from the original handler
        original_params = list(sig.parameters.values())
        path_param_names = set(params.keys())

        # Build new signature preserving non-path parameters as-is
        new_params = []

        # First, add path parameters with correct types
        for param_name, param_info in params.items():
            if param_info["type"] == "int":
                param_type = int
            else:
                param_type = str

            new_params.append(
                inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=param_type,
                )
            )

        # Then, add all other parameters from the original handler (request bodies, etc.)
        for param in original_params:
            if param.name not in path_param_names:
                new_params.append(param)

        # Create wrapper function that preserves FastAPI's dependency injection
        if inspect.iscoroutinefunction(handler):

            async def wrapper(*args, **kwargs):
                return await handler(*args, **kwargs)
        else:

            def wrapper(*args, **kwargs):
                return handler(*args, **kwargs)

        # Set the correct signature for FastAPI
        new_sig = inspect.Signature(new_params)
        wrapper.__signature__ = new_sig

        return wrapper

    def scan_routes(self):
        """Scan the routes directory and register all route files."""
        if not self.routes_dir.exists():
            raise FileNotFoundError(f"Routes directory '{self.routes_dir}' not found")

        # Find all Python files in routes directory
        for file_path in self.routes_dir.rglob("*.py"):
            if file_path.name.startswith("__"):
                continue

            try:
                # Convert file path to route pattern
                route_pattern, params = self._convert_file_path_to_route(file_path)

                # Load the module
                module = self._load_route_module(file_path)
                if module is None:
                    continue

                # Extract handlers
                handlers = self._extract_route_handlers(module, route_pattern, params)

                if not handlers:
                    continue

                # Register each handler
                for method, handler in handlers.items():
                    wrapped_handler = self._create_route_wrapper(handler, params)

                    # Add route to FastAPI app
                    self.app.add_api_route(
                        route_pattern,
                        wrapped_handler,
                        methods=[method],
                        name=f"{method.lower()}_{file_path.stem}",
                    )

                # Store route info
                self._routes.append(
                    {
                        "pattern": route_pattern,
                        "file_path": str(file_path),
                        "params": params,
                        "methods": list(handlers.keys()),
                    }
                )

            except Exception as e:
                print(f"Error loading route {file_path}: {e}")
                continue

    def get_routes(self) -> List[Dict[str, Any]]:
        """Get information about all registered routes."""
        return self._routes.copy()

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app


def create_file_router(routes_dir: str = "routes") -> FileBasedRouter:
    """Create and configure a file-based router."""
    router = FileBasedRouter(routes_dir)
    router.scan_routes()
    return router
