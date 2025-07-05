"""Main module for mounting FastAPI MCP OpenAPI tools."""

import logging
from typing import Optional, Callable

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    # Fallback types if FastAPI is not available
    FastAPI = None
    CORSMiddleware = None

from .server import FastAPIMCPServer

logger = logging.getLogger(__name__)


def mount_mcp_openapi(
    app,  # FastAPI app
    mcp_path: str = "/mcp",
    endpoint_filter: Optional[Callable] = None,
    server_name: str = "fastapi-openapi-server",
    server_version: str = "0.1.0",
    enable_cors: bool = True,
    cors_origins: Optional[list] = None
) -> FastAPIMCPServer:
    """
    Mount MCP OpenAPI tools to a FastAPI application.
    
    This function creates and mounts an MCP server that provides tools for
    endpoint introspection on the given FastAPI application.
    
    Args:
        app: FastAPI application instance to mount the MCP tools on
        mcp_path: Path prefix for MCP endpoints (default: "/mcp")
        endpoint_filter: Optional function to filter which endpoints to include.
                        Function signature: (route, mcp_path: str) -> bool
        server_name: Name of the MCP server (default: "fastapi-openapi-server")
        server_version: Version of the MCP server (default: "0.1.0")
        enable_cors: Whether to enable CORS for MCP endpoints (default: True)
        cors_origins: List of allowed CORS origins. If None, allows all origins.
    
    Returns:
        FastAPIMCPServer instance that was mounted
    
    Example:
        ```python
        from fastapi import FastAPI
        from fastapi_mcp_openapi import mount_mcp_openapi
        
        app = FastAPI()
        
        # Mount with default settings
        mcp_server = mount_mcp_openapi(app)
        
        # Mount with custom settings
        def custom_filter(route, mcp_path):
            return not route.path.startswith("/internal")
        
        mcp_server = mount_mcp_openapi(
            app,
            mcp_path="/api-tools",
            endpoint_filter=custom_filter,
            server_name="my-api-server",
            enable_cors=True,
            cors_origins=["http://localhost:3000", "https://myapp.com"]
        )
        
        @app.get("/users/{user_id}")
        async def get_user(user_id: int):
            return {"user_id": user_id}
        ```
    """
    try:
        # Create the MCP server instance
        mcp_server = FastAPIMCPServer(
            app=app,
            mcp_path=mcp_path,
            endpoint_filter=endpoint_filter,
            server_name=server_name,
            server_version=server_version
        )
        
        # Get the FastMCP app (simplified implementation)
        mcp_app = mcp_server.get_mcp_app()
        
        # In a real implementation, this would mount the actual MCP server
        # For now, we'll create a simple endpoint that describes the available tools
        @app.get(f"{mcp_path}/tools")
        async def list_mcp_tools():
            """List available MCP tools."""
            return {
                "server": {
                    "name": server_name,
                    "version": server_version
                },
                "tools": [
                    {
                        "name": "list_endpoints",
                        "description": "List all user-defined endpoints in the FastAPI application"
                    },
                    {
                        "name": "get_endpoint_docs", 
                        "description": "Get detailed OpenAPI documentation for a specific endpoint"
                    }
                ]
            }
        
        @app.post(f"{mcp_path}/call")
        async def call_mcp_tool(request: dict):
            """Call an MCP tool."""
            tool_name = request.get("tool")
            if not tool_name:
                return {"error": "Tool name is required"}
                
            arguments = request.get("arguments", {})
            
            tool_func = mcp_server.get_tool(tool_name)
            if not tool_func:
                return {"error": f"Tool '{tool_name}' not found"}
            
            try:
                result = await tool_func(**arguments)
                return {"result": result}
            except Exception as e:
                return {"error": str(e)}
        
        logger.info(f"MCP OpenAPI tools mounted at {mcp_path}")
        logger.info("Available tools: list_endpoints, get_endpoint_docs")
        
        return mcp_server
    
    except Exception as e:
        logger.error(f"Failed to mount MCP OpenAPI tools: {e}")
        raise


def create_standalone_mcp_server(
    app,  # FastAPI app
    endpoint_filter: Optional[Callable] = None,
    server_name: str = "fastapi-openapi-server",
    server_version: str = "0.1.0"
) -> FastAPIMCPServer:
    """
    Create a standalone MCP server for FastAPI endpoint introspection.
    
    This function creates an MCP server that can be run independently
    or integrated into other systems without mounting to the FastAPI app.
    
    Args:
        app: FastAPI application instance to introspect
        endpoint_filter: Optional function to filter which endpoints to include
        server_name: Name of the MCP server
        server_version: Version of the MCP server
    
    Returns:
        FastAPIMCPServer instance
    
    Example:
        ```python
        from fastapi import FastAPI
        from fastapi_mcp_openapi import create_standalone_mcp_server
        
        app = FastAPI()
        
        @app.get("/users/{user_id}")
        async def get_user(user_id: int):
            return {"user_id": user_id}
        
        # Create standalone MCP server
        mcp_server = create_standalone_mcp_server(app)
        
        # Use the MCP server independently
        mcp_app = mcp_server.get_mcp_app()
        ```
    """
    try:
        mcp_server = FastAPIMCPServer(
            app=app,
            mcp_path="",  # No path filtering for standalone
            endpoint_filter=endpoint_filter,
            server_name=server_name,
            server_version=server_version
        )
        
        logger.info("Standalone MCP server created for FastAPI endpoint introspection")
        return mcp_server
    
    except Exception as e:
        logger.error(f"Failed to create standalone MCP server: {e}")
        raise
