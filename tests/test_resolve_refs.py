"""
Tests for the _resolve_refs method functionality.
"""

from fastapi_mcp_openapi import FastAPIMCPOpenAPI


class TestResolveRefs:
    """Test reference resolution functionality."""

    def test_resolve_refs_primitive_types(self, basic_app):
        """Test _resolve_refs with primitive types."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        # Test string
        result = mcp._resolve_refs("test_string", {})
        assert result == "test_string"

        # Test number
        result = mcp._resolve_refs(42, {})
        assert result == 42

        # Test boolean
        result = mcp._resolve_refs(True, {})
        assert result is True

        # Test None
        result = mcp._resolve_refs(None, {})
        assert result is None

    def test_resolve_refs_list(self, basic_app):
        """Test _resolve_refs with lists."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        # Test simple list
        test_list = ["a", "b", "c"]
        result = mcp._resolve_refs(test_list, {})
        assert result == ["a", "b", "c"]

        # Test list with nested objects
        test_list = [{"key": "value"}, "string", 42]
        result = mcp._resolve_refs(test_list, {})
        assert result == [{"key": "value"}, "string", 42]

    def test_resolve_refs_dict_without_ref(self, basic_app):
        """Test _resolve_refs with dictionary without $ref."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        test_dict = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        }

        result = mcp._resolve_refs(test_dict, {})
        assert result == test_dict

    def test_resolve_refs_simple_ref(self, basic_app):
        """Test _resolve_refs with simple $ref."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        openapi_schema = {
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                        },
                    }
                }
            }
        }

        ref_obj = {"$ref": "#/components/schemas/User"}
        result = mcp._resolve_refs(ref_obj, openapi_schema)

        expected = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}},
        }
        assert result == expected

    def test_resolve_refs_nested_ref(self, basic_app):
        """Test _resolve_refs with nested references."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        openapi_schema = {
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "address": {"$ref": "#/components/schemas/Address"},
                        },
                    },
                    "Address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                        },
                    },
                }
            }
        }

        ref_obj = {"$ref": "#/components/schemas/User"}
        result = mcp._resolve_refs(ref_obj, openapi_schema)

        expected = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                },
            },
        }
        assert result == expected

    def test_resolve_refs_ref_not_found(self, basic_app):
        """Test _resolve_refs with non-existent reference."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        openapi_schema = {
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    }
                }
            }
        }

        ref_obj = {"$ref": "#/components/schemas/NonExistent"}
        result = mcp._resolve_refs(ref_obj, openapi_schema)

        # Should return the original $ref when not found
        assert result == {"$ref": "#/components/schemas/NonExistent"}

    def test_resolve_refs_external_ref(self, basic_app):
        """Test _resolve_refs with external reference."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        openapi_schema = {}
        external_ref = {"$ref": "https://example.com/schemas/User.json"}
        result = mcp._resolve_refs(external_ref, openapi_schema)

        # External references should be returned as-is
        assert result == {"$ref": "https://example.com/schemas/User.json"}

    def test_resolve_refs_complex_nested_structure(self, basic_app):
        """Test _resolve_refs with complex nested structure."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        openapi_schema = {
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                    "Post": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"$ref": "#/components/schemas/User"},
                        },
                    },
                }
            }
        }

        complex_obj = {
            "type": "object",
            "properties": {
                "posts": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Post"},
                },
                "user": {"$ref": "#/components/schemas/User"},
            },
        }

        result = mcp._resolve_refs(complex_obj, openapi_schema)

        expected = {
            "type": "object",
            "properties": {
                "posts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "author": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                            },
                        },
                    },
                },
                "user": {"type": "object", "properties": {"name": {"type": "string"}}},
            },
        }
        assert result == expected

    def test_resolve_refs_circular_reference_protection(self, basic_app):
        """Test _resolve_refs with potentially circular references."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        # Create a schema that could cause infinite recursion
        openapi_schema = {
            "components": {
                "schemas": {
                    "Node": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "child": {"$ref": "#/components/schemas/Node"},
                        },
                    }
                }
            }
        }

        ref_obj = {"$ref": "#/components/schemas/Node"}
        result = mcp._resolve_refs(ref_obj, openapi_schema)

        # Should resolve the first level without infinite recursion
        assert result["type"] == "object"
        assert "value" in result["properties"]
        assert "child" in result["properties"]

        # The child should still be a reference to prevent infinite recursion
        child_ref = result["properties"]["child"]
        assert child_ref == {"$ref": "#/components/schemas/Node"}

    def test_resolve_refs_malformed_ref_path(self, basic_app):
        """Test _resolve_refs with malformed reference path."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        openapi_schema = {"components": {"schemas": {"User": {"type": "object"}}}}

        # Test with invalid path structure
        malformed_ref = {"$ref": "#/invalid/path/structure"}
        result = mcp._resolve_refs(malformed_ref, openapi_schema)

        # Should return the original ref when path is invalid
        assert result == {"$ref": "#/invalid/path/structure"}

    def test_resolve_refs_empty_schema(self, basic_app):
        """Test _resolve_refs with empty schema."""
        mcp = FastAPIMCPOpenAPI(basic_app)

        ref_obj = {"$ref": "#/components/schemas/User"}
        result = mcp._resolve_refs(ref_obj, {})

        # Should return the original ref when schema is empty
        assert result == {"$ref": "#/components/schemas/User"}
