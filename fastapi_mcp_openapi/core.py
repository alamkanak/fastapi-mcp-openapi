"""
Core module for FastAPI MCP OpenAPI.

This module provides the main FastAPIMCPOpenAPI class that integrates with FastAPI
to provide MCP tools for endpoint introspection and OpenAPI documentation.
"""

import json
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message, Receive, Scope, Send


class FastAPIMCPOpenAPI:
    """
    A class that provides MCP tools for FastAPI endpoint introspection and OpenAPI documentation.

    This class can be mounted to a FastAPI application to expose MCP tools that allow
    clients to discover endpoints and retrieve detailed OpenAPI documentation.
    """

    def __init__(
        self,
        app: FastAPI,
        mount_path: str = "/mcp",
        server_name: str = "fastapi-openapi-mcp",
        server_version: str = "0.1.0",
        section_name: str = "mcp",
        list_endpoints_tool_name: str = "listEndpoints",
        get_endpoint_docs_tool_name: str = "getEndpointDocs",
    ):
        """
        Initialize the FastAPI MCP OpenAPI integration.

        Args:
            app: The FastAPI application to introspect
            mount_path: The path where the MCP server will be mounted
            server_name: Name of the MCP server
            server_version: Version of the MCP server
            section_name: Name of the section in documentation for MCP endpoints
        """
        self.app = app
        self.mount_path = mount_path
        self.server_name = server_name
        self.server_version = server_version
        self.section_name = section_name
        self.mcp_server = FastMCP(server_name)
        self.list_endpoints_tool_name = list_endpoints_tool_name
        self.get_endpoint_docs_tool_name = get_endpoint_docs_tool_name

        # Store references to tool functions for HTTP handler
        self._list_endpoints_func: Callable[[], str] | None = None
        self._get_endpoint_docs_func: Callable[[str, str], str] | None = None

        # Register MCP tools
        self._register_tools()

        # Mount the MCP server to the FastAPI app
        self._mount_mcp_server()

    def _register_tools(self) -> None:
        """Register the MCP tools for endpoint introspection."""

        @self.mcp_server.tool(name=self.list_endpoints_tool_name)
        def list_endpoints() -> str:
            """
            List all FastAPI endpoints and authentication strategy.

            Returns:
                JSON string containing user-defined endpoints and authentication information
            """
            endpoints = []

            for route in self.app.routes:
                if isinstance(route, APIRoute):
                    # Skip MCP endpoints
                    if route.path.startswith(self.mount_path):
                        continue

                    # Skip health endpoint added by MCP
                    if route.path == "/health" and route.name == "health_endpoint":
                        continue

                    # Find the first non-empty line
                    summary = None
                    if route.endpoint.__doc__:
                        for line in getattr(route.endpoint, "__doc__", "").split("\n"):
                            if line.strip():
                                summary = line.strip()
                                break

                    endpoint_info = {
                        "path": route.path,
                        "methods": list(route.methods),
                        "name": route.name,
                        "summary": summary
                    }
                    endpoints.append(endpoint_info)

            # Get authentication information from OpenAPI schema
            openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description,
                routes=self.app.routes,
            )
            authentication = {}
            if "components" in openapi_schema and "securitySchemes" in openapi_schema["components"]:
                authentication = openapi_schema["components"]["securitySchemes"]

            response_data = {
                "endpoints": endpoints,
                "authentication": authentication
            }

            return json.dumps(response_data, indent=2)

        # Store reference to the function for HTTP handler
        self._list_endpoints_func = list_endpoints

        @self.mcp_server.tool(name=self.get_endpoint_docs_tool_name)
        def get_endpoint_docs(endpoint_path: str, method: str = "GET") -> str:
            """
            Get detailed OpenAPI documentation for a specific endpoint.

            Args:
                endpoint_path: The path of the endpoint (e.g., "/users/{user_id}")
                method: The HTTP method (default: "GET")

            Returns:
                JSON string containing the OpenAPI schema for the endpoint
            """
            method = method.upper()

            # Generate the full OpenAPI schema
            openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description,
                routes=self.app.routes,
            )

            # Find the specific endpoint in the schema
            if "paths" in openapi_schema and endpoint_path in openapi_schema["paths"]:
                path_item = openapi_schema["paths"][endpoint_path]

                if method.lower() in path_item:
                    operation = path_item[method.lower()].copy()

                    # Remove operationId if present
                    if "operationId" in operation:
                        del operation["operationId"]

                    # Resolve all $ref references in the operation
                    resolved_operation = self._resolve_refs(operation, openapi_schema)

                    endpoint_schema = {
                        "path": endpoint_path,
                        "method": method,
                        "operation": resolved_operation,
                    }
                    return json.dumps(endpoint_schema, indent=2)
                else:
                    return json.dumps(
                        {
                            "error": f"Method {method} not found for endpoint {endpoint_path}",
                            "available_methods": list(path_item.keys()),
                        },
                        indent=2,
                    )
            else:
                return json.dumps(
                    {
                        "error": f"Endpoint {endpoint_path} not found",
                        "available_endpoints": list(
                            openapi_schema.get("paths", {}).keys()
                        ),
                    },
                    indent=2,
                )

        # Store reference to the function for HTTP handler
        self._get_endpoint_docs_func = get_endpoint_docs

    def _resolve_refs(
        self, obj: Any, openapi_schema: dict[str, Any], visited_refs: set[str] | None = None
    ) -> Any:
        """
        Recursively resolve all $ref references in an OpenAPI schema object.

        Args:
            obj: The object to resolve references in
            openapi_schema: The full OpenAPI schema containing components
            visited_refs: Set of reference paths already being resolved (for circular reference protection)

        Returns:
            The object with all references resolved inline
        """
        if visited_refs is None:
            visited_refs = set()

        if isinstance(obj, dict):
            if "$ref" in obj:
                # Extract the reference path (e.g., "#/components/schemas/UserLogin")
                ref_path = obj["$ref"]
                if ref_path.startswith("#/"):
                    # Check for circular reference
                    if ref_path in visited_refs:
                        # Return the $ref as-is to prevent infinite recursion
                        return obj

                    # Split the path and navigate through the schema
                    parts = ref_path[2:].split("/")  # Remove "#/" and split
                    resolved_obj = openapi_schema
                    for part in parts:
                        if part in resolved_obj:
                            resolved_obj = resolved_obj[part]
                        else:
                            # Reference not found, return the original $ref
                            return obj

                    # Add this ref to the visited set and recursively resolve
                    new_visited = visited_refs | {ref_path}
                    return self._resolve_refs(resolved_obj, openapi_schema, new_visited)
                else:
                    # External reference, return as-is
                    return obj
            else:
                # Recursively resolve references in dictionary values
                resolved_dict = {}
                for key, value in obj.items():
                    resolved_dict[key] = self._resolve_refs(value, openapi_schema, visited_refs)
                return resolved_dict
        elif isinstance(obj, list):
            # Recursively resolve references in list items
            return [self._resolve_refs(item, openapi_schema, visited_refs) for item in obj]
        else:
            # Primitive type, return as-is
            return obj

    def _mount_mcp_server(self) -> None:
        """Mount the MCP server as a Starlette application with proper MCP protocol support."""

        async def handle_mcp_request(
            scope: Scope, receive: Receive, send: Send
        ) -> None:
            """Handle MCP protocol requests."""
            if scope["type"] == "http":
                request = Request(scope, receive)

                # Handle OPTIONS request for CORS
                if request.method == "OPTIONS":
                    response = Response(
                        status_code=200,
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Max-Age": "86400",
                        },
                    )
                    await response(scope, receive, send)
                    return

                # Handle GET requests - for transport negotiation
                if request.method == "GET":
                    # Check if this is a transport type query
                    transport_type = request.query_params.get("transportType")
                    if transport_type:
                        # Return basic server info for transport negotiation
                        response = Response(
                            content=json.dumps(
                                {
                                    "name": self.server_name,
                                    "version": self.server_version,
                                    "transport": "streamable-http",
                                    "capabilities": {"tools": {}},
                                }
                            ),
                            media_type="application/json",
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                                "Access-Control-Allow-Headers": "*",
                            },
                        )
                    else:
                        # Return server info
                        response = Response(
                            content=json.dumps(
                                {
                                    "name": self.server_name,
                                    "version": self.server_version,
                                    "protocol": "mcp",
                                    "mount_path": self.mount_path,
                                    "tools": [
                                        self.list_endpoints_tool_name,
                                        self.get_endpoint_docs_tool_name,
                                    ],
                                }
                            ),
                            media_type="application/json",
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                                "Access-Control-Allow-Headers": "*",
                            },
                        )

                # Handle POST requests - MCP protocol messages
                elif request.method == "POST":
                    try:
                        body = await request.body()
                        if body:
                            # Parse the MCP request
                            try:
                                mcp_request = json.loads(body.decode())

                                # Handle different MCP request types
                                if mcp_request.get("method") == "initialize":
                                    # MCP initialization
                                    response_data = {
                                        "jsonrpc": "2.0",
                                        "id": mcp_request.get("id"),
                                        "result": {
                                            "protocolVersion": "2024-11-05",
                                            "serverInfo": {
                                                "name": self.server_name,
                                                "version": self.server_version,
                                            },
                                            "capabilities": {"tools": {}},
                                        },
                                    }
                                elif mcp_request.get("method") == "tools/list":
                                    # List available tools
                                    response_data = {
                                        "jsonrpc": "2.0",
                                        "id": mcp_request.get("id"),
                                        "result": {
                                            "tools": [
                                                {
                                                    "name": self.list_endpoints_tool_name,
                                                    "description": "List all FastAPI endpoints and authentication strategy",
                                                    "inputSchema": {
                                                        "type": "object",
                                                        "properties": {},
                                                        "required": [],
                                                    },
                                                },
                                                {
                                                    "name": self.get_endpoint_docs_tool_name,
                                                    "description": "Get detailed OpenAPI documentation for a specific endpoint",
                                                    "inputSchema": {
                                                        "type": "object",
                                                        "properties": {
                                                            "endpoint_path": {
                                                                "type": "string",
                                                                "description": "The path of the endpoint",
                                                            },
                                                            "method": {
                                                                "type": "string",
                                                                "description": "The HTTP method",
                                                                "default": "GET",
                                                            },
                                                        },
                                                        "required": ["endpoint_path"],
                                                    },
                                                },
                                            ]
                                        },
                                    }
                                elif mcp_request.get("method") == "tools/call":
                                    # Call a tool
                                    tool_name = mcp_request.get("params", {}).get(
                                        "name"
                                    )
                                    tool_args = mcp_request.get("params", {}).get(
                                        "arguments", {}
                                    )

                                    if tool_name == self.list_endpoints_tool_name:
                                        # Call the actual registered tool function
                                        assert self._list_endpoints_func is not None
                                        result_content = self._list_endpoints_func()

                                    elif tool_name == self.get_endpoint_docs_tool_name:
                                        # Call the actual registered tool function
                                        endpoint_path = tool_args.get("endpoint_path")
                                        method = tool_args.get("method", "GET")
                                        assert self._get_endpoint_docs_func is not None
                                        result_content = self._get_endpoint_docs_func(endpoint_path, method)
                                    else:
                                        result_content = json.dumps(
                                            {"error": f"Unknown tool: {tool_name}"}
                                        )

                                    response_data = {
                                        "jsonrpc": "2.0",
                                        "id": mcp_request.get("id"),
                                        "result": {
                                            "content": [
                                                {"type": "text", "text": result_content}
                                            ]
                                        },
                                    }
                                else:
                                    # Unknown method
                                    response_data = {
                                        "jsonrpc": "2.0",
                                        "id": mcp_request.get("id"),
                                        "error": {
                                            "code": -32601,
                                            "message": f"Method not found: {mcp_request.get('method')}",
                                        },
                                    }

                            except json.JSONDecodeError:
                                response_data = {
                                    "jsonrpc": "2.0",
                                    "id": None,
                                    "error": {"code": -32700, "message": "Parse error"},
                                }
                        else:
                            response_data = {
                                "jsonrpc": "2.0",
                                "id": None,
                                "error": {"code": -32600, "message": "Invalid Request"},
                            }

                        response = Response(
                            content=json.dumps(response_data),
                            media_type="application/json",
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                                "Access-Control-Allow-Headers": "*",
                            },
                        )

                    except Exception as e:
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32603,
                                "message": f"Internal error: {str(e)}",
                            },
                        }
                        response = Response(
                            content=json.dumps(response_data),
                            media_type="application/json",
                            headers={
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                                "Access-Control-Allow-Headers": "*",
                            },
                        )

                else:
                    response = Response("Method Not Allowed", status_code=405)

                await response(scope, receive, send)
            else:
                # For non-HTTP requests, send a 404
                await Response("Not Found", status_code=404)(scope, receive, send)

        # Mount the MCP handler directly - handle both /mcp and /mcp/ paths
        self.app.mount(self.mount_path, handle_mcp_request)

        # Also register a direct route to avoid redirects
        @self.app.post(self.mount_path, tags=[self.section_name])
        @self.app.get(self.mount_path, tags=[self.section_name])
        @self.app.options(self.mount_path, tags=[self.section_name])
        async def mcp_direct_handler(request: Request) -> Response:
            """Direct handler for MCP requests to avoid redirects."""
            # Create a minimal scope for the handler
            scope = {
                "type": "http",
                "method": request.method,
                "path": self.mount_path,
                "query_string": str(request.url.query).encode(),
                "headers": [
                    (k.encode(), v.encode()) for k, v in request.headers.items()
                ],
            }

            # Create receive and send callables
            body = await request.body()

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body, "more_body": False}

            response_started = False
            response_body = b""
            response_status = 200
            response_headers = []

            async def send(message: Message) -> None:
                nonlocal \
                    response_started, \
                    response_body, \
                    response_status, \
                    response_headers
                if message["type"] == "http.response.start":
                    response_started = True
                    response_status = message["status"]
                    response_headers = message.get("headers", [])
                elif message["type"] == "http.response.body":
                    response_body += message.get("body", b"")

            # Call the handler
            await handle_mcp_request(scope, receive, send)

            # Return the response
            headers = {k.decode(): v.decode() for k, v in response_headers}
            return Response(
                content=response_body, status_code=response_status, headers=headers
            )

        # Add health endpoint for MCP Inspector
        @self.app.get("/health", tags=[self.section_name])
        @self.app.options("/health", tags=[self.section_name])
        async def health_endpoint(request: Request) -> Response:
            """Health check endpoint for MCP Inspector."""
            if request.method == "OPTIONS":
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Max-Age": "86400",
                    },
                )

            return Response(
                content=json.dumps(
                    {
                        "status": "healthy",
                        "server": self.server_name,
                        "version": self.server_version,
                        "mcp_endpoint": self.mount_path,
                    }
                ),
                media_type="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                },
            )

    def get_mcp_info(self) -> dict[str, Any]:
        """
        Get information about the mounted MCP server.

        Returns:
            Dictionary containing MCP server information
        """
        return {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "mount_path": self.mount_path,
            "section_name": self.section_name,
            "mcp_endpoint": f"{self.mount_path}/",
            "health_endpoint": f"{self.mount_path}/health",
            "tools": [
                {
                    "name": self.list_endpoints_tool_name,
                    "description": "List all FastAPI endpoints and authentication strategy",
                },
                {
                    "name": self.get_endpoint_docs_tool_name,
                    "description": "Get detailed OpenAPI documentation for a specific endpoint",
                },
            ],
        }
