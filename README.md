# FastAPI MCP OpenAPI

A FastAPI library that provides Model Context Protocol (MCP) tools for endpoint introspection and documentation.

## Features

- **Zero Configuration**: Simply mount the library to your FastAPI app
- **Endpoint Discovery**: List all user-defined endpoints in your FastAPI application
- **Detailed Documentation**: Get comprehensive OpenAPI documentation for any endpoint
- **MCP Compatible**: Uses the latest Model Context Protocol standards
- **Lightweight**: Minimal overhead with automatic filtering of MCP endpoints

## Installation

```bash
pip install fastapi-mcp-openapi
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_mcp_openapi import mount_mcp_openapi

app = FastAPI()

# Mount the MCP OpenAPI tools
mount_mcp_openapi(app)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a user by ID."""
    return {"user_id": user_id, "name": "John Doe"}

@app.post("/users")
async def create_user(user: dict):
    """Create a new user."""
    return {"message": "User created", "user": user}
```

## Available MCP Tools

### 1. `list_endpoints`
Lists all user-defined endpoints in the FastAPI application, excluding MCP endpoints.

**Usage:**
```json
{
    "tool": "list_endpoints",
    "arguments": {}
}
```

**Response:**
```json
{
    "endpoints": [
        {
            "path": "/users/{user_id}",
            "methods": ["GET"],
            "name": "get_user",
            "summary": "Get a user by ID."
        },
        {
            "path": "/users",
            "methods": ["POST"],
            "name": "create_user",
            "summary": "Create a new user."
        }
    ]
}
```

### 2. `get_endpoint_docs`
Gets detailed OpenAPI documentation for a specific endpoint.

**Usage:**
```json
{
    "tool": "get_endpoint_docs",
    "arguments": {
        "endpoint_path": "/users/{user_id}",
        "method": "GET"
    }
}
```

**Response:**
```json
{
    "path": "/users/{user_id}",
    "method": "GET",
    "summary": "Get a user by ID.",
    "description": "Get a user by ID.",
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "required": true,
            "schema": {
                "type": "integer"
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {}
                }
            }
        }
    }
}
```

## Configuration Options

You can customize the MCP mounting behavior:

```python
from fastapi_mcp_openapi import mount_mcp_openapi

# Custom path prefix for MCP endpoints
mount_mcp_openapi(app, mcp_path="/custom-mcp")

# Custom endpoint filtering
def custom_filter(route):
    return not route.path.startswith("/internal")

mount_mcp_openapi(app, endpoint_filter=custom_filter)
```

## Requirements

- Python 3.8+
- FastAPI 0.68.0+
- MCP 1.0.0+

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
