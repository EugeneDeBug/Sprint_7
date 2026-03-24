import pytest
from helpers import (
    create_courier, delete_courier, login_courier,
    create_order, cancel_order, finish_order, get_order_by_track,
    get_courier_data_valid, get_order_data_base
)

@pytest.fixture
def new_courier():
    """Создаёт курьера, возвращает payload и response. Удаляет после теста."""
    payload = get_courier_data_valid()
    response = create_courier(payload)
    yield payload, response
    login_response = login_courier({"login": payload["login"], "password": payload["password"]})
    if login_response.status_code == 200:
        courier_id = login_response.json()["id"]
        delete_courier(courier_id)

@pytest.fixture
def existing_courier():
    """Создаёт курьера, возвращает payload и courier_id. Удаляет после теста."""
    payload = get_courier_data_valid()
    create_courier(payload)
    login_response = login_courier({"login": payload["login"], "password": payload["password"]})
    courier_id = login_response.json()["id"] if login_response.status_code == 200 else None
    yield payload, courier_id
    if courier_id:
        delete_courier(courier_id)

@pytest.fixture
def new_order():
    """Создаёт заказ, возвращает track. Отменяет после теста."""
    payload = get_order_data_base()
    response = create_order(payload)
    track = response.json().get("track") if response.status_code == 201 else None
    yield track
    if track:
        cancel_order(track)

@pytest.fixture
def new_order_with_id():
    """Создаёт заказ, возвращает track и order_id. Завершает (finish) после теста."""
    payload = get_order_data_base()
    response = create_order(payload)
    track = response.json().get("track") if response.status_code == 201 else None
    order_id = None
    if track:
        order_resp = get_order_by_track(track)
        if order_resp.status_code == 200:
            order_id = order_resp.json()["order"]["id"]
    yield track, order_id
    if order_id:
        finish_order(order_id)
    elif track:
        cancel_order(track)
        