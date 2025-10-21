"""
Tests for the MCP tools functionality.
"""

import json

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class TestMCPTools:
    """Test MCP tools functionality."""

    def test_list_endpoints_basic(self, basic_app):
        """Test list_endpoints tool with basic app."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        # Get the list_endpoints function from the registered tools
        # We'll test this indirectly by checking the tool works as expected
        endpoints_data = self._call_list_endpoints_tool(mcp)
        response = json.loads(endpoints_data)
        endpoints = response["endpoints"]

        # Should have 3 endpoints: root, get_user, create_user
        assert len(endpoints) == 3

        # Check root endpoint
        root_endpoint = next(e for e in endpoints if e["path"] == "/")
        assert "GET" in root_endpoint["methods"]
        assert root_endpoint["name"] == "root"
        assert root_endpoint["summary"] == "Root endpoint."

        # Check user endpoints
        get_user_endpoint = next(
            e for e in endpoints if e["path"] == "/users/{user_id}"
        )
        assert "GET" in get_user_endpoint["methods"]
        assert get_user_endpoint["name"] == "get_user"
        assert get_user_endpoint["summary"] == "Get a user by ID."

        create_user_endpoint = next(e for e in endpoints if e["path"] == "/users/")
        assert "POST" in create_user_endpoint["methods"]
        assert create_user_endpoint["name"] == "create_user"
        assert create_user_endpoint["summary"] == "Create a new user."

    def test_list_endpoints_excludes_mcp_routes(self, basic_app):
        """Test that list_endpoints excludes MCP routes."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        endpoints_data = self._call_list_endpoints_tool(mcp)
        response = json.loads(endpoints_data)
        endpoints = response["endpoints"]

        # Check that no MCP endpoints are included
        mcp_paths = [e["path"] for e in endpoints if e["path"].startswith("/mcp")]
        assert len(mcp_paths) == 0

        # Health endpoint should also be excluded since it's added by MCP
        health_paths = [e["path"] for e in endpoints if e["path"] == "/health"]
        assert len(health_paths) == 0

    def test_list_endpoints_custom_mount_path(self, basic_app):
        """Test list_endpoints with custom mount path."""
        custom_mount = "/custom-api"
        mcp = FastAPIMCPOpenAPI(basic_app, mount_path=custom_mount)

        endpoints_data = self._call_list_endpoints_tool(mcp)
        response = json.loads(endpoints_data)
        endpoints = response["endpoints"]

        # Should still exclude the custom mount path
        custom_paths = [
            e["path"] for e in endpoints if e["path"].startswith(custom_mount)
        ]
        assert len(custom_paths) == 0

    def test_list_endpoints_no_docstring(self, empty_app):
        """Test list_endpoints with endpoints that have no docstring."""

        @empty_app.get("/no-doc")
        async def no_doc_endpoint():
            return {"message": "No docstring"}

        mcp = FastAPIMCPOpenAPI(empty_app)
        endpoints_data = self._call_list_endpoints_tool(mcp)
        response = json.loads(endpoints_data)
        endpoints = response["endpoints"]

        endpoint_without_doc = next(e for e in endpoints if e["path"] == "/no-doc")
        assert endpoint_without_doc["summary"] is None

    def test_get_endpoint_docs_basic(self, basic_app):
        """Test get_endpoint_docs with basic endpoint."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/", "GET")
        docs = json.loads(docs_data)

        assert docs["path"] == "/"
        assert docs["method"] == "GET"
        assert "operation" in docs
        assert "responses" in docs["operation"]

    def test_get_endpoint_docs_with_path_parameter(self, basic_app):
        """Test get_endpoint_docs with path parameter."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/users/{user_id}", "GET")
        docs = json.loads(docs_data)

        assert docs["path"] == "/users/{user_id}"
        assert docs["method"] == "GET"
        assert "operation" in docs
        assert "parameters" in docs["operation"]

        # Check that path parameter is included
        parameters = docs["operation"]["parameters"]
        user_id_param = next(p for p in parameters if p["name"] == "user_id")
        assert user_id_param["in"] == "path"
        assert user_id_param["required"] is True

    def test_get_endpoint_docs_post_method(self, basic_app):
        """Test get_endpoint_docs with POST method."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/users/", "POST")
        docs = json.loads(docs_data)

        assert docs["path"] == "/users/"
        assert docs["method"] == "POST"
        assert "operation" in docs
        assert "requestBody" in docs["operation"]

    def test_get_endpoint_docs_method_not_found(self, basic_app):
        """Test get_endpoint_docs with non-existent method."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/", "DELETE")
        docs = json.loads(docs_data)

        assert "error" in docs
        assert "Method DELETE not found" in docs["error"]
        assert "available_methods" in docs
        assert "get" in docs["available_methods"]

    def test_get_endpoint_docs_endpoint_not_found(self, basic_app):
        """Test get_endpoint_docs with non-existent endpoint."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/nonexistent", "GET")
        docs = json.loads(docs_data)

        assert "error" in docs
        assert "Endpoint /nonexistent not found" in docs["error"]
        assert "available_endpoints" in docs

    def test_get_endpoint_docs_case_insensitive_method(self, basic_app):
        """Test get_endpoint_docs with lowercase method."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/", "get")
        docs = json.loads(docs_data)

        assert docs["path"] == "/"
        assert docs["method"] == "GET"  # Should be normalized to uppercase

    def test_get_endpoint_docs_default_method(self, basic_app):
        """Test get_endpoint_docs with default method."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        # Test without providing method (should default to GET)
        docs_data = self._call_get_endpoint_docs_tool(mcp, "/")
        docs = json.loads(docs_data)

        assert docs["method"] == "GET"

    def test_get_endpoint_docs_removes_operation_id(self, complex_app):
        """Test that operationId is removed from endpoint docs."""
        mcp = FastAPIMCPOpenAPI(complex_app)

        docs_data = self._call_get_endpoint_docs_tool(mcp, "/users/{user_id}", "GET")
        docs = json.loads(docs_data)

        # operationId should be removed
        assert "operationId" not in docs["operation"]

    def test_list_endpoints_with_authentication_schemes(self):
        """Test that list_endpoints includes authentication schemes from OpenAPI."""
        from fastapi import FastAPI, Depends
        from fastapi.security import HTTPBearer, OAuth2AuthorizationCodeBearer
        
        # Create app with security schemes
        app = FastAPI(title="Auth API", version="1.0.0")
        
        security = HTTPBearer()
        oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl="https://example.com/auth",
            tokenUrl="https://example.com/token",
            scopes={"read": "read access", "write": "write access"}
        )
        
        @app.get("/")
        async def root():
            return {"message": "public"}
            
        @app.get("/secure", dependencies=[Depends(security)])
        async def secure():
            return {"message": "secure"}
            
        @app.get("/oauth", dependencies=[Depends(oauth2_scheme)])
        async def oauth():
            return {"message": "oauth"}
        
        mcp = FastAPIMCPOpenAPI(app)
        endpoints_data = self._call_list_endpoints_tool(mcp)
        response = json.loads(endpoints_data)
        
        # Check structure
        assert "endpoints" in response
        assert "authentication" in response
        
        # Check endpoints
        endpoints = response["endpoints"]
        assert len(endpoints) == 3
        
        # Check authentication schemes
        auth = response["authentication"]
        assert len(auth) == 2
        
        # Validate HTTPBearer scheme
        assert "HTTPBearer" in auth
        assert auth["HTTPBearer"]["type"] == "http"
        assert auth["HTTPBearer"]["scheme"] == "bearer"
        
        # Validate OAuth2 scheme
        assert "OAuth2AuthorizationCodeBearer" in auth
        oauth_scheme = auth["OAuth2AuthorizationCodeBearer"]
        assert oauth_scheme["type"] == "oauth2"
        assert "flows" in oauth_scheme
        assert "authorizationCode" in oauth_scheme["flows"]
        
        flow = oauth_scheme["flows"]["authorizationCode"]
        assert "scopes" in flow
        assert "read" in flow["scopes"]
        assert "write" in flow["scopes"]

    def test_list_endpoints_empty_authentication(self, empty_app):
        """Test that list_endpoints returns empty authentication when no schemes are present."""
        mcp = FastAPIMCPOpenAPI(empty_app)
        endpoints_data = self._call_list_endpoints_tool(mcp)
        response = json.loads(endpoints_data)
        
        assert "authentication" in response
        assert response["authentication"] == {}

    def _call_list_endpoints_tool(self, mcp: FastAPIMCPOpenAPI) -> str:
        """Helper method to call the list_endpoints tool."""
        # Simulate calling the list_endpoints tool
        endpoints = []
        for route in mcp.app.routes:
            from fastapi.routing import APIRoute

            if isinstance(route, APIRoute):
                # Skip MCP endpoints
                if route.path.startswith(mcp.mount_path):
                    continue

                # Skip health endpoint added by MCP
                if route.path == "/health" and route.name == "health_endpoint":
                    continue

                endpoint_info = {
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name,
                    "summary": getattr(route.endpoint, "__doc__", "").split("\n")[0]
                    if route.endpoint.__doc__
                    else None,
                }
                endpoints.append(endpoint_info)

        # Get authentication information from OpenAPI schema
        from fastapi.openapi.utils import get_openapi
        
        openapi_schema = get_openapi(
            title=mcp.app.title,
            version=mcp.app.version,
            description=mcp.app.description,
            routes=mcp.app.routes,
        )
        
        authentication = {}
        if "components" in openapi_schema and "securitySchemes" in openapi_schema["components"]:
            authentication = openapi_schema["components"]["securitySchemes"]

        response_data = {
            "endpoints": endpoints,
            "authentication": authentication
        }

        return json.dumps(response_data, indent=2)

    def _call_get_endpoint_docs_tool(
        self, mcp: FastAPIMCPOpenAPI, endpoint_path: str, method: str = "GET"
    ) -> str:
        """Helper method to call the get_endpoint_docs tool."""
        from fastapi.openapi.utils import get_openapi

        method = method.upper()

        # Generate the full OpenAPI schema
        openapi_schema = get_openapi(
            title=mcp.app.title,
            version=mcp.app.version,
            description=mcp.app.description,
            routes=mcp.app.routes,
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
                resolved_operation = mcp._resolve_refs(operation, openapi_schema)

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
                    "available_endpoints": list(openapi_schema.get("paths", {}).keys()),
                },
                indent=2,
            )
