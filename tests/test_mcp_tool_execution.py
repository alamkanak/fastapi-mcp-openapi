"""
Tests for actual MCP tool execution to ensure coverage of registered functions.
"""

import json

from fastapi.testclient import TestClient

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class TestMCPToolExecution:
    """Test actual execution of registered MCP tools."""

    def test_actual_list_endpoints_tool_execution(self, basic_app):
        """Test actual execution of the registered listEndpoints tool via HTTP."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        # Call the actual tool via MCP protocol
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        result = response.json()
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert "result" in result

        # Parse the actual tool output
        content = result["result"]["content"][0]["text"]
        response_data = json.loads(content)
        endpoints = response_data["endpoints"]

        # Verify the endpoints are correct (should have basic_app endpoints)
        assert len(endpoints) == 3  # root, get_user, create_user

        endpoint_paths = [e["path"] for e in endpoints]
        assert "/" in endpoint_paths
        assert "/users/{user_id}" in endpoint_paths
        assert "/users/" in endpoint_paths

        # Verify structure of each endpoint
        for endpoint in endpoints:
            assert "path" in endpoint
            assert "methods" in endpoint
            assert "name" in endpoint
            assert "summary" in endpoint
            assert isinstance(endpoint["methods"], list)

    def test_actual_list_endpoints_with_no_docstring(self, empty_app):
        """Test listEndpoints tool with endpoints that have no docstring."""

        @empty_app.get("/no-doc")
        async def no_doc_endpoint():
            return {"message": "No docstring"}

        FastAPIMCPOpenAPI(empty_app)
        client = TestClient(empty_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        content = response.json()["result"]["content"][0]["text"]
        response_data = json.loads(content)
        endpoints = response_data["endpoints"]

        # Should have the no-doc endpoint
        no_doc_ep = next(e for e in endpoints if e["path"] == "/no-doc")
        assert no_doc_ep["summary"] is None

    def test_actual_list_endpoints_excludes_mcp_health(self, basic_app):
        """Test that actual tool excludes MCP endpoints and health endpoint."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response = client.post("/mcp", json=payload)
        content = response.json()["result"]["content"][0]["text"]
        response_data = json.loads(content)
        endpoints = response_data["endpoints"]

        # Verify no MCP paths are included
        mcp_paths = [e["path"] for e in endpoints if e["path"].startswith("/mcp")]
        assert len(mcp_paths) == 0

        # Verify no health endpoints are included (MCP creates these)
        health_paths = [
            e["path"]
            for e in endpoints
            if e["path"] == "/health" and e["name"] == "health_endpoint"
        ]
        assert len(health_paths) == 0

    def test_actual_list_endpoints_with_custom_mount(self, basic_app):
        """Test listEndpoints tool with custom mount path."""
        custom_mount = "/custom-mcp"
        FastAPIMCPOpenAPI(basic_app, mount_path=custom_mount)
        client = TestClient(basic_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response = client.post(custom_mount, json=payload)
        content = response.json()["result"]["content"][0]["text"]
        response_data = json.loads(content)
        endpoints = response_data["endpoints"]

        # Should exclude custom mount path
        custom_paths = [
            e["path"] for e in endpoints if e["path"].startswith(custom_mount)
        ]
        assert len(custom_paths) == 0

        # Should still include user endpoints
        user_paths = [e["path"] for e in endpoints if e["path"].startswith("/users")]
        assert len(user_paths) == 2

    def test_actual_get_endpoint_docs_tool_execution(self, basic_app):
        """Test actual execution of the registered getEndpointDocs tool."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "getEndpointDocs",
                "arguments": {"endpoint_path": "/users/{user_id}", "method": "GET"},
            },
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        result = response.json()
        content = result["result"]["content"][0]["text"]
        docs = json.loads(content)

        assert docs["path"] == "/users/{user_id}"
        assert docs["method"] == "GET"
        assert "operation" in docs
        assert "parameters" in docs["operation"]

    def test_complex_app_endpoints_coverage(self, complex_app):
        """Test listEndpoints with complex app to cover various endpoint types."""
        FastAPIMCPOpenAPI(complex_app)
        client = TestClient(complex_app)

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response = client.post("/mcp", json=payload)
        content = response.json()["result"]["content"][0]["text"]
        response_data = json.loads(content)
        endpoints = response_data["endpoints"]

        # Complex app should have many endpoints
        assert len(endpoints) >= 5

        # Verify different HTTP methods are captured
        all_methods = set()
        for endpoint in endpoints:
            all_methods.update(endpoint["methods"])

        # Should have various HTTP methods
        assert "GET" in all_methods
        assert "POST" in all_methods
        assert "PUT" in all_methods
        assert "DELETE" in all_methods

        # Verify summaries are extracted from docstrings
        endpoints_with_summaries = [e for e in endpoints if e["summary"] is not None]
        assert len(endpoints_with_summaries) > 0

        # Check specific endpoints exist
        endpoint_paths = [e["path"] for e in endpoints]
        assert "/" in endpoint_paths
        assert "/users/{user_id}" in endpoint_paths
        assert "/users/" in endpoint_paths
