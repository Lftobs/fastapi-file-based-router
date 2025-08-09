"""
Test script to verify the curl error is fixed.
"""

from file_router import file_router
from fastapi.testclient import TestClient


def test_curl_error_fix():
    print("🔧 Testing curl error fix...")

    # Create router
    router = file_router("routes")
    client = TestClient(router.get_app())

    test_cases = [
        {
            "name": "POST /users with JSON body",
            "method": "POST",
            "url": "/users",
            "json": {"name": "Test User", "email": "test@example.com"},
        },
        {
            "name": "PUT /users/1 with JSON body",
            "method": "PUT",
            "url": "/users/1",
            "json": {"name": "Updated User", "email": "updated@example.com"},
        },
        {
            "name": "GET /posts with query params",
            "method": "GET",
            "url": "/posts",
            "params": {"limit": 5, "published_only": True},
        },
        {
            "name": "POST /posts with complex body",
            "method": "POST",
            "url": "/posts",
            "json": {
                "title": "Test Post",
                "content": "Test content",
                "tags": ["test"],
                "published": True,
            },
            "headers": {"Authorization": "Bearer test-token"},
        },
    ]

    print("\n📋 Test Results:")
    print("-" * 50)

    all_passed = True
    for test in test_cases:
        try:
            if test["method"] == "GET":
                response = client.get(test["url"], params=test.get("params", {}))
            elif test["method"] == "POST":
                response = client.post(
                    test["url"], json=test.get("json"), headers=test.get("headers", {})
                )
            elif test["method"] == "PUT":
                response = client.put(test["url"], json=test.get("json"))

            status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
            print(f"{status} {test['name']} -> {response.status_code}")

            if response.status_code != 200:
                all_passed = False
                print(f"     Error: {response.text}")

        except Exception as e:
            print(f"❌ FAIL {test['name']} -> Exception: {e}")
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("🎉 All tests passed! The curl error is fixed.")
    else:
        print("❌ Some tests failed. Check the errors above.")

    return all_passed


if __name__ == "__main__":
    test_curl_error_fix()
