"""Tests for the Items module."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch

from app.main import app


@pytest.fixture
async def client():
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient):
    """Test listing items returns sample data."""
    response = await client.get("/api/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Sample data


@pytest.mark.asyncio
async def test_list_items_active_only_filters_results(client: AsyncClient):
    """Test listing only active items forwards the query flag."""
    with patch("app.modules.items.service.ItemService.list_items") as mock_list:
        mock_list.return_value = []

        response = await client.get("/api/items/?active_only=true")

        assert response.status_code == 200
        mock_list.assert_called_once_with(active_only=True)


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient):
    """Test getting a specific item."""
    response = await client.get("/api/items/item-1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "item-1"
    assert data["name"] == "Welcome Item"


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient):
    """Test getting a non-existent item returns 404."""
    response = await client.get("/api/items/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item_not_found(client: AsyncClient):
    """Test updating a missing item returns 404."""
    with patch("app.modules.items.service.ItemService.update_item") as mock_update:
        mock_update.return_value = None

        response = await client.patch(
            "/api/items/missing-item",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Item 'missing-item' not found"


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    """Test creating a new item."""
    response = await client.post(
        "/api/items/",
        json={"name": "Test Item", "description": "A test item"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "A test item"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_item_validation_error(client: AsyncClient):
    """Test that invalid item payloads are rejected."""
    response = await client.post(
        "/api/items/",
        json={"name": "", "description": "A test item"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_item(client: AsyncClient):
    """Test updating an existing item."""
    response = await client.patch(
        "/api/items/item-1",
        json={"name": "Updated Item"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Item"


@pytest.mark.asyncio
async def test_delete_item_not_found(client: AsyncClient):
    """Test deleting a missing item returns 404."""
    with patch("app.modules.items.service.ItemService.delete_item") as mock_delete:
        mock_delete.return_value = False

        response = await client.delete("/api/items/missing-item")

        assert response.status_code == 404
        assert response.json()["detail"] == "Item 'missing-item' not found"


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient):
    """Test deleting an item."""
    # First create an item to delete
    create_response = await client.post(
        "/api/items/",
        json={"name": "To Delete"},
    )
    item_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.text == "Healthy"
