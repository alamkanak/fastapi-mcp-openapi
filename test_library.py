"""
Test script for FastAPI MCP OpenAPI library.

This script tests the core functionality of the library to ensure
the MCP tools work correctly.
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_mcp_openapi import FastAPIMCPOpenAPI

# Create a simple test FastAPI app
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

def test_library_functionality():
    """Test the core library functionality."""
    print("Testing FastAPI MCP OpenAPI Library")
    print("=" * 40)
    
    # Test library initialization
    print("\n1. Testing library initialization:")
    print("-" * 30)
    
    try:
        mcp = FastAPIMCPOpenAPI(app, mount_path="/mcp")
        print("✅ FastAPIMCPOpenAPI initialized successfully")
        
        # Test MCP server info
        info = mcp.get_mcp_info()
        print(f"✅ Server Name: {info['server_name']}")
        print(f"✅ Server Version: {info['server_version']}")
        print(f"✅ Mount Path: {info['mount_path']}")
        print(f"✅ Available Tools: {len(info['tools'])}")
        for tool in info['tools']:
            print(f"   - {tool['name']}: {tool['description']}")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False
    
    # Test endpoint introspection
    print("\n2. Testing endpoint introspection:")
    print("-" * 30)
    
    try:
        # Count user-defined endpoints (excluding MCP endpoints)
        user_endpoints = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                if not route.path.startswith("/mcp"):
                    user_endpoints.append({
                        "path": route.path,
                        "methods": list(route.methods),
                        "name": route.name
                    })
        
        print(f"✅ Found {len(user_endpoints)} user-defined endpoints:")
        for endpoint in user_endpoints:
            print(f"   - {endpoint['methods']} {endpoint['path']} ({endpoint['name']})")
        
    except Exception as e:
        print(f"❌ Error during endpoint introspection: {e}")
        return False
    
    # Test OpenAPI schema generation
    print("\n3. Testing OpenAPI schema generation:")
    print("-" * 30)
    
    try:
        from fastapi.openapi.utils import get_openapi
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        if "paths" in openapi_schema:
            endpoint_count = len(openapi_schema["paths"])
            print(f"✅ OpenAPI schema generated with {endpoint_count} endpoints")
            
            # Test specific endpoint docs
            if "/" in openapi_schema["paths"]:
                root_endpoint = openapi_schema["paths"]["/"]
                if "get" in root_endpoint:
                    print("✅ Root endpoint documentation available")
                    operation = root_endpoint["get"]
                    print(f"   Summary: {operation.get('summary', 'N/A')}")
                else:
                    print("❌ Root endpoint GET method not found")
            else:
                print("❌ Root endpoint not found in OpenAPI schema")
        else:
            print("❌ No paths found in OpenAPI schema")
            return False
            
    except Exception as e:
        print(f"❌ Error during OpenAPI schema generation: {e}")
        return False
    
    print("\n✅ All tests completed successfully!")
    print("\nNext steps:")
    print("- Run the example app to test the full integration")
    print("- Use an MCP client to test the actual tools")
    print("- Check the mounted endpoints at /mcp/")
    
    return True

if __name__ == "__main__":
    success = test_library_functionality()
    if not success:
        exit(1)
