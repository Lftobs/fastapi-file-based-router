"""
Module: file_router.py
This module implements a file-based router for FastAPI, allowing dynamic route registration based on file structure.
It supports static, dynamic, typed, slug, and catch-all routes, along with custom tagging functionality.
"""

import inspect
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any, Callable
from fastapi import FastAPI

from constants import FUNCTIONS_TO_SKIP


class FileBasedRouter:
    """
    Main class for the file-based router.
    This class handles:
    - Scanning the routes directory
    - Converting file paths to route patterns
    - Loading route modules
    - Extracting route handlers
    - Registering routes with FastAPI
    - Custom tag assignment for routes
    - Providing access to registered routes and the FastAPI app instance
    """

    def __init__(self, routes_dir: str = "routes"):
        self.routes_dir = Path(routes_dir)
        self.app = FastAPI()
        self._routes: List[Dict[str, Any]] = []
        self._custom_tags: Dict[str, str] = {}

    def _generate_tag_from_route(self, route_pattern: str, file_path: Path) -> str:
        """
        Generate a tag for the route based on the route pattern.

        Priority:
        1. Specific file path custom tag if set
        2. Directory-level custom tag if set
        3. First path segment (e.g., /users/1 -> "users")
        4. "default" for root routes
        """
        file_path_str = str(file_path)

        # Check for specific file path custom tag override
        if file_path_str in self._custom_tags:
            return self._custom_tags[file_path_str]

        # Check for directory-level custom tag override
        # Goes up the directory tree to find a matching custom tag
        current_path = file_path.parent
        while current_path != self.routes_dir.parent:
            dir_path_str = str(current_path)
            if dir_path_str in self._custom_tags:
                return self._custom_tags[dir_path_str]
            current_path = current_path.parent

        # Extract first path segment
        parts = [
            part
            for part in route_pattern.split("/")
            if part and not part.startswith("{")
        ]

        if parts:
            return parts[0]
        else:
            return "default"

    def set_custom_tag(self, path: str, tag: str):
        """
        Set a custom tag for a specific route file or directory.

        Examples:
        - router.set_custom_tag("routes/users/[id].py", "user-details") # Specific file
        - router.set_custom_tag("routes/users", "user-management")      # All files in directory
        """
        self._custom_tags[path] = tag

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
                param_type = "str"
            return param_name, param_type, False

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

        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        method_names = [method.lower() for method in methods]

        for method in methods:
            handler_name = method.lower()
            if hasattr(module, handler_name):
                handler = getattr(module, handler_name)
                if callable(handler):
                    handlers[method] = handler

        # Check for unrecognized function names and log a warning
        for name in dir(module):
            if name.startswith("_"):
                continue

            attr = getattr(module, name)
            if callable(attr) and inspect.isfunction(attr) and name not in method_names:
                if name not in FUNCTIONS_TO_SKIP:
                    logger = logging.getLogger("uvicorn.error")
                    logger.warning(
                        "Function '%s' in %s is not a recognized HTTP method handler",
                        name,
                        module.__name__,
                    )

        return handlers

    def _create_route_wrapper(self, handler: Callable, params: Dict[str, Any]):
        """Create a wrapper function that properly handles path parameters."""
        sig = inspect.signature(handler)

        if not params:
            # create simple wrapper that preserves signature if not path parameters
            # This allows FastAPI to handle request bodies, query params, headers, etc.
            if inspect.iscoroutinefunction(handler):

                async def simple_wrapper(*args, **kwargs):
                    return await handler(*args, **kwargs)
            else:

                def simple_wrapper(*args, **kwargs):
                    return handler(*args, **kwargs)

            # Preserve the original signature for FastAPI dependency injection
            simple_wrapper.__signature__ = sig
            return simple_wrapper

        original_params = list(sig.parameters.values())
        path_param_names = set(params.keys())

        # Build new signature preserving non-path parameters as-is
        new_params = []

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

        for param in original_params:
            if param.name not in path_param_names:
                new_params.append(param)

        # wrapper function to preserves FastAPI's dependency injection
        if inspect.iscoroutinefunction(handler):

            async def param_wrapper(*args, **kwargs):
                return await handler(*args, **kwargs)
        else:
            def param_wrapper(*args, **kwargs):
                return handler(*args, **kwargs)

        # Set the correct signature for FastAPI
        new_sig = inspect.Signature(new_params)
        param_wrapper.__signature__ = new_sig

        return param_wrapper

    def scan_routes(self):
        """Scan the routes directory and register all route files."""
        if not self.routes_dir.exists():
            raise FileNotFoundError(f"Routes directory '{self.routes_dir}' not found")

        for file_path in self.routes_dir.rglob("*.py"):
            if file_path.name.startswith("__"):
                continue

            try:
                route_pattern, params = self._convert_file_path_to_route(file_path)

                module = self._load_route_module(file_path)
                if module is None:
                    continue

                handlers = self._extract_route_handlers(module, route_pattern, params)

                if not handlers:
                    continue

                # Register each handler
                for method, handler in handlers.items():
                    wrapped_handler = self._create_route_wrapper(handler, params)

                    tag = self._generate_tag_from_route(route_pattern, file_path)

                    self.app.add_api_route(
                        route_pattern,
                        wrapped_handler,
                        methods=[method],
                        name=f"{method.lower()}_{file_path.stem}",
                        tags=[tag],
                    )

                # Store route info
                self._routes.append(
                    {
                        "pattern": route_pattern,
                        "file_path": str(file_path),
                        "params": params,
                        "methods": list(handlers.keys()),
                        "tag": tag,
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


def file_router(routes_dir: str = "routes") -> FileBasedRouter:
    """Create and configure a file-based router."""
    router = FileBasedRouter(routes_dir)
    router.scan_routes()
    return router
