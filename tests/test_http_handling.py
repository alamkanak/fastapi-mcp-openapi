"""
Tests for HTTP handling functionality.
"""

import json

from fastapi.testclient import TestClient

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class TestHTTPHandling:
    """Test HTTP request handling for MCP endpoints."""

    def test_health_endpoint_get(self, basic_app):
        """Test GET request to health endpoint."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "fastapi-openapi-mcp"
        assert data["version"] == "0.1.0"
        assert data["mcp_endpoint"] == "/mcp"

        # Check CORS headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"

    def test_health_endpoint_options(self, basic_app):
        """Test OPTIONS request to health endpoint."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.options("/health")
        assert response.status_code == 200

        # Check CORS headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "GET, POST, OPTIONS" in response.headers["Access-Control-Allow-Methods"]
        assert response.headers["Access-Control-Max-Age"] == "86400"

    def test_mcp_endpoint_get_without_transport_type(self, basic_app):
        """Test GET request to MCP endpoint without transportType query."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.get("/mcp")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "fastapi-openapi-mcp"
        assert data["version"] == "0.1.0"
        assert data["protocol"] == "mcp"
        assert data["mount_path"] == "/mcp"
        assert "listEndpoints" in data["tools"]
        assert "getEndpointDocs" in data["tools"]

    def test_mcp_endpoint_get_with_transport_type(self, basic_app):
        """Test GET request to MCP endpoint with transportType query."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.get("/mcp?transportType=streamable-http")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "fastapi-openapi-mcp"
        assert data["version"] == "0.1.0"
        assert data["transport"] == "streamable-http"
        assert data["capabilities"] == {"tools": {}}

    def test_mcp_endpoint_options(self, basic_app):
        """Test OPTIONS request to MCP endpoint."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.options("/mcp")
        assert response.status_code == 200

        # Check CORS headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "GET, POST, OPTIONS" in response.headers["Access-Control-Allow-Methods"]

    def test_mcp_endpoint_post_initialize(self, basic_app):
        """Test POST request to MCP endpoint with initialize method."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["protocolVersion"] == "2024-11-05"
        assert data["result"]["serverInfo"]["name"] == "fastapi-openapi-mcp"
        assert data["result"]["capabilities"] == {"tools": {}}

    def test_mcp_endpoint_post_tools_list(self, basic_app):
        """Test POST request to MCP endpoint with tools/list method."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert "result" in data
        assert "tools" in data["result"]

        tools = data["result"]["tools"]
        assert len(tools) == 2

        list_tool = next(t for t in tools if t["name"] == "listEndpoints")
        assert list_tool["description"] == "List all FastAPI endpoints and authentication strategy"
        assert list_tool["inputSchema"]["type"] == "object"

        docs_tool = next(t for t in tools if t["name"] == "getEndpointDocs")
        assert (
            docs_tool["description"]
            == "Get detailed OpenAPI documentation for a specific endpoint"
        )
        assert "endpoint_path" in docs_tool["inputSchema"]["properties"]

    def test_mcp_endpoint_post_tools_call_list_endpoints(self, basic_app):
        """Test POST request to call listEndpoints tool."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 3
        assert "result" in data
        assert "content" in data["result"]

        content = data["result"]["content"][0]
        assert content["type"] == "text"

        result = json.loads(content["text"])
        endpoints = result["endpoints"]
        assert len(endpoints) == 3  # root, get_user, create_user

    def test_mcp_endpoint_post_tools_call_get_endpoint_docs(self, basic_app):
        """Test POST request to call getEndpointDocs tool."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "getEndpointDocs",
                "arguments": {"endpoint_path": "/", "method": "GET"},
            },
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 4
        assert "result" in data

        content = data["result"]["content"][0]
        endpoint_docs = json.loads(content["text"])
        assert endpoint_docs["path"] == "/"
        assert endpoint_docs["method"] == "GET"
        assert "operation" in endpoint_docs

    def test_mcp_endpoint_post_unknown_tool(self, basic_app):
        """Test POST request with unknown tool name."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "unknownTool", "arguments": {}},
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        content = data["result"]["content"][0]
        error_data = json.loads(content["text"])
        assert "error" in error_data
        assert "Unknown tool: unknownTool" in error_data["error"]

    def test_mcp_endpoint_post_unknown_method(self, basic_app):
        """Test POST request with unknown method."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {"jsonrpc": "2.0", "id": 6, "method": "unknown/method", "params": {}}

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 6
        assert "error" in data
        assert data["error"]["code"] == -32601
        assert "Method not found" in data["error"]["message"]

    def test_mcp_endpoint_post_invalid_json(self, basic_app):
        """Test POST request with invalid JSON."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.post(
            "/mcp", content="invalid json", headers={"content-type": "application/json"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] is None
        assert "error" in data
        assert data["error"]["code"] == -32700
        assert data["error"]["message"] == "Parse error"

    def test_mcp_endpoint_post_empty_body(self, basic_app):
        """Test POST request with empty body."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.post("/mcp", content="")
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] is None
        assert "error" in data
        assert data["error"]["code"] == -32600
        assert data["error"]["message"] == "Invalid Request"

    def test_mcp_endpoint_unsupported_method(self, basic_app):
        """Test unsupported HTTP method on MCP endpoint."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        response = client.put("/mcp")
        assert response.status_code == 405

    def test_custom_mount_path_endpoints(self, basic_app):
        """Test endpoints with custom mount path."""
        custom_path = "/api-inspector"
        FastAPIMCPOpenAPI(basic_app, mount_path=custom_path)
        client = TestClient(basic_app)

        # Test custom MCP endpoint
        response = client.get(custom_path)
        assert response.status_code == 200

        data = response.json()
        assert data["mount_path"] == custom_path

        # Health endpoint should still be at /health
        response = client.get("/health")
        assert response.status_code == 200

    def test_cors_headers_present(self, basic_app):
        """Test that CORS headers are present in all responses."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        # Test GET request
        response = client.get("/mcp")
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "GET, POST, OPTIONS" in response.headers["Access-Control-Allow-Methods"]

        # Test POST request
        payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        response = client.post("/mcp", json=payload)
        assert response.headers["Access-Control-Allow-Origin"] == "*"

        # Test OPTIONS request
        response = client.options("/mcp")
        assert response.headers["Access-Control-Allow-Origin"] == "*"

    def test_internal_error_handling(self, basic_app):
        """Test internal error handling in MCP endpoint."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        # This should trigger an internal error due to malformed request structure
        # We'll send a request that passes JSON parsing but fails during processing
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "getEndpointDocs",
                "arguments": {
                    "endpoint_path": "/nonexistent"
                    # Missing method parameter should be handled gracefully
                },
            },
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        data = response.json()
        # Should return a proper result, not an error, since missing method defaults to GET
        assert "result" in data
