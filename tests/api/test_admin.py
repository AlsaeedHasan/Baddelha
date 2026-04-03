import pytest

from app.users.models import User
from tests.factories import ItemFactory, SwapFactory, UserFactory


def test_admin_stats(user_client, db_session):
    client, admin = user_client
    admin.is_admin = True
    db_session.flush()

    UserFactory.create_batch(3)
    ItemFactory.create_batch(2)
    SwapFactory(status="Pending")
    SwapFactory(status="Accepted")
    db_session.flush()

    response = client.get("/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] >= 4  # admin + 3
    assert data["total_items"] >= 2  # 2 items
    assert data["total_swaps_requested"] >= 2
    assert data["total_swaps_completed"] >= 1


def test_admin_stats_forbidden(user_client):
    client, regular_user = user_client
    assert regular_user.is_admin is False

    response = client.get("/admin/stats")
    assert response.status_code == 403


def test_admin_ban_user(user_client, db_session):
    client, admin = user_client
    admin.is_admin = True
    db_session.flush()

    target_user = UserFactory(is_active=True)
    db_session.flush()

    response = client.put(f"/admin/users/{target_user.id}/ban")
    assert response.status_code == 200

    db_session.refresh(target_user)
    assert target_user.is_active is False


def test_admin_ban_user_forbidden(user_client, db_session):
    client, regular_user = user_client

    target_user = UserFactory(is_active=True)
    db_session.flush()

    response = client.put(f"/admin/users/{target_user.id}/ban")
    assert response.status_code == 403

    db_session.refresh(target_user)
    assert target_user.is_active is True
