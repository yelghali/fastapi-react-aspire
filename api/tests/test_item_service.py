"""Unit tests for the Items service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from app.modules.items.schemas import Item, ItemCreate, ItemUpdate
from app.modules.items.service import ItemService


@pytest.fixture
def service() -> ItemService:
    """Create a fresh item service for each test."""
    return ItemService()


@pytest.mark.asyncio
async def test_list_items_sorts_by_created_at_desc(service: ItemService):
    """Items should be returned newest first."""
    older = datetime.now(UTC) - timedelta(days=1)
    newer = datetime.now(UTC)

    service._items = {
        "older": Item(
            id="older",
            name="Older",
            description="",
            is_active=True,
            created_at=older,
            updated_at=older,
        ),
        "newer": Item(
            id="newer",
            name="Newer",
            description="",
            is_active=False,
            created_at=newer,
            updated_at=newer,
        ),
    }

    result = await service.list_items()

    assert [item.id for item in result] == ["newer", "older"]


@pytest.mark.asyncio
async def test_list_items_active_only_filters_inactive_items(service: ItemService):
    """Inactive items should be removed when active_only is enabled."""
    service._items["inactive"] = Item(
        id="inactive",
        name="Inactive",
        description="",
        is_active=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    result = await service.list_items(active_only=True)

    assert all(item.is_active for item in result)
    assert "inactive" not in [item.id for item in result]


@pytest.mark.asyncio
async def test_create_item_generates_id_and_persists(service: ItemService):
    """Creating an item should generate a new ID and store it."""
    item_create = ItemCreate(name="New Item", description="A new item")

    with patch("app.modules.items.service.uuid.uuid4") as mock_uuid:
        mock_uuid.return_value.hex = "1234567890abcdef"

        result = await service.create_item(item_create)

    assert result.id == "item-12345678"
    assert result.name == "New Item"
    assert service._items[result.id] == result


@pytest.mark.asyncio
async def test_update_item_updates_only_provided_fields(service: ItemService):
    """Partial updates should preserve existing values."""
    created_at = datetime.now(UTC) - timedelta(hours=1)
    existing = Item(
        id="item-1",
        name="Original",
        description="Original description",
        is_active=True,
        created_at=created_at,
        updated_at=created_at,
    )
    service._items[existing.id] = existing

    result = await service.update_item(
        "item-1",
        ItemUpdate(description="Updated description"),
    )

    assert result is not None
    assert result.name == "Original"
    assert result.description == "Updated description"
    assert result.updated_at > created_at


@pytest.mark.asyncio
async def test_update_item_missing_returns_none(service: ItemService):
    """Updating a missing item should return None."""
    result = await service.update_item("missing", ItemUpdate(name="Nope"))

    assert result is None


@pytest.mark.asyncio
async def test_delete_item_removes_existing_item(service: ItemService):
    """Deleting an existing item should remove it from storage."""
    service._items["item-1"] = Item(
        id="item-1",
        name="Delete me",
        description="",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    result = await service.delete_item("item-1")

    assert result is True
    assert "item-1" not in service._items


@pytest.mark.asyncio
async def test_delete_item_missing_returns_false(service: ItemService):
    """Deleting a missing item should return False."""
    result = await service.delete_item("missing")

    assert result is False
