"""
Advanced example showing custom configuration of fastapi-mcp-openapi.

This example demonstrates:
- Custom MCP path
- Custom endpoint filtering
- Standalone MCP server usage
- CORS configuration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from fastapi_mcp_openapi import mount_mcp_openapi, create_standalone_mcp_server

app = FastAPI(
    title="Advanced API Example",
    description="Demonstrates advanced features of fastapi-mcp-openapi",
    version="2.0.0"
)


# Custom endpoint filter function
def custom_endpoint_filter(route, mcp_path: str) -> bool:
    """
    Custom filter to exclude internal and admin endpoints.
    
    This filter excludes:
    - MCP endpoints (handled automatically)
    - Internal endpoints (starting with /internal)
    - Admin endpoints (starting with /admin)
    - System endpoints
    """
    if not hasattr(route, 'path') or not hasattr(route, 'methods'):
        return False
    
    path = getattr(route, 'path', '')
    
    # Exclude MCP endpoints (already handled by default filter)
    if path.startswith(mcp_path):
        return False
    
    # Exclude internal and admin endpoints
    if path.startswith('/internal') or path.startswith('/admin'):
        return False
    
    # Exclude system endpoints
    system_paths = {'/health', '/metrics', '/status'}
    if path in system_paths:
        return False
    
    return True


# Mount MCP tools with custom configuration
mcp_server = mount_mcp_openapi(
    app,
    mcp_path="/api-introspection",  # Custom path
    endpoint_filter=custom_endpoint_filter,  # Custom filter
    server_name="advanced-api-server",
    server_version="2.0.0",
    enable_cors=True,
    cors_origins=["http://localhost:3000", "https://myapp.com"]
)


# Sample models
class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str
    in_stock: bool = True


class CreateProductRequest(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True


# Sample data
products_db = [
    Product(id=1, name="Laptop", price=999.99, category="Electronics"),
    Product(id=2, name="Book", price=19.99, category="Education"),
    Product(id=3, name="Coffee Mug", price=12.99, category="Kitchen"),
]


# Public API endpoints (will be included in MCP introspection)
@app.get("/")
async def root():
    """Welcome endpoint for the Advanced API."""
    return {"message": "Welcome to the Advanced API!", "version": "2.0.0"}


@app.get("/products", response_model=List[Product], tags=["products"])
async def list_products(category: Optional[str] = None, in_stock: Optional[bool] = None):
    """
    List all products with optional filtering.
    
    Args:
        category: Filter by product category
        in_stock: Filter by stock availability
    
    Returns:
        List of products matching the criteria
    """
    filtered_products = products_db
    
    if category:
        filtered_products = [p for p in filtered_products if p.category.lower() == category.lower()]
    
    if in_stock is not None:
        filtered_products = [p for p in filtered_products if p.in_stock == in_stock]
    
    return filtered_products


@app.get("/products/{product_id}", response_model=Product, tags=["products"])
async def get_product(product_id: int):
    """Get a product by ID."""
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=Product, tags=["products"])
async def create_product(product_data: CreateProductRequest):
    """Create a new product."""
    new_id = max(p.id for p in products_db) + 1 if products_db else 1
    new_product = Product(id=new_id, **product_data.dict())
    products_db.append(new_product)
    return new_product


# Internal endpoints (will be excluded by custom filter)
@app.get("/internal/stats")
async def internal_stats():
    """Internal endpoint for system statistics."""
    return {"total_products": len(products_db), "categories": len(set(p.category for p in products_db))}


@app.get("/internal/debug")
async def internal_debug():
    """Internal debug endpoint."""
    return {"debug": True, "products_db": products_db}


# Admin endpoints (will be excluded by custom filter)
@app.post("/admin/reset")
async def admin_reset():
    """Admin endpoint to reset the database."""
    global products_db
    products_db.clear()
    return {"message": "Database reset"}


@app.get("/admin/users")
async def admin_list_users():
    """Admin endpoint to list all users."""
    return {"users": ["admin", "user1", "user2"]}


# System endpoints (will be excluded by custom filter)
@app.get("/health")
async def health_check():
    """System health check."""
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """System metrics."""
    return {"requests": 100, "uptime": "1h"}


# Example of creating a standalone MCP server
def create_standalone_example():
    """
    Example of creating a standalone MCP server.
    
    This can be useful when you want to run the MCP server
    separately from the main FastAPI application.
    """
    standalone_server = create_standalone_mcp_server(
        app,
        endpoint_filter=custom_endpoint_filter,
        server_name="standalone-introspection-server",
        server_version="1.0.0"
    )
    
    # Get the MCP app for independent use
    mcp_app = standalone_server.get_mcp_app()
    
    return mcp_app


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Advanced API Example...")
    print("API documentation: http://localhost:8000/docs")
    print("MCP endpoints: http://localhost:8000/api-introspection")
    print()
    print("Available endpoints for MCP introspection:")
    print("- GET /")
    print("- GET /products")
    print("- GET /products/{product_id}")
    print("- POST /products")
    print()
    print("Excluded from MCP (due to custom filter):")
    print("- /internal/* (internal endpoints)")
    print("- /admin/* (admin endpoints)")
    print("- /health, /metrics (system endpoints)")
    print()
    print("MCP Tools available:")
    print("1. list_endpoints - Lists only the public API endpoints")
    print("2. get_endpoint_docs - Get detailed docs for any public endpoint")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
