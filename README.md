# FastAPI MCP OpenAPI

A FastAPI library that provides Model Context Protocol (MCP) tools for endpoint introspection and OpenAPI documentation. This library allows AI agents to discover and understand your FastAPI endpoints through MCP.

## Features

- **Endpoint Discovery**: Lists all available FastAPI endpoints with metadata
- **OpenAPI Documentation**: Provides detailed OpenAPI schema for specific endpoints with fully resolved inline schemas
- **Clean Output**: Removes unnecessary references and fields for minimal context usage
- **MCP Streamable HTTP Transport**: Full compatibility with the latest MCP protocol (2025-03-26)
- **Easy Integration**: Simple mounting system similar to fastapi-mcp
- **Security**: Built-in CORS protection and origin validation
- **Focused Tool Set**: Only provides tools capability - resources and prompts endpoints are disabled

## Installation

```bash
pip install fastapi-mcp-openapi
```

Or with uv:

```bash
uv add fastapi-mcp-openapi
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_mcp_openapi import FastAPIMCPOpenAPI

# Create your FastAPI app
app = FastAPI(title="My API", version="1.0.0")

# Add some example endpoints
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": "John Doe"}

@app.post("/users/")
async def create_user(user_data: dict):
    return {"message": "User created", "data": user_data}

# Create and mount the MCP server
mcp = FastAPIMCPOpenAPI(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Your MCP server will be available at `http://localhost:8000/mcp` and provides two tools:

1. **listEndpoints**: Get all available endpoints (excluding MCP endpoints)
2. **getEndpointDocs**: Get detailed OpenAPI documentation for a specific endpoint

## Configuration

### Constructor Parameters

- `app`: The FastAPI application to introspect
- `mount_path`: Path where MCP server will be mounted (default: "/mcp")
- `server_name`: Name of the MCP server (default: "fastapi-openapi-mcp")
- `server_version`: Version of the MCP server (default: "0.1.0")
- `section_name`: Name of the section in documentation for MCP endpoints (default: "mcp")
- `list_endpoints_tool_name`: Name of the list endpoints tool (default: "listEndpoints")
- `get_endpoint_docs_tool_name`: Name of the get endpoint docs tool (default: "getEndpointDocs")

### Example with Custom Configuration

```python
from fastapi import FastAPI
from fastapi_mcp_openapi import FastAPIMCPOpenAPI

app = FastAPI()

# Custom configuration
mcp = FastAPIMCPOpenAPI(
    app=app,
    mount_path="/api-mcp",
    server_name="Custom API Inspector",
    server_version="2.0.0"
    section_name="api-mcp",
    list_endpoints_tool_name="listApiEndpoints",
    get_endpoint_docs_tool_name="getApiEndpointDocs"
)
```

## MCP Tools

### 1. list_endpoints

Lists all available FastAPI endpoints with their metadata.

**Input**: No parameters required

**Output**: JSON array of endpoint information including:
- `path`: The endpoint path  
- `methods`: Array of HTTP methods
- `name`: Endpoint name
- `summary`: Endpoint summary from docstring

### 2. get_endpoint_docs

Get detailed OpenAPI documentation for a specific endpoint.

**Input**:
- `endpoint_path` (required): The path of the endpoint (e.g., "/users/{user_id}")
- `method` (optional): The HTTP method (default: "GET")

**Output**: JSON object with detailed OpenAPI information including:
- `path`: The endpoint path
- `method`: The HTTP method
- `operation`: OpenAPI operation details with fully resolved schemas

## Transport Support

This library implements the latest MCP Streamable HTTP transport (protocol version 2025-03-26) which:

- Uses a single HTTP endpoint for both requests and responses
- Supports both immediate JSON responses and Server-Sent Events (SSE) streaming
- Provides backward compatibility with older MCP clients
- Includes proper session management with unique session IDs

## Security

The library includes built-in security features:

- **Origin Header Validation**: Prevents DNS rebinding attacks
- **CORS Configuration**: Configured for localhost development by default
- **Session Management**: Proper MCP session handling with unique IDs

For production use, make sure to:
1. Configure appropriate CORS origins
2. Implement proper authentication if needed
3. Bind to localhost (127.0.0.1) for local instances

## Integration with AI Agents

This library is designed to work with AI agents and MCP clients like:

- Claude Desktop (via mcp-remote)
- VS Code extensions with MCP support
- Custom MCP clients

Example client configuration for Claude Desktop:

```json
{
  "mcpServers": {
    "fastapi-mcp-openapi": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

## Development

### Setting up the development environment

```bash
git clone <repository-url>
cd fastapi-mcp-openapi
uv sync
```

### Running tests

```bash
uv run pytest
```

### Building the package

```bash
uv build
```

### Using locally built package
To use the locally built package in another FastAPI project, you can either install it from the wheel file or in editable mode.

```bash
# Option 1: Install from wheel file
pip install /path/to/fastapi_mcp_openapi-0.1.0-py3-none-any.whl
# or with uv
uv add /path/to/fastapi_mcp_openapi-0.1.0-py3-none-any.whl

# Option 2: Install in editable mode
pip install -e /path/to/fastapi-mcp-openapi
# or with uv
uv add --editable /path/to/fastapi-mcp-openapi
```

### Example Application

See `example.py` for a complete example application demonstrating the library's features.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
