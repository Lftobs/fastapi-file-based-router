# Request Body Handling in File-Based Router

## How It Works

The file-based router handles request bodies through **FastAPI's dependency injection system**. The router preserves the original function signatures, allowing FastAPI to automatically handle:

- **JSON Request Bodies** (Pydantic models)
- **Query Parameters** 
- **Headers**
- **Form Data**
- **Raw Request Access**

## Implementation Location

**File**: `file_router.py`
**Method**: `_create_route_wrapper()` (lines 125-170)

### Key Features:

1. **No Path Parameters**: Returns handler as-is → Full FastAPI dependency injection
2. **With Path Parameters**: Preserves non-path parameters → Hybrid approach

```python
def _create_route_wrapper(self, handler: Callable, params: Dict[str, Any]):
    if not params:
        # No path parameters - return handler as-is for FastAPI to handle
        return handler
    
    # For routes with path parameters, preserve other parameter types
    # (request bodies, query params, headers, etc.)
```

## Request Body Examples

### 1. JSON Request Body (Pydantic Models)

```python
# routes/users/index.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

def post(user_data: UserCreate):
    return {"user": user_data.dict()}
```

**Usage**: `POST /users` with JSON body

### 2. Path Parameters + Request Body

```python
# routes/users/[id:int].py
def put(id: int, user_data: UserUpdate):
    # id from URL path, user_data from JSON body
    return {"id": id, "data": user_data}
```

**Usage**: `PUT /users/123` with JSON body

### 3. Query Parameters + Headers

```python
# routes/posts.py
from fastapi import Query, Header

def get(
    limit: int = Query(10),
    authorization: str = Header(None)
):
    return {"limit": limit, "has_auth": authorization is not None}
```

**Usage**: `GET /posts?limit=5` with headers

### 4. Multiple Body Parts

```python
def put(
    post_data: PostData = Body(...),
    comments: list[CommentData] = Body([]),
    metadata: dict = Body({})
):
    return {"post": post_data, "comments": comments, "metadata": metadata}
```

### 5. Raw Request Access

```python
from fastapi import Request

async def patch(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    return {"body_size": len(body), "headers": headers}
```

## Testing Request Bodies

```bash
# JSON Body
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'

# Query Parameters  
curl "http://localhost:8000/posts?limit=5&published_only=true"

# Headers + Body
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Post", "content": "Content here"}'
```

## Supported Parameter Types

| Type | Example | Usage |
|------|---------|-------|
| **Path** | `id: int` | From URL: `/users/{id}` |
| **JSON Body** | `user: UserModel` | From request body |
| **Query** | `limit: int = Query(10)` | From URL: `?limit=10` |
| **Header** | `auth: str = Header(None)` | From HTTP headers |
| **Form** | `name: str = Form(...)` | From form data |
| **Raw** | `request: Request` | Full request access |

The router automatically handles all FastAPI parameter types while adding file-based routing capabilities! 🚀