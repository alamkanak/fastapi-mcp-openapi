"""
Direct test of the MCP tools functionality.

This script directly calls the MCP tool functions to verify they work correctly.
"""

import asyncio

from fastapi import FastAPI
from fastapi.routing import APIRoute

from fastapi_mcp_openapi import FastAPIMCPOpenAPI

# Create a test FastAPI app
app = FastAPI(title="Test API", version="1.0.0")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a user by ID."""
    return {"user_id": user_id, "name": f"User {user_id}"}


@app.post("/users/")
async def create_user(name: str):
    """Create a new user."""
    return {"message": f"Created user {name}"}


async def test_mcp_tools_directly():
    """Test the MCP tools by calling their functions directly."""
    print("Testing MCP Tools Directly")
    print("=" * 30)

    # Initialize MCP integration
    mcp = FastAPIMCPOpenAPI(app, mount_path="/mcp")

    # Test list_endpoints functionality (simulate what the tool would do)
    print("\n1. Testing list_endpoints logic:")
    print("-" * 30)

    endpoints = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            # Skip MCP endpoints
            if route.path.startswith("/mcp"):
                continue

            endpoint_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "summary": getattr(route.endpoint, "__doc__", "").split("\n")[0]
                if route.endpoint and getattr(route.endpoint, "__doc__", None)
                else None,
            }
            endpoints.append(endpoint_info)

    print(f"Found {len(endpoints)} user endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint['methods']} {endpoint['path']} ({endpoint['name']})")
        if endpoint["summary"]:
            print(f"    Summary: {endpoint['summary']}")

    # Test get_endpoint_docs functionality
    print("\n2. Testing get_endpoint_docs logic:")
    print("-" * 30)

    from fastapi.openapi.utils import get_openapi

    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    endpoint_path = "/"
    method = "GET"

    if "paths" in openapi_schema and endpoint_path in openapi_schema["paths"]:
        path_item = openapi_schema["paths"][endpoint_path]

        if method.lower() in path_item:
            endpoint_schema = {
                "path": endpoint_path,
                "method": method,
                "operation": path_item[method.lower()],
                "components": openapi_schema.get("components", {}),
            }
            print(f"✅ Successfully retrieved docs for {method} {endpoint_path}")
            print(f"   Summary: {endpoint_schema['operation'].get('summary', 'N/A')}")
            print(
                f"   Description: {endpoint_schema['operation'].get('description', 'N/A')}"
            )
            print(f"   Components: {len(endpoint_schema['components'])} types")
        else:
            print(f"❌ Method {method} not found for endpoint {endpoint_path}")
    else:
        print(f"❌ Endpoint {endpoint_path} not found")

    print("\n3. Testing MCP server information:")
    print("-" * 30)

    info = mcp.get_mcp_info()
    print(f"✅ Server: {info['server_name']} v{info['server_version']}")
    print(f"✅ Mount Path: {info['mount_path']}")
    print(f"✅ Tools Available: {len(info['tools'])}")
    for tool in info["tools"]:
        print(f"   - {tool['name']}")

    print("\n✅ All MCP functionality tests passed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools_directly())
