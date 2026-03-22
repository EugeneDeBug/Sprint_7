import pytest
import time
from helpers import (
    create_courier, delete_courier, login_courier,
    create_order, cancel_order, get_courier_data_valid, get_order_data_base
)

@pytest.fixture
def new_courier():    
    payload = get_courier_data_valid()
    response = create_courier(payload)
    assert response.status_code == 201
    yield payload    
    login_response = login_courier({"login": payload["login"], "password": payload["password"]})
    assert login_response.status_code == 200
    courier_id = login_response.json()["id"]
    delete_courier(courier_id)

@pytest.fixture
def existing_courier():    
    payload = get_courier_data_valid()
    response = create_courier(payload)
    assert response.status_code == 201
    login_response = login_courier({"login": payload["login"], "password": payload["password"]})
    assert login_response.status_code == 200
    courier_id = login_response.json()["id"]
    yield payload, courier_id
    delete_courier(courier_id)

@pytest.fixture
def new_order():
    
    payload = get_order_data_base()
    response = create_order(payload)
    assert response.status_code == 201
    track = response.json()["track"]
    time.sleep(1)  
    yield track
    cancel_order(track)
    