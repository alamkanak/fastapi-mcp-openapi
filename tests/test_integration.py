"""
Integration tests for FastAPI MCP OpenAPI.
"""

import json

from fastapi.testclient import TestClient

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class TestIntegration:
    """Integration tests for the complete functionality."""

    def test_complete_workflow(self, complex_app):
        """Test complete workflow from initialization to MCP tool usage."""
        # Initialize with custom configuration
        FastAPIMCPOpenAPI(
            app=complex_app,
            mount_path="/integration-mcp",
            server_name="Integration Test Server",
            server_version="1.0.0",
        )

        client = TestClient(complex_app)

        # 1. Test health endpoint (app already has one, so check both work)
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        # This should be the app's health endpoint
        assert health_data["status"] == "healthy"

        # 2. Test MCP server info
        response = client.get("/integration-mcp")
        assert response.status_code == 200
        server_info = response.json()
        assert server_info["name"] == "Integration Test Server"

        # 3. Test tools list
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        response = client.post("/integration-mcp", json=payload)
        assert response.status_code == 200
        tools_data = response.json()
        assert len(tools_data["result"]["tools"]) == 2

        # 4. Test list endpoints tool
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }
        response = client.post("/integration-mcp", json=payload)
        assert response.status_code == 200

        endpoints_response = response.json()
        endpoints_text = endpoints_response["result"]["content"][0]["text"]
        result = json.loads(endpoints_text)
        endpoints = result["endpoints"]

        # Should have multiple endpoints from complex_app
        assert len(endpoints) >= 5
        endpoint_paths = [e["path"] for e in endpoints]
        assert "/" in endpoint_paths
        assert "/users/{user_id}" in endpoint_paths

        # 5. Test get endpoint docs tool
        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "getEndpointDocs",
                "arguments": {"endpoint_path": "/users/{user_id}", "method": "GET"},
            },
        }
        response = client.post("/integration-mcp", json=payload)
        assert response.status_code == 200

        docs_response = response.json()
        docs_text = docs_response["result"]["content"][0]["text"]
        docs = json.loads(docs_text)

        assert docs["path"] == "/users/{user_id}"
        assert docs["method"] == "GET"
        assert "operation" in docs
        assert "parameters" in docs["operation"]

    def test_error_handling_workflow(self, basic_app):
        """Test error handling in a complete workflow."""
        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        # Test non-existent endpoint
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "getEndpointDocs",
                "arguments": {"endpoint_path": "/nonexistent", "method": "GET"},
            },
        }
        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        error_response = response.json()
        error_text = error_response["result"]["content"][0]["text"]
        error_data = json.loads(error_text)

        assert "error" in error_data
        assert "not found" in error_data["error"]
        assert "available_endpoints" in error_data

    def test_multiple_instances(self, basic_app, empty_app):
        """Test multiple MCP instances on different apps."""
        # Create two different MCP instances
        FastAPIMCPOpenAPI(basic_app, mount_path="/mcp1", server_name="Server 1")
        FastAPIMCPOpenAPI(empty_app, mount_path="/mcp2", server_name="Server 2")

        # Test both instances work independently
        client1 = TestClient(basic_app)
        client2 = TestClient(empty_app)

        # Test first instance
        response1 = client1.get("/mcp1")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["name"] == "Server 1"

        # Test second instance
        response2 = client2.get("/mcp2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["name"] == "Server 2"

        # List endpoints should return different results
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listEndpoints", "arguments": {}},
        }

        response1 = client1.post("/mcp1", json=payload)
        response2 = client2.post("/mcp2", json=payload)

        result1 = json.loads(response1.json()["result"]["content"][0]["text"])
        result2 = json.loads(response2.json()["result"]["content"][0]["text"])
        endpoints1 = result1["endpoints"]
        endpoints2 = result2["endpoints"]

        # basic_app should have more endpoints than empty_app
        assert len(endpoints1) > len(endpoints2)

    def test_real_openapi_schema_resolution(self, basic_app):
        """Test with real OpenAPI schema that has references."""
        # Add a more complex endpoint with Pydantic models
        from pydantic import BaseModel

        class UserResponse(BaseModel):
            id: int
            name: str
            email: str

        @basic_app.get("/complex-user/{user_id}", response_model=UserResponse)
        async def get_complex_user(user_id: int):
            """Get a complex user with full model."""
            return UserResponse(id=user_id, name="Test", email="test@example.com")

        FastAPIMCPOpenAPI(basic_app)
        client = TestClient(basic_app)

        # Get docs for the complex endpoint
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "getEndpointDocs",
                "arguments": {
                    "endpoint_path": "/complex-user/{user_id}",
                    "method": "GET",
                },
            },
        }

        response = client.post("/mcp", json=payload)
        assert response.status_code == 200

        docs_text = response.json()["result"]["content"][0]["text"]
        docs = json.loads(docs_text)

        # Check that response schema is resolved
        assert "responses" in docs["operation"]
        response_200 = docs["operation"]["responses"]["200"]

        # The schema should be fully resolved (no $ref)
        content = response_200["content"]["application/json"]["schema"]
        assert "$ref" not in json.dumps(content)  # No references should remain
        assert "properties" in content
        assert "id" in content["properties"]
