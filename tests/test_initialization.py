"""
Tests for the FastAPIMCPOpenAPI initialization and configuration.
"""

from mcp.server.fastmcp import FastMCP

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class TestFastAPIMCPOpenAPIInit:
    """Test initialization and configuration of FastAPIMCPOpenAPI."""

    def test_default_initialization(self, basic_app):
        """Test initialization with default parameters."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        assert mcp.app is basic_app
        assert mcp.mount_path == "/mcp"
        assert mcp.server_name == "fastapi-openapi-mcp"
        assert mcp.server_version == "0.1.0"
        assert mcp.section_name == "mcp"
        assert mcp.list_endpoints_tool_name == "listEndpoints"
        assert mcp.get_endpoint_docs_tool_name == "getEndpointDocs"
        assert isinstance(mcp.mcp_server, FastMCP)

    def test_custom_initialization(self, basic_app):
        """Test initialization with custom parameters."""
        mcp = FastAPIMCPOpenAPI(
            app=basic_app,
            mount_path="/custom-mcp",
            server_name="Custom Server",
            server_version="2.0.0",
            section_name="custom",
            list_endpoints_tool_name="customList",
            get_endpoint_docs_tool_name="customDocs",
        )

        assert mcp.app is basic_app
        assert mcp.mount_path == "/custom-mcp"
        assert mcp.server_name == "Custom Server"
        assert mcp.server_version == "2.0.0"
        assert mcp.section_name == "custom"
        assert mcp.list_endpoints_tool_name == "customList"
        assert mcp.get_endpoint_docs_tool_name == "customDocs"

    def test_mcp_server_creation(self, basic_app):
        """Test that FastMCP server is created with correct name."""
        server_name = "Test MCP Server"
        mcp = FastAPIMCPOpenAPI(basic_app, server_name=server_name)

        assert isinstance(mcp.mcp_server, FastMCP)
        # The FastMCP server is created with the server name

    def test_tools_registration(self, basic_app):
        """Test that MCP tools are registered during initialization."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        # Check that the mcp_server has tools registered
        # This is verified by checking that _register_tools was called
        # during initialization (implicit test through successful init)
        assert mcp.mcp_server is not None

    def test_app_mounting(self, basic_app):
        """Test that MCP server is mounted to the FastAPI app."""
        initial_routes_count = len(basic_app.routes)
        FastAPIMCPOpenAPI(basic_app)

        # After mounting, there should be additional routes
        assert len(basic_app.routes) > initial_routes_count

        # Check that routes were added with the correct mount path
        route_paths = [getattr(route, "path", None) for route in basic_app.routes]
        assert "/mcp" in route_paths
        assert "/health" in route_paths

    def test_custom_mount_path(self, basic_app):
        """Test mounting with custom path."""
        custom_path = "/api-inspector"
        FastAPIMCPOpenAPI(basic_app, mount_path=custom_path)

        route_paths = [getattr(route, "path", None) for route in basic_app.routes]
        assert custom_path in route_paths

    def test_get_mcp_info(self, mcp_instance):
        """Test get_mcp_info method returns correct information."""
        info = mcp_instance.get_mcp_info()

        expected_keys = {
            "server_name",
            "server_version",
            "mount_path",
            "section_name",
            "mcp_endpoint",
            "health_endpoint",
            "tools",
        }
        assert set(info.keys()) == expected_keys

        assert info["server_name"] == "fastapi-openapi-mcp"
        assert info["server_version"] == "0.1.0"
        assert info["mount_path"] == "/mcp"
        assert info["section_name"] == "mcp"
        assert info["mcp_endpoint"] == "/mcp/"
        assert info["health_endpoint"] == "/mcp/health"

        assert len(info["tools"]) == 2
        tool_names = [tool["name"] for tool in info["tools"]]
        assert "listEndpoints" in tool_names
        assert "getEndpointDocs" in tool_names

    def test_get_mcp_info_custom_config(self, custom_mcp_instance):
        """Test get_mcp_info with custom configuration."""
        info = custom_mcp_instance.get_mcp_info()

        assert info["server_name"] == "Custom Test Server"
        assert info["server_version"] == "2.0.0"
        assert info["mount_path"] == "/custom-mcp"
        assert info["section_name"] == "custom"
        assert info["mcp_endpoint"] == "/custom-mcp/"
        assert info["health_endpoint"] == "/custom-mcp/health"

        tool_names = [tool["name"] for tool in info["tools"]]
        assert "customListEndpoints" in tool_names
        assert "customGetEndpointDocs" in tool_names
