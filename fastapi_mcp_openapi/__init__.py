"""
FastAPI MCP OpenAPI - A library that provides MCP tools for endpoint introspection.

This library allows FastAPI applications to expose their endpoint information
through the Model Context Protocol (MCP), enabling AI agents and tools to
discover and understand API structure.
"""

from .main import mount_mcp_openapi, create_standalone_mcp_server
from .models import EndpointInfo, EndpointDetail
from .version import __version__

__all__ = [
    "mount_mcp_openapi", 
    "create_standalone_mcp_server",
    "EndpointInfo", 
    "EndpointDetail", 
    "__version__"
]
