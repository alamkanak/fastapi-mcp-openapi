"""
Test configuration and fixtures for FastAPI MCP OpenAPI tests.
"""

import pytest
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class User(BaseModel):
    """Test user model."""

    id: int
    name: str
    email: str


class UserCreate(BaseModel):
    """Test user creation model."""

    name: str
    email: str


@pytest.fixture
def basic_app():
    """Create a basic FastAPI app for testing."""
    app = FastAPI(
        title="Test API",
        version="1.0.0",
        description="A test API for FastAPI MCP OpenAPI",
    )

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Hello World"}

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        """Get a user by ID."""
        return {"user_id": user_id, "name": f"User {user_id}"}

    @app.post("/users/", response_model=User)
    async def create_user(user: UserCreate):
        """Create a new user."""
        return User(id=1, name=user.name, email=user.email)

    return app


@pytest.fixture
def mcp_instance(basic_app):
    """Create a FastAPIMCPOpenAPI instance with basic app."""
    return FastAPIMCPOpenAPI(basic_app)


@pytest.fixture
def custom_mcp_instance(basic_app):
    """Create a FastAPIMCPOpenAPI instance with custom configuration."""
    return FastAPIMCPOpenAPI(
        app=basic_app,
        mount_path="/custom-mcp",
        server_name="Custom Test Server",
        server_version="2.0.0",
        section_name="custom",
        list_endpoints_tool_name="customListEndpoints",
        get_endpoint_docs_tool_name="customGetEndpointDocs",
    )


@pytest.fixture
def empty_app():
    """Create an empty FastAPI app."""
    return FastAPI(title="Empty API", version="1.0.0")


@pytest.fixture
def complex_app():
    """Create a more complex FastAPI app with various endpoint types."""
    app = FastAPI(
        title="Complex API", version="2.0.0", description="A complex test API"
    )

    @app.get("/")
    async def root():
        return {"message": "Complex API"}

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        """Get user by ID with detailed info."""
        return {"user_id": user_id, "name": f"User {user_id}"}

    @app.post("/users/")
    async def create_user(user: UserCreate):
        """Create a new user account."""
        return {"id": 1, "name": user.name, "email": user.email}

    @app.put("/users/{user_id}")
    async def update_user(user_id: int, user: UserCreate):
        """Update an existing user."""
        return {"id": user_id, "name": user.name, "email": user.email}

    @app.delete("/users/{user_id}")
    async def delete_user(user_id: int):
        """Delete a user."""
        return {"message": f"User {user_id} deleted"}

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app
