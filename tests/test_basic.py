"""Tests for fastapi-mcp-openapi library."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fastapi_mcp_openapi import mount_mcp_openapi, create_standalone_mcp_server


class User(BaseModel):
    id: int
    name: str


def create_test_app():
    """Create a test FastAPI app with some endpoints."""
    app = FastAPI(title="Test API", version="1.0.0")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Hello World"}
    
    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        """Get a user by ID."""
        return {"id": user_id, "name": f"User {user_id}"}
    
    @app.post("/users")
    async def create_user(user: User):
        """Create a new user."""
        return user
    
    @app.get("/health")
    async def health():
        """Health check."""
        return {"status": "ok"}
    
    return app


def test_mount_mcp_openapi():
    """Test mounting MCP OpenAPI tools to a FastAPI app."""
    app = create_test_app()
    
    # Mount the MCP tools
    mcp_server = mount_mcp_openapi(app, mcp_path="/test-mcp")
    
    assert mcp_server is not None
    
    # Test that the app still works
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_standalone_mcp_server():
    """Test creating a standalone MCP server."""
    app = create_test_app()
    
    # Create standalone server
    mcp_server = create_standalone_mcp_server(
        app,
        server_name="test-server",
        server_version="1.0.0"
    )
    
    assert mcp_server is not None
    
    # Get the MCP app
    mcp_app = mcp_server.get_mcp_app()
    assert mcp_app is not None


def test_custom_endpoint_filter():
    """Test custom endpoint filtering."""
    app = create_test_app()
    
    def custom_filter(route, mcp_path):
        """Custom filter that excludes health endpoint."""
        if hasattr(route, 'path') and route.path == '/health':
            return False
        return True
    
    # Mount with custom filter
    mcp_server = mount_mcp_openapi(
        app,
        endpoint_filter=custom_filter,
        mcp_path="/filtered-mcp"
    )
    
    assert mcp_server is not None


def test_multiple_http_methods():
    """Test endpoint with multiple HTTP methods."""
    app = FastAPI()
    
    @app.get("/items/{item_id}")
    @app.put("/items/{item_id}")
    async def handle_item(item_id: int):
        """Handle item with GET and PUT."""
        return {"item_id": item_id}
    
    mcp_server = mount_mcp_openapi(app)
    assert mcp_server is not None


if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    try:
        test_mount_mcp_openapi()
        print("✓ test_mount_mcp_openapi passed")
    except Exception as e:
        print(f"✗ test_mount_mcp_openapi failed: {e}")
    
    try:
        test_create_standalone_mcp_server()
        print("✓ test_create_standalone_mcp_server passed")
    except Exception as e:
        print(f"✗ test_create_standalone_mcp_server failed: {e}")
    
    try:
        test_custom_endpoint_filter()
        print("✓ test_custom_endpoint_filter passed")
    except Exception as e:
        print(f"✗ test_custom_endpoint_filter failed: {e}")
    
    try:
        test_multiple_http_methods()
        print("✓ test_multiple_http_methods passed")
    except Exception as e:
        print(f"✗ test_multiple_http_methods failed: {e}")
    
    print("Basic tests completed!")
