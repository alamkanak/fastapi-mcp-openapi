"""Pytest configuration and shared fixtures for tests."""

import pytest
from fastapi import FastAPI


@pytest.fixture
def test_app():
    """Create a test FastAPI app for use in tests."""
    app = FastAPI(title="Test API", version="1.0.0")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Hello World"}

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        """Get a user by ID."""
        return {"user_id": user_id, "name": f"User {user_id}"}

    @app.post("/users/")
    async def create_user(name: str):
        """Create a new user."""
        return {"message": f"Created user {name}"}

    return app
