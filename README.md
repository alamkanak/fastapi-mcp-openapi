# <div align="center">FastAPI MCP OpenAPI</div>

<p align="center">
  <b>Instantly turn your FastAPI API Docs into an AI-friendly, fully introspectable MCP server for LLMs and agents like <a href="https://www.cursor.so/">Cursor</a> and <a href="https://github.com/features/copilot">GitHub Copilot in VS Code</a>.</b><br>
  <i>Discover, document, and stream your endpoints for next-gen AI workflows.</i>
</p>

<!-- Badges -->
<div align="center">
  <a href="https://pypi.org/project/fastapi-mcp-openapi/" style="text-decoration:none;">
    <img src="https://img.shields.io/pypi/v/fastapi-mcp-openapi?label=PyPI%20version" alt="PyPI" />
  </a>
  <a href="https://github.com/alamkanak/fastapi-mcp-openapi/releases" style="text-decoration:none;">
    <img src="https://img.shields.io/github/v/tag/alamkanak/fastapi-mcp-openapi?label=GitHub%20release" alt="GitHub tag (latest by date)" />
  </a>
  <a href="https://app.codecov.io/gh/alamkanak/fastapi-mcp-openapi" style="text-decoration:none;">
    <img src="https://img.shields.io/codecov/c/github/alamkanak/fastapi-mcp-openapi?label=coverage" alt="Codecov" />
  </a>
  <a href="https://github.com/alamkanak/fastapi-mcp-openapi/blob/main/LICENSE" style="text-decoration:none;">
    <img src="https://img.shields.io/pypi/l/fastapi-mcp-openapi" alt="License" />
  </a>
  <a href="https://github.com/astral-sh/ruff" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/linting-ruff-blue?logo=ruff" alt="Ruff" />
  </a>
  <a href="https://github.com/python/mypy" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/type%20checked-mypy-blue" alt="mypy" />
  </a>
</div>

---

## Why use this?

- **Zero-effort LLM/MCP integration:** Expose your FastAPI endpoints to AI agents, Cursor, GitHub Copilot, and other dev tools with a single line of code.
- **Seamless API doc connectivity:** Tools like Cursor and Copilot can instantly discover and use your API docs for autocompletion, endpoint introspection, and more for app development.
- **Full OpenAPI support:** Get detailed, resolved OpenAPI docs for every endpoint—no more guessing what your API does.
- **Streamable, modern protocol:** Implements the latest MCP Streamable HTTP transport for real-time, agent-friendly workflows.
- **Security by default:** CORS, origin validation, and session management out of the box.
- **Production-ready:** Used in real-world AI agent stacks and developer tools.

## Who's using this?

A FastAPI library that provides [Model Context Protocol (MCP)](https://modelcontextprotocol.io) tools for endpoint introspection and OpenAPI documentation. This library allows AI agents to discover and understand your FastAPI endpoints through MCP.

## Features

- **Endpoint Discovery**: Lists all available FastAPI endpoints with metadata
- **OpenAPI Documentation**: Provides detailed OpenAPI schema for specific endpoints with fully resolved inline schemas
- **Clean Output**: Removes unnecessary references and fields for minimal context usage
- **MCP Streamable HTTP Transport**: Full compatibility with the latest MCP protocol (2025-03-26)
- **Easy Integration**: Simple mounting system similar to fastapi-mcp
- **Security**: Built-in CORS protection and origin validation
- **Focused Tool Set**: Only provides tools capability - resources and prompts endpoints are disabled


## 🚀 Try it in 5 minutes

```bash
pip install fastapi-mcp-openapi
# or
uv add fastapi-mcp-openapi
```

Create a file called `main.py`:

```python
from fastapi import FastAPI
from fastapi_mcp_openapi import FastAPIMCPOpenAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/hello")
async def hello():
    return {"message": "Hello, world!"}

mcp = FastAPIMCPOpenAPI(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run it:

```bash
python main.py
```

Visit [http://localhost:8000/mcp](http://localhost:8000/mcp) to see your MCP server in action!

Your MCP server will be available at `http://localhost:8000/mcp` and provides two tools:

1. **listEndpoints**: Get all available endpoints (excluding MCP endpoints)
2. **getEndpointDocs**: Get detailed OpenAPI documentation for a specific endpoint

> [!CAUTION]
> All API endpoints must be fully typed with Pydantic models or FastAPI's native types to ensure proper OpenAPI generation and MCP compatibility.

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

### 1. listEndpoints

Lists all available FastAPI endpoints with their metadata.

**Input**: No parameters required

**Output**: JSON array of endpoint information including:
- `path`: The endpoint path  
- `methods`: Array of HTTP methods
- `name`: Endpoint name
- `summary`: Endpoint summary from docstring

### 2. getEndpointDocs

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

Example client configuration for VS Code Copilot:

```json
{
  "mcpServers": {
    "your-api-name": {
      "url": "http://localhost:8000/mcp",
      "type": "sse",
      "dev": {
          "debug": {
              "type": "web",
          }
      }
    }
  }
}
```

## Development

### Setting up the development environment

```bash
git clone <repository-url>
cd fastapi-mcp-openapi
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running tests

```bash
uv run pytest

# Coverage report (local)
uv run pytest --cov=fastapi_mcp_openapi --cov-report=html

```

### Code Quality

This project uses several tools to maintain code quality:

```bash
# Run linting
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .

# Type checking
mypy fastapi_mcp_openapi --ignore-missing-imports
```

### Building the package

```bash
uv build
```

### Publishing

See [PUBLISHING.md](PUBLISHING.md) for detailed instructions on setting up automated PyPI publishing with GitHub Actions.

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

## Example Applications

This repository includes two example applications in the `examples/` folder demonstrating the library's features:

### Simple Example (`examples/simple_example.py`)

A minimal example showing basic integration:

```bash
# Run the simple example
python examples/simple_example.py
```

This creates a basic FastAPI app with a few endpoints and shows the MCP integration info on startup.

### Complete Example (`examples/advanced_example.py`)

A comprehensive example with multiple endpoint types, Pydantic models, and full CRUD operations:

```bash
# Run the complete example
python examples/advanced_example.py
```

Both examples can be seen in docs url at `http://localhost:8000/docs` after running the application.
Use claude [MCP inspector](https://github.com/modelcontextprotocol/inspector) to see the MCP endpoints and tools. Connect to the MCP server at `http://localhost:8000/mcp` with transport type Streamable HTTP.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
