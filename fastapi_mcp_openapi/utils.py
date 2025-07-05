"""Utility functions for extracting endpoint information from FastAPI routes."""

import inspect
import logging
from typing import Optional, Set, List, Dict, Any, Callable

from fastapi.routing import APIRoute
from fastapi import params

from .models import EndpointInfo, EndpointDetail, ParameterInfo, ResponseInfo

logger = logging.getLogger(__name__)


def filter_user_endpoints(route, mcp_path: str = "/mcp") -> bool:
    """
    Filter to include only user-defined endpoints.
    
    Excludes MCP endpoints, docs, and other system endpoints.
    
    Args:
        route: FastAPI route object
        mcp_path: Path prefix for MCP endpoints to exclude
    
    Returns:
        True if the route should be included
    """
    if not hasattr(route, 'path') or not hasattr(route, 'methods'):
        return False
    
    path = getattr(route, 'path', '')
    
    # Exclude MCP endpoints
    if path.startswith(mcp_path):
        return False
    
    # Exclude common system endpoints
    system_paths = {
        '/docs', '/redoc', '/openapi.json', '/favicon.ico',
        '/health', '/healthz', '/ready', '/metrics'
    }
    
    if path in system_paths:
        return False
    
    # Exclude routes without methods (like static file routes)
    methods = getattr(route, 'methods', set())
    if not methods or methods == {'HEAD'}:
        return False
    
    return True


def extract_endpoint_info(route) -> Optional[EndpointInfo]:
    """
    Extract basic endpoint information from a FastAPI route.
    
    Args:
        route: FastAPI route object
    
    Returns:
        EndpointInfo object or None if extraction fails
    """
    try:
        if not isinstance(route, APIRoute):
            return None
        
        path = route.path
        methods = list(route.methods - {'HEAD', 'OPTIONS'})  # Exclude HEAD and OPTIONS
        name = route.name or "unnamed"
        
        # Extract summary from docstring or operation summary
        summary = None
        if hasattr(route, 'summary') and route.summary:
            summary = route.summary
        elif hasattr(route, 'endpoint') and route.endpoint:
            docstring = inspect.getdoc(route.endpoint)
            if docstring:
                # Use first line of docstring as summary
                summary = docstring.split('\n')[0].strip()
        
        # Extract tags
        tags = []
        if hasattr(route, 'tags') and route.tags:
            tags = list(route.tags)
        
        return EndpointInfo(
            path=path,
            methods=methods,
            name=name,
            summary=summary,
            tags=tags
        )
    
    except Exception as e:
        logger.warning(f"Failed to extract endpoint info for route: {e}")
        return None


def extract_endpoint_detail(route, method: str) -> Optional[EndpointDetail]:
    """
    Extract detailed endpoint information from a FastAPI route.
    
    Args:
        route: FastAPI route object
        method: HTTP method to get details for
    
    Returns:
        EndpointDetail object or None if extraction fails
    """
    try:
        if not isinstance(route, APIRoute):
            return None
        
        path = route.path
        
        # Extract summary and description
        summary = None
        description = None
        
        if hasattr(route, 'summary') and route.summary:
            summary = route.summary
        if hasattr(route, 'description') and route.description:
            description = route.description
        elif hasattr(route, 'endpoint') and route.endpoint:
            docstring = inspect.getdoc(route.endpoint)
            if docstring:
                lines = docstring.split('\n')
                if not summary:
                    summary = lines[0].strip()
                if len(lines) > 1:
                    description = '\n'.join(line.strip() for line in lines[1:]).strip()
        
        # Extract parameters
        parameters = []
        if hasattr(route, 'dependant') and route.dependant:
            parameters = _extract_parameters_from_dependant(route.dependant)
        
        # Extract request body info
        request_body = None
        if hasattr(route, 'body_field') and route.body_field:
            request_body = _extract_request_body_info(route.body_field)
        
        # Extract response info
        responses = {}
        if hasattr(route, 'responses') and route.responses:
            for status_code, response_info in route.responses.items():
                responses[str(status_code)] = _extract_response_info(response_info)
        
        # Default 200 response if none specified
        if not responses:
            responses["200"] = ResponseInfo(
                description="Successful Response",
                content={"application/json": {"schema": {}}}
            )
        
        # Extract tags
        tags = []
        if hasattr(route, 'tags') and route.tags:
            tags = list(route.tags)
        
        # Extract operation ID
        operation_id = getattr(route, 'operation_id', None)
        
        # Check if deprecated
        deprecated = getattr(route, 'deprecated', False) or False
        
        return EndpointDetail(
            path=path,
            method=method.upper(),
            summary=summary,
            description=description,
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            tags=tags,
            operation_id=operation_id,
            deprecated=deprecated
        )
    
    except Exception as e:
        logger.warning(f"Failed to extract endpoint detail for route {method} {route.path}: {e}")
        return None


def _extract_parameters_from_dependant(dependant) -> List[ParameterInfo]:
    """Extract parameter information from FastAPI dependant."""
    parameters = []
    
    try:
        # Path parameters
        for param in getattr(dependant, 'path_params', []):
            param_info = _create_parameter_info(param, "path")
            if param_info:
                parameters.append(param_info)
        
        # Query parameters
        for param in getattr(dependant, 'query_params', []):
            param_info = _create_parameter_info(param, "query")
            if param_info:
                parameters.append(param_info)
        
        # Header parameters
        for param in getattr(dependant, 'header_params', []):
            param_info = _create_parameter_info(param, "header")
            if param_info:
                parameters.append(param_info)
        
        # Cookie parameters
        for param in getattr(dependant, 'cookie_params', []):
            param_info = _create_parameter_info(param, "cookie")
            if param_info:
                parameters.append(param_info)
    
    except Exception as e:
        logger.warning(f"Failed to extract parameters from dependant: {e}")
    
    return parameters


def _create_parameter_info(param, location: str) -> Optional[ParameterInfo]:
    """Create ParameterInfo from a FastAPI parameter."""
    try:
        name = getattr(param, 'alias', None) or getattr(param, 'name', 'unknown')
        
        # Check if parameter is required
        required = True
        if hasattr(param, 'default'):
            # Handle different types of default values
            default_val = param.default
            required = default_val is None or (hasattr(param, 'empty') and default_val != param.empty)
        
        # Extract schema information
        schema = {"type": "string"}  # Default
        if hasattr(param, 'annotation'):
            schema = _get_schema_from_annotation(param.annotation)
        
        description = getattr(param, 'description', None)
        
        return ParameterInfo(
            name=name,
            **{"in": location},  # Use dict unpacking for the 'in' field
            required=required,
            schema=schema,
            description=description
        )
    
    except Exception as e:
        logger.warning(f"Failed to create parameter info: {e}")
        return None


def _extract_request_body_info(body_field) -> Optional[Dict[str, Any]]:
    """Extract request body information from FastAPI body field."""
    try:
        if not body_field:
            return None
        
        # Basic request body structure
        request_body = {
            "content": {
                "application/json": {
                    "schema": _get_schema_from_annotation(body_field.type_)
                }
            },
            "required": body_field.required
        }
        
        if hasattr(body_field, 'description') and body_field.description:
            request_body["description"] = body_field.description
        
        return request_body
    
    except Exception as e:
        logger.warning(f"Failed to extract request body info: {e}")
        return None


def _extract_response_info(response_info) -> ResponseInfo:
    """Extract response information."""
    try:
        description = getattr(response_info, 'description', 'Successful Response')
        content = getattr(response_info, 'content', None)
        headers = getattr(response_info, 'headers', None)
        
        return ResponseInfo(
            description=description,
            content=content,
            headers=headers
        )
    
    except Exception:
        return ResponseInfo(
            description="Response",
            content=None,
            headers=None
        )


def _get_schema_from_annotation(annotation) -> Dict[str, Any]:
    """Get JSON schema from Python type annotation."""
    try:
        # Basic type mapping
        type_mapping = {
            int: {"type": "integer"},
            float: {"type": "number"},
            str: {"type": "string"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
        }
        
        if annotation in type_mapping:
            return type_mapping[annotation]
        
        # Handle Optional types
        if hasattr(annotation, '__origin__'):
            origin = annotation.__origin__
            if origin is list:
                args = getattr(annotation, '__args__', ())
                if args:
                    return {
                        "type": "array",
                        "items": _get_schema_from_annotation(args[0])
                    }
                return {"type": "array"}
            
            elif origin is dict:
                return {"type": "object"}
        
        # Default to string for unknown types
        return {"type": "string"}
    
    except Exception:
        return {"type": "string"}
