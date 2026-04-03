import tempfile
import uuid
from unittest.mock import mock_open, patch

import pytest

from app.items.models import Comment, Item
from tests.factories import CommentFactory, ItemFactory, UserFactory


def test_create_item(user_client, db_session):
    client, user = user_client
    item_data = {
        "title": "Test Item",
        "description": "Very nice item",
        "estimated_price": 500.0,
        "city": "TestCity",
        "category": "Electronics",
        "transaction_type": "Sell",
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == item_data["title"]
    assert str(data["owner_id"]) == str(user.id)


def test_get_items(client, db_session):
    item1 = ItemFactory(
        title="iPhone 13", city="Cairo", category="Electronics", transaction_type="Sell"
    )
    item2 = ItemFactory(
        title="MacBook", city="Alexandria", category="Laptops", transaction_type="Swap"
    )
    item3 = ItemFactory(
        title="Desk", city="Cairo", category="Furniture", transaction_type="Both"
    )
    db_session.flush()

    # Filter empty
    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # Filter by city
    response = client.get("/items/?city=Cairo")
    assert len(response.json()) == 2

    # Filter by category
    response = client.get("/items/?category=Electronics")
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "iPhone 13"


def test_get_item(client, db_session):
    item = ItemFactory()
    db_session.flush()

    response = client.get(f"/items/{item.id}")
    assert response.status_code == 200
    assert response.json()["title"] == item.title


def test_get_item_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == 404


def test_update_item(user_client, db_session):
    client, user = user_client
    item = ItemFactory(owner=user, title="Old Title")
    db_session.flush()

    response = client.put(
        f"/items/{item.id}", json={"title": "New Title", "estimated_price": 200}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_update_item_not_owner(user_client, db_session):
    client, _ = user_client
    other_user = UserFactory()
    item = ItemFactory(owner=other_user)
    db_session.flush()

    response = client.put(f"/items/{item.id}", json={"title": "New Title"})
    assert response.status_code == 404


def test_delete_item(user_client, db_session):
    client, user = user_client
    item = ItemFactory(owner=user)
    db_session.flush()

    item_id = item.id

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200

    deleted_item = db_session.query(Item).filter(Item.id == item_id).first()
    assert deleted_item is None


def test_add_comment(user_client, db_session):
    client, user = user_client
    item = ItemFactory()
    db_session.flush()

    response = client.post(f"/items/{item.id}/comments", json={"text": "Nice item!"})
    assert response.status_code == 200
    assert response.json()["text"] == "Nice item!"
    assert str(response.json()["author_id"]) == str(user.id)


@patch("app.items.router.open", new_callable=mock_open)
@patch("os.makedirs")
def test_upload_image(mock_makedirs, mock_file, user_client, db_session):
    client, user = user_client
    item = ItemFactory(owner=user)
    db_session.flush()

    pdf_content = b"fake image content"
    response = client.post(
        f"/items/{item.id}/image",
        files={"file": ("test_image.jpg", pdf_content, "image/jpeg")},
    )

    assert response.status_code == 200
    assert "image_url" in response.json()
    assert ".jpg" in response.json()["image_url"]

    db_session.refresh(item)
    assert item.image_url is not None
