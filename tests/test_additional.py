import allure
import requests
from helpers import (
    delete_courier, login_courier, get_order_by_track, cancel_order,
    accept_order, create_order, BASE_URL,
    get_order_data_base,create_courier,get_courier_data_valid,
    NON_EXISTENT_COURIER_ID, NON_EXISTENT_ORDER_ID, NON_EXISTENT_TRACK
)

@allure.feature("Курьер")
class TestDeleteCourier:
    

    @allure.title("Успешное удаление курьера")
    def test_delete_courier_success(self):
        
        payload = get_courier_data_valid()
        response = create_courier(payload)
        assert response.status_code == 201
        login_resp = login_courier({"login": payload["login"], "password": payload["password"]})
        assert login_resp.status_code == 200
        courier_id = login_resp.json()["id"]
        response = delete_courier(courier_id)
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        #second_login = login_courier({"login": payload["login"], "password": payload["password"]})
        #assert second_login.status_code == 404
    
    @allure.title("Удаление несуществующего курьера")
    def test_delete_nonexistent_courier(self):        
        response = delete_courier(NON_EXISTENT_COURIER_ID)
        assert response.status_code == 404
        # Реальное сообщение API содержит точку в конце
        assert response.json()["message"] == "Курьера с таким id нет."

    @allure.title("Удаление курьера без id")
    def test_delete_courier_without_id(self):        
        response = delete_courier("")
        assert response.status_code == 404


@allure.feature("Заказы")
class TestAcceptOrder:    

    @allure.title("Успешное принятие заказа курьером")
    def test_accept_order_success(self, existing_courier):        
        _, courier_id = existing_courier
        
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        assert order_response.status_code == 201
        track = order_response.json()["track"]
        
        order_resp = get_order_by_track(track)
        order_id = order_resp.json()["order"]["id"]

        response = accept_order(order_id, courier_id)
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        cancel_order(track)

    @allure.title("Принятие заказа без courierId")
    def test_accept_order_missing_courier_id(self):        
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        assert order_response.status_code == 201
        track = order_response.json()["track"]
        order_resp = get_order_by_track(track)
        order_id = order_resp.json()["order"]["id"]

        response = requests.put(f"{BASE_URL}/orders/accept/{order_id}")
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для поиска"

        cancel_order(track)

    @allure.title("Принятие заказа с неверным courierId")
    def test_accept_order_wrong_courier_id(self):        
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        assert order_response.status_code == 201
        track = order_response.json()["track"]
        order_resp = get_order_by_track(track)
        order_id = order_resp.json()["order"]["id"]

        response = accept_order(order_id, NON_EXISTENT_COURIER_ID)
        assert response.status_code == 404
        # Реальное сообщение API
        assert response.json()["message"] == "Курьера с таким id не существует"

        cancel_order(track)

    @allure.title("Принятие заказа с неверным orderId")
    def test_accept_order_wrong_order_id(self, existing_courier):        
        _, courier_id = existing_courier
        response = accept_order(NON_EXISTENT_ORDER_ID, courier_id)
        assert response.status_code == 404
        # Реальное сообщение API
        assert response.json()["message"] == "Заказа с таким id не существует"


@allure.feature("Заказы")
class TestGetOrderByTrack:    

    @allure.title("Получение заказа по треку")
    def test_get_order_by_track_success(self, new_order):        
        track = new_order
        response = get_order_by_track(track)
        assert response.status_code == 200
        assert response.json()["order"]["track"] == track

    @allure.title("Получение заказа без трека")
    def test_get_order_without_track(self):        
        response = requests.get(f"{BASE_URL}/orders/track")
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для поиска"

    @allure.title("Получение заказа с несуществующим треком")
    def test_get_order_nonexistent_track(self):        
        response = get_order_by_track(NON_EXISTENT_TRACK)
        assert response.status_code == 404
        assert response.json()["message"] == "Заказ не найден"


@allure.feature("Заказы")
class TestCancelOrder:    
    @allure.title("Успешная отмена заказа")
    def test_cancel_order_success(self):        
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        assert order_response.status_code == 201
        track = order_response.json()["track"]

        response = cancel_order(track)
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    @allure.title("Отмена заказа без трека")
    def test_cancel_order_without_track(self):        
        response = requests.put(f"{BASE_URL}/orders/cancel")
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для поиска"

    @allure.title("Отмена несуществующего заказа")
    def test_cancel_nonexistent_order(self):    
        response = cancel_order(NON_EXISTENT_TRACK)
        assert response.status_code == 404
        assert response.json()["message"] == "Заказ не найден"
