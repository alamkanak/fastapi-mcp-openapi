"""
Simple example of using FastAPI MCP OpenAPI library.

This example demonstrates the basic usage of the library with a minimal FastAPI app.
"""

from fastapi import FastAPI

from fastapi_mcp_openapi import FastAPIMCPOpenAPI

# Create FastAPI app
app = FastAPI(
    title="Simple API",
    version="1.0.0",
    description="A simple API to demonstrate FastAPI MCP OpenAPI",
)


@app.get("/")
async def root():
    """Root endpoint that returns a greeting."""
    return {"message": "Hello from FastAPI MCP OpenAPI!"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a user by their ID."""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
    }


@app.post("/users/")
async def create_user(name: str, email: str):
    """Create a new user with name and email."""
    return {"message": f"User '{name}' created with email '{email}'"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FastAPI MCP OpenAPI Demo"}


# Initialize the MCP server
mcp = FastAPIMCPOpenAPI(app)

# Get information about the MCP integration
print("FastAPI MCP OpenAPI Example")
print("=" * 40)
info = mcp.get_mcp_info()
print(f"Server Name: {info['server_name']}")
print(f"Version: {info['server_version']}")
print(f"Mount Path: {info['mount_path']}")
print("\nAvailable MCP Tools:")
for tool in info["tools"]:
    print(f"  - {tool['name']}: {tool['description']}")

print("\nMCP Endpoints:")
print(f"  - Main: http://localhost:8000{info['mount_path']}/")
print(f"  - Health: http://localhost:8000{info['health_endpoint']}")

if __name__ == "__main__":
    import uvicorn

    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Root: http://localhost:8000/")
    print("MCP Server: http://localhost:8000/mcp/")

    uvicorn.run(app, host="127.0.0.1", port=8000)
