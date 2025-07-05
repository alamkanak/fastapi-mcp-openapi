"""MCP Server implementation for FastAPI endpoint introspection."""

import logging
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import unquote

from .utils import extract_endpoint_info, extract_endpoint_detail, filter_user_endpoints

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry for MCP tools - a simplified implementation."""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool function."""
        self.tools[name] = func
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a registered tool."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())


class FastAPIMCPServer:
    """MCP Server that provides tools for FastAPI endpoint introspection."""
    
    def __init__(
        self,
        app,
        mcp_path: str = "/mcp",
        endpoint_filter: Optional[Callable] = None,
        server_name: str = "fastapi-openapi-server",
        server_version: str = "0.1.0"
    ):
        """
        Initialize the FastAPI MCP Server.
        
        Args:
            app: FastAPI application instance
            mcp_path: Path prefix for MCP endpoints
            endpoint_filter: Optional function to filter endpoints
            server_name: Name of the MCP server
            server_version: Version of the MCP server
        """
        self.app = app
        self.mcp_path = mcp_path
        self.endpoint_filter = endpoint_filter or filter_user_endpoints
        self.server_name = server_name
        self.server_version = server_version
        
        # Initialize tool registry
        self.tool_registry = MCPToolRegistry()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register MCP tools for endpoint introspection."""
        
        async def list_endpoints() -> List[Dict[str, Any]]:
            """
            List all user-defined endpoints in the FastAPI application.
            
            Returns a list of endpoints with basic information including path,
            methods, name, and summary. Excludes MCP endpoints and other
            system endpoints.
            
            Returns:
                List of endpoint information dictionaries
            """
            try:
                endpoints = []
                
                # Get all routes from the FastAPI app
                for route in self.app.routes:
                    if self.endpoint_filter(route, self.mcp_path):
                        endpoint_info = extract_endpoint_info(route)
                        if endpoint_info:
                            endpoints.append(endpoint_info.dict())
                
                logger.info(f"Found {len(endpoints)} user-defined endpoints")
                return endpoints
                
            except Exception as e:
                logger.error(f"Error listing endpoints: {e}")
                raise
        
        async def get_endpoint_docs(
            endpoint_path: str,
            method: str = "GET"
        ) -> Dict[str, Any]:
            """
            Get detailed OpenAPI documentation for a specific endpoint.
            
            Provides comprehensive information about an endpoint including
            parameters, request body, responses, and full OpenAPI specification.
            
            Args:
                endpoint_path: The path of the endpoint (e.g., "/users/{user_id}")
                method: HTTP method (default: "GET")
            
            Returns:
                Detailed endpoint documentation
            """
            try:
                method = method.upper()
                
                # Find the matching route
                target_route = None
                for route in self.app.routes:
                    if hasattr(route, 'path') and hasattr(route, 'methods'):
                        # Handle path parameters by comparing normalized paths
                        route_path = getattr(route, 'path', '')
                        if (self._normalize_path(route_path) == self._normalize_path(endpoint_path) 
                            and method in getattr(route, 'methods', set())):
                            target_route = route
                            break
                
                if not target_route:
                    raise ValueError(f"Endpoint {method} {endpoint_path} not found")
                
                # Extract detailed endpoint information
                endpoint_detail = extract_endpoint_detail(target_route, method)
                if not endpoint_detail:
                    raise ValueError(f"Could not extract details for {method} {endpoint_path}")
                
                # Get OpenAPI spec for this specific endpoint
                openapi_spec = self._get_endpoint_openapi_spec(target_route, method)
                
                result = {
                    "endpoint": endpoint_detail.dict(),
                    "openapi_spec": openapi_spec
                }
                
                logger.info(f"Retrieved documentation for {method} {endpoint_path}")
                return result
                
            except Exception as e:
                logger.error(f"Error getting endpoint docs for {method} {endpoint_path}: {e}")
                raise
        
        # Register the tools
        self.tool_registry.register_tool("list_endpoints", list_endpoints)
        self.tool_registry.register_tool("get_endpoint_docs", get_endpoint_docs)
    
    def _normalize_path(self, path: str) -> str:
        """Normalize a path for comparison."""
        return unquote(path.rstrip('/'))
    
    def _get_endpoint_openapi_spec(self, route, method: str) -> Dict[str, Any]:
        """Get the OpenAPI specification for a specific endpoint."""
        try:
            # Get the full OpenAPI spec
            openapi_spec = self.app.openapi()
            
            # Find the matching path in the OpenAPI spec
            path = getattr(route, 'path', '')
            if path in openapi_spec.get('paths', {}):
                path_spec = openapi_spec['paths'][path]
                if method.lower() in path_spec:
                    return {
                        'path': path,
                        'method': method,
                        'spec': path_spec[method.lower()],
                        'components': openapi_spec.get('components', {})
                    }
            
            return {}
            
        except Exception as e:
            logger.warning(f"Could not extract OpenAPI spec for {method} {path}: {e}")
            return {}
    
    def get_tool(self, tool_name: str) -> Optional[Callable]:
        """Get a registered tool by name."""
        return self.tool_registry.get_tool(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return self.tool_registry.list_tools()
    
    def get_mcp_app(self):
        """Get the MCP application instance (simplified version)."""
        # This is a simplified implementation
        # In a real MCP implementation, this would return the actual MCP server
        return {
            "name": self.server_name,
            "version": self.server_version,
            "tools": self.list_tools(),
            "registry": self.tool_registry
        }
