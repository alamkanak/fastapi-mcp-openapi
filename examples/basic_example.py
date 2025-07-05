"""
Basic example of using fastapi-mcp-openapi.

This example shows how to mount the MCP OpenAPI tools to a FastAPI application
with default settings.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import the library
from fastapi_mcp_openapi import mount_mcp_openapi

app = FastAPI(
    title="Example API",
    description="A simple API to demonstrate fastapi-mcp-openapi",
    version="1.0.0"
)

# Mount the MCP OpenAPI tools (this will add /mcp endpoints)
mcp_server = mount_mcp_openapi(app)


# Define some Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None


class CreateUserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


# Sample data
users_db = [
    User(id=1, name="John Doe", email="john@example.com", age=30),
    User(id=2, name="Jane Smith", email="jane@example.com", age=25),
]


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the Example API! Visit /docs to see the API documentation."}


@app.get("/users", response_model=List[User], tags=["users"])
async def list_users():
    """
    Get all users.
    
    Returns a list of all users in the system.
    """
    return users_db


@app.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user(user_id: int):
    """
    Get a user by ID.
    
    Retrieves a specific user by their unique identifier.
    
    Args:
        user_id: The unique identifier of the user
    
    Returns:
        User object if found
    
    Raises:
        HTTPException: 404 if user not found
    """
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", response_model=User, tags=["users"])
async def create_user(user_data: CreateUserRequest):
    """
    Create a new user.
    
    Creates a new user with the provided information.
    
    Args:
        user_data: User information for creating the new user
    
    Returns:
        Created user object with assigned ID
    """
    new_id = max(user.id for user in users_db) + 1 if users_db else 1
    new_user = User(id=new_id, **user_data.dict())
    users_db.append(new_user)
    return new_user


@app.put("/users/{user_id}", response_model=User, tags=["users"])
async def update_user(user_id: int, user_data: UpdateUserRequest):
    """
    Update an existing user.
    
    Updates the specified user with the provided information.
    Only provided fields will be updated.
    
    Args:
        user_id: The unique identifier of the user to update
        user_data: Updated user information
    
    Returns:
        Updated user object
    
    Raises:
        HTTPException: 404 if user not found
    """
    for i, user in enumerate(users_db):
        if user.id == user_id:
            update_data = user_data.dict(exclude_unset=True)
            updated_user = user.copy(update=update_data)
            users_db[i] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int):
    """
    Delete a user.
    
    Removes the specified user from the system.
    
    Args:
        user_id: The unique identifier of the user to delete
    
    Returns:
        Success message
    
    Raises:
        HTTPException: 404 if user not found
    """
    for i, user in enumerate(users_db):
        if user.id == user_id:
            users_db.pop(i)
            return {"message": f"User {user_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "users_count": len(users_db)}


if __name__ == "__main__":
    import uvicorn
    print("Starting Example API...")
    print("API documentation: http://localhost:8000/docs")
    print("MCP endpoints: http://localhost:8000/mcp")
    print()
    print("Try the MCP tools:")
    print("1. list_endpoints - Get all available endpoints")
    print("2. get_endpoint_docs - Get detailed docs for a specific endpoint")
    uvicorn.run(app, host="0.0.0.0", port=8000)
