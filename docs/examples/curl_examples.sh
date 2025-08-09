#!/bin/bash
# Working curl examples for the file-based router

echo "🌐 Curl Examples for File-Based Router"
echo "======================================"

# First, start the server (run this in another terminal)
echo "1. Start the server first:"
echo "   python server.py"
echo ""

echo "2. Then run these curl commands:"
echo ""

echo "📤 POST request with JSON body:"
echo 'curl -X POST http://localhost:8000/users \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"name": "John Doe", "email": "john@example.com"}'"'"
echo ""

echo "🔄 PUT request with JSON body:"
echo 'curl -X PUT http://localhost:8000/users/1 \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"name": "Jane Smith", "email": "jane@example.com"}'"'"
echo ""

echo "🔍 GET request with query parameters:"
echo 'curl "http://localhost:8000/posts?limit=5&published_only=true"'
echo ""

echo "📝 Complex POST with headers:"
echo 'curl -X POST http://localhost:8000/posts \'
echo '  -H "Content-Type: application/json" \'
echo '  -H "Authorization: Bearer my-token" \'
echo '  -d '"'"'{
    "title": "My Blog Post", 
    "content": "This is the content",
    "tags": ["fastapi", "python"],
    "published": true
  }'"'"
echo ""

echo "🎯 Simple GET requests:"
echo "curl http://localhost:8000/"
echo "curl http://localhost:8000/users"  
echo "curl http://localhost:8000/users/1"
echo "curl http://localhost:8000/blog/hello-world"
echo "curl http://localhost:8000/files/documents/readme.txt"
echo "curl http://localhost:8000/api/v1/health"