"""
Demo script showing how fastapi-mcp-openapi works.

This script demonstrates the core functionality of the library
without requiring all dependencies to be installed.
"""

import sys
import os

# Add the library to the path for demonstration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    
    # Import our library
    from fastapi_mcp_openapi import mount_mcp_openapi
    
    # Create a simple FastAPI app
    app = FastAPI(title="Demo API", version="1.0.0")
    
    class User(BaseModel):
        id: int
        name: str
        email: str
    
    # Add some endpoints
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Hello from Demo API!"}
    
    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        """Get a user by ID."""
        return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}
    
    @app.post("/users")
    async def create_user(user: User):
        """Create a new user."""
        return {"message": "User created", "user": user}
    
    # Mount the MCP tools
    mcp_server = mount_mcp_openapi(app, mcp_path="/mcp-demo")
    
    print("✓ FastAPI MCP OpenAPI library successfully mounted!")
    print(f"✓ Server name: {mcp_server.server_name}")
    print(f"✓ Available tools: {', '.join(mcp_server.list_tools())}")
    
    # Demonstrate the tools
    async def demo_tools():
        """Demonstrate the MCP tools."""
        
        print("\n--- Demo: list_endpoints tool ---")
        list_endpoints_tool = mcp_server.get_tool("list_endpoints")
        if list_endpoints_tool:
            try:
                endpoints = await list_endpoints_tool()
                print(f"Found {len(endpoints)} endpoints:")
                for endpoint in endpoints:
                    print(f"  - {endpoint['methods']} {endpoint['path']} ({endpoint['name']})")
                    if endpoint.get('summary'):
                        print(f"    Summary: {endpoint['summary']}")
            except Exception as e:
                print(f"Error calling list_endpoints: {e}")
        
        print("\n--- Demo: get_endpoint_docs tool ---")
        get_docs_tool = mcp_server.get_tool("get_endpoint_docs")
        if get_docs_tool:
            try:
                docs = await get_docs_tool("/users/{user_id}", "GET")
                endpoint_info = docs.get("endpoint", {})
                print("Documentation for GET /users/{user_id}:")
                print(f"  Summary: {endpoint_info.get('summary', 'N/A')}")
                print(f"  Description: {endpoint_info.get('description', 'N/A')}")
                print(f"  Parameters: {len(endpoint_info.get('parameters', []))}")
                print(f"  Responses: {list(endpoint_info.get('responses', {}).keys())}")
                
                # Show OpenAPI spec if available
                openapi_spec = docs.get("openapi_spec", {})
                if openapi_spec:
                    print(f"  OpenAPI spec available: {bool(openapi_spec.get('spec'))}")
                
            except Exception as e:
                print(f"Error calling get_endpoint_docs: {e}")
    
    # Run the demo
    import asyncio
    asyncio.run(demo_tools())
    
    print("\n--- Integration Info ---")
    print("To use this library in your FastAPI app:")
    print("1. pip install fastapi-mcp-openapi")
    print("2. from fastapi_mcp_openapi import mount_mcp_openapi")
    print("3. mount_mcp_openapi(app)")
    print("4. Your app will now have MCP endpoints for introspection!")
    
    print("\n--- Real Usage ---")
    print("In a real MCP environment, you would:")
    print("1. Start your FastAPI app with the library mounted")
    print("2. Connect an MCP client to the endpoints")
    print("3. Use the tools to discover and understand your API structure")
    
except ImportError as e:
    print(f"Dependencies not installed: {e}")
    print("This is a demo script showing the library structure.")
    print("To run the full demo, install the requirements:")
    print("pip install -r requirements.txt")
    
    # Show what the library provides even without dependencies
    print("\n--- Library Structure ---")
    print("fastapi-mcp-openapi provides:")
    print("1. mount_mcp_openapi() - Mount MCP tools to your FastAPI app")
    print("2. create_standalone_mcp_server() - Create a standalone MCP server")
    print("3. Two MCP tools:")
    print("   - list_endpoints: List all user-defined endpoints")
    print("   - get_endpoint_docs: Get detailed docs for specific endpoints")
    
    print("\n--- Installation ---")
    print("pip install fastapi-mcp-openapi")
    
except Exception as e:
    print(f"Demo error: {e}")
    print("This demonstrates the library structure and capabilities.")
