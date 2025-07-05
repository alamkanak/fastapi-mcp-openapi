"""Pydantic models for the FastAPI MCP OpenAPI library."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EndpointInfo(BaseModel):
    """Basic information about an API endpoint."""
    
    path: str = Field(..., description="The endpoint path")
    methods: List[str] = Field(..., description="HTTP methods supported by this endpoint")
    name: str = Field(..., description="The endpoint function name")
    summary: Optional[str] = Field(None, description="Brief description of the endpoint")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the endpoint")


class ParameterInfo(BaseModel):
    """Information about an endpoint parameter."""
    
    name: str = Field(..., description="Parameter name")
    in_: str = Field(..., alias="in", description="Parameter location (path, query, header, cookie)")
    required: bool = Field(..., description="Whether the parameter is required")
    schema_: Dict[str, Any] = Field(..., alias="schema", description="Parameter schema")
    description: Optional[str] = Field(None, description="Parameter description")


class ResponseInfo(BaseModel):
    """Information about an endpoint response."""
    
    description: str = Field(..., description="Response description")
    content: Optional[Dict[str, Any]] = Field(None, description="Response content specification")
    headers: Optional[Dict[str, Any]] = Field(None, description="Response headers")


class EndpointDetail(BaseModel):
    """Detailed information about an API endpoint."""
    
    path: str = Field(..., description="The endpoint path")
    method: str = Field(..., description="HTTP method")
    summary: Optional[str] = Field(None, description="Brief description of the endpoint")
    description: Optional[str] = Field(None, description="Detailed description of the endpoint")
    parameters: List[ParameterInfo] = Field(default_factory=list, description="Endpoint parameters")
    request_body: Optional[Dict[str, Any]] = Field(None, description="Request body specification")
    responses: Dict[str, ResponseInfo] = Field(default_factory=dict, description="Response specifications")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the endpoint")
    operation_id: Optional[str] = Field(None, description="Unique operation identifier")
    deprecated: bool = Field(False, description="Whether the endpoint is deprecated")


class EndpointListResponse(BaseModel):
    """Response model for list_endpoints tool."""
    
    endpoints: List[EndpointInfo] = Field(..., description="List of available endpoints")
    total_count: int = Field(..., description="Total number of endpoints")


class EndpointDetailResponse(BaseModel):
    """Response model for get_endpoint_docs tool."""
    
    endpoint: EndpointDetail = Field(..., description="Detailed endpoint information")
    openapi_spec: Dict[str, Any] = Field(..., description="Raw OpenAPI specification for this endpoint")
