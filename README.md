# FastAPI File-Based Router

A powerful file-based routing system for FastAPI that automatically maps file structures to API routes with support for dynamic parameters.

> [!NOTE]
> You can use this to fuck with your personal or a friends repo but do not push to prod :)  

## Features

- **Static Routes**: `routes/index.py` → `GET /`
- **Dynamic Routes**: `routes/users/[id].py` → `GET /users/{id}`
- **Typed Parameters**: `routes/posts/[id:int].py` → `GET /posts/{id:int}`
- **Slug Routes**: `routes/blog/[slug:].py` → `GET /blog/{slug}`
- **Catch-all Routes**: `routes/files/[...path].py` → `GET /files/{path:path}`
- **Multiple HTTP Methods**: Support for GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- **Async Support**: Both sync and async route handlers
- **Automatic Route Discovery**: Scans directory structure automatically

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the demo server:**
   ```bash
   python main.py
   ```

3. **Visit the API:**
   - Main page: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Example routes:
     - `GET /users` - List all users
     - `GET /users/1` - Get user by ID
     - `GET /blog/hello-world` - Get blog post by slug
     - `GET /files/documents/readme.txt` - Get file (catch-all)

## Route File Structure

```
routes/
├── index.py                    # GET /
├── users/
│   ├── index.py               # GET /users
│   └── [id:int].py           # GET /users/{id:int}
├── blog/
│   └── [slug:].py            # GET /blog/{slug}
├── files/
│   └── [...path].py          # GET /files/{path:path}
└── api/
    └── v1/
        └── health.py          # GET /api/v1/health
```

> [!IMPORTANT]
> The files in the directory used for the routing (the example above uses the routes dir) should strictly only contain the method call for the endpoint.
> Example below:

## Route Handler Examples

### Basic Route (`routes/users/index.py`)
```python
def get():
    return {"users": []}

def post():
    return {"message": "User created"}
```

### Dynamic Route (`routes/users/[id:int].py`)
```python
def get(id: int):
    return {"user_id": id}

def put(id: int):
    return {"updated_user": id}
```

### Async Route (`routes/async.py`)
```python
import asyncio

async def get():
    await asyncio.sleep(0.1)
    return {"async": True}
```

### Catch-all Route (`routes/files/[...path].py`)
```python
def get(path: str):
    return {"path": path, "segments": path.split("/")}
```

## Dynamic Route Types

| Pattern | Example File | Route | Parameter Type |
|---------|-------------|-------|----------------|
| `[id]` | `[id].py` | `/{id}` | string |
| `[id:int]` | `[id:int].py` | `/{id:int}` | integer |
| `[slug:]` | `[slug:].py` | `/{slug}` | string (slug) |
| `[...rest]` | `[...rest].py` | `/{rest:path}` | catch-all path |

## Usage in Your Project

```python
from file_router import file_router

# Create router
router = file_router("routes")
app = router.get_app()

# Or use the class directly
from file_router import FileBasedRouter

router = FileBasedRouter("routes")
router.scan_routes()
app = router.get_app()
```

## Running Tests

```bash
pytest test_file_router.py -v
```

## API Documentation

The FastAPI automatic documentation is available at `/docs` when running the server.

## License

MIT License
