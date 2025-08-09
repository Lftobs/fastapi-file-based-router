#!/usr/bin/env python3
"""
Example demonstrating custom tag functionality in the file-based router.

This shows how to:
1. Use automatic tag assignment based on route structure
2. Override tags for specific routes
3. View the resulting tag assignments
"""

from file_router import file_router


def main():
    # Create router with automatic tag assignment
    router = file_router("routes")

    print("=== Default Tag Assignment ===")
    routes = router.get_routes()
    for route in sorted(routes, key=lambda x: x["pattern"]):
        print(f"{route['pattern']:<30} -> tag: '{route['tag']}'")

    print("\n=== Custom Tag Override Example ===")

    # Override some tags
    router.set_custom_tag("routes/api/v1/health.py", "health-check")
    router.set_custom_tag("routes/users", "user-management")
    # router.set_custom_tag("routes/users/[:id].py", "user-m2")

    # Re-scan routes to apply custom tags
    router._routes.clear()  # Clear existing routes
    router.scan_routes()  # Re-scan with custom tags

    routes = router.get_routes()
    for route in sorted(routes, key=lambda x: x["pattern"]):
        print(f"{route['pattern']:<30} -> tag: '{route['tag']}'")

    print("\n=== Tag Summary ===")
    tags = {}
    for route in routes:
        tag = route["tag"]
        if tag not in tags:
            tags[tag] = []
        tags[tag].append(route["pattern"])

    for tag, patterns in sorted(tags.items()):
        print(f"\nTag '{tag}':")
        for pattern in patterns:
            print(f"  - {pattern}")


if __name__ == "__main__":
    main()
