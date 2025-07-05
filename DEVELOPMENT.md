# Development Guide

## Setup

1. Clone the repository and navigate to the project directory
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Project Structure

```
fastapi-mcp-openapi/
├── fastapi_mcp_openapi/           # Main library package
│   ├── __init__.py               # Package exports
│   ├── main.py                   # Mount functions
│   ├── server.py                 # MCP server implementation
│   ├── models.py                 # Pydantic models
│   ├── utils.py                  # Utility functions
│   └── version.py                # Version information
├── examples/                     # Usage examples
│   ├── basic_example.py          # Basic usage
│   └── advanced_example.py       # Advanced features
├── tests/                        # Test files
│   └── test_basic.py             # Basic tests
├── docs/                         # Documentation
├── pyproject.toml                # Project configuration
├── requirements.txt              # Dependencies
├── README.md                     # Main documentation
└── LICENSE                       # MIT License
```

## Running Examples

### Basic Example
```bash
python examples/basic_example.py
```

This starts a FastAPI server with:
- Basic CRUD operations for users
- MCP tools mounted at `/mcp`
- API docs at `http://localhost:8000/docs`

### Advanced Example
```bash
python examples/advanced_example.py
```

This demonstrates:
- Custom MCP path (`/api-introspection`)
- Custom endpoint filtering
- CORS configuration
- Excluded internal/admin endpoints

## Testing

Run the basic tests:
```bash
python tests/test_basic.py
```

Or use pytest:
```bash
pytest tests/
```

## Using the MCP Tools

Once you have a FastAPI app running with the library mounted, you can use the MCP tools:

### 1. List Endpoints
```json
{
    "tool": "list_endpoints",
    "arguments": {}
}
```

### 2. Get Endpoint Documentation
```json
{
    "tool": "get_endpoint_docs",
    "arguments": {
        "endpoint_path": "/users/{user_id}",
        "method": "GET"
    }
}
```

## Development Workflow

1. Make changes to the library code
2. Test your changes with the examples:
   ```bash
   python examples/basic_example.py
   ```
3. Run tests to ensure nothing is broken:
   ```bash
   python tests/test_basic.py
   ```
4. Format code:
   ```bash
   black fastapi_mcp_openapi/
   isort fastapi_mcp_openapi/
   ```

## Building and Publishing

To build the package:
```bash
python -m build
```

To publish to PyPI (requires credentials):
```bash
python -m twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Architecture

The library consists of several key components:

1. **Main Module** (`main.py`): Provides the `mount_mcp_openapi()` function that users call to add MCP tools to their FastAPI app.

2. **MCP Server** (`server.py`): Implements the actual MCP server using FastMCP, providing the two tools:
   - `list_endpoints`: Lists all user-defined endpoints
   - `get_endpoint_docs`: Gets detailed documentation for a specific endpoint

3. **Models** (`models.py`): Pydantic models for structured data:
   - `EndpointInfo`: Basic endpoint information
   - `EndpointDetail`: Detailed endpoint information
   - `ParameterInfo`: Parameter specifications
   - `ResponseInfo`: Response specifications

4. **Utilities** (`utils.py`): Helper functions for:
   - Filtering user endpoints vs system endpoints
   - Extracting endpoint information from FastAPI routes
   - Converting FastAPI route info to structured models

The library automatically discovers FastAPI routes and converts them into structured information that can be consumed by MCP clients.
