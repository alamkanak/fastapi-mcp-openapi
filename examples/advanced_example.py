"""
Example FastAPI application demonstrating FastAPI MCP OpenAPI library.

This example shows how to integrate the library with a real FastAPI app
that has various types of endpoints.
"""

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi_mcp_openapi.core import FastAPIMCPOpenAPI

# Create FastAPI app
app = FastAPI(
    title="Example API",
    version="1.0.0",
    description="An example API to demonstrate FastAPI MCP OpenAPI integration",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int | None = None


class UserCreate(BaseModel):
    name: str
    email: str
    age: int | None = None


class Post(BaseModel):
    id: int
    title: str
    content: str
    author_id: int


# Sample data
users_db = [
    User(id=1, name="Alice", email="alice@example.com", age=30),
    User(id=2, name="Bob", email="bob@example.com", age=25),
]

posts_db = [
    Post(id=1, title="Hello World", content="This is my first post", author_id=1),
    Post(id=2, title="FastAPI Tips", content="Some useful FastAPI tips", author_id=2),
]


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Check if the API is healthy."""
    return {"status": "healthy", "version": "1.0.0"}


# User endpoints
@app.get("/users/", response_model=list[User], tags=["users"])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
):
    """Get a list of users with pagination."""
    return users_db[skip : skip + limit]


@app.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user(
    user_id: int = Path(..., description="The ID of the user to retrieve"),
):
    """Get a specific user by ID."""
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/", response_model=User, tags=["users"])
async def create_user(user: UserCreate):
    """Create a new user."""
    new_id = max(u.id for u in users_db) + 1 if users_db else 1
    new_user = User(id=new_id, **user.dict())
    users_db.append(new_user)
    return new_user


@app.put("/users/{user_id}", response_model=User, tags=["users"])
async def update_user(
    user_update: UserCreate,
    user_id: int = Path(..., description="The ID of the user to update"),
):
    """Update an existing user."""
    for i, user in enumerate(users_db):
        if user.id == user_id:
            updated_user = User(id=user_id, **user_update.dict())
            users_db[i] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(
    user_id: int = Path(..., description="The ID of the user to delete"),
):
    """Delete a user."""
    for i, user in enumerate(users_db):
        if user.id == user_id:
            deleted_user = users_db.pop(i)
            return {"message": f"User {deleted_user.name} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


# Post endpoints
@app.get("/posts/", response_model=list[Post], tags=["posts"])
async def list_posts():
    """Get a list of all posts."""
    return posts_db


@app.get("/posts/{post_id}", response_model=Post, tags=["posts"])
async def get_post(
    post_id: int = Path(..., description="The ID of the post to retrieve"),
):
    """Get a specific post by ID."""
    for post in posts_db:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.get("/users/{user_id}/posts", response_model=list[Post], tags=["posts", "users"])
async def get_user_posts(
    user_id: int = Path(..., description="The ID of the user whose posts to retrieve"),
):
    """Get all posts by a specific user."""
    user_posts = [post for post in posts_db if post.author_id == user_id]
    if not user_posts:
        # Check if user exists
        user_exists = any(user.id == user_id for user in users_db)
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
    return user_posts


# Search endpoint with query parameters
@app.get("/search/users", response_model=list[User], tags=["search"])
async def search_users(
    q: str = Query(..., description="Search query for user names or emails"),
    min_age: int | None = Query(None, description="Minimum age filter"),
    max_age: int | None = Query(None, description="Maximum age filter"),
):
    """Search users by name or email with optional age filters."""
    results = []
    for user in users_db:
        # Check if query matches name or email
        if q.lower() in user.name.lower() or q.lower() in user.email.lower():
            # Apply age filters if provided
            if min_age is not None and user.age is not None and user.age < min_age:
                continue
            if max_age is not None and user.age is not None and user.age > max_age:
                continue
            results.append(user)
    return results


# Create and mount the MCP server
mcp = FastAPIMCPOpenAPI(
    app=app,
    mount_path="/mcp",
    server_name="Example API MCP Server",
    server_version="1.0.0",
)

if __name__ == "__main__":
    import uvicorn

    print("Starting Example API with FastAPI MCP OpenAPI integration...")
    print("API Documentation: http://localhost:8000/docs")
    print("MCP Server: http://localhost:8000/mcp")
    print("")
    print("Available MCP Tools:")
    print("1. list_endpoints - Get all available API endpoints")
    print("2. get_endpoint_docs - Get detailed OpenAPI docs for specific endpoint")
    print("")
    print("Example endpoints to explore:")
    print("- GET /users/ - List users with pagination")
    print("- GET /users/{user_id} - Get specific user")
    print("- POST /users/ - Create new user")
    print("- GET /posts/ - List all posts")
    print("- GET /search/users - Search users with filters")

    uvicorn.run(app, host="0.0.0.0", port=8000)
