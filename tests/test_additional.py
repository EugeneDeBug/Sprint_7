import allure
import requests
from helpers import (
    get_order_by_track, cancel_order, accept_order, finish_order,
    create_order, get_order_data_base, NON_EXISTENT_COURIER_ID,
    NON_EXISTENT_ORDER_ID, NON_EXISTENT_TRACK, BASE_URL
)
from data.messages import (
    COURIER_NOT_EXISTS, ORDER_NOT_EXISTS, ORDER_NOT_FOUND,
    INSUFFICIENT_SEARCH_DATA
)


@allure.feature("Принятие заказа")
class TestAcceptOrder:

    @allure.title("Успешное принятие заказа курьером")
    def test_accept_order_success(self, existing_courier, new_order_with_id):
        _, courier_id = existing_courier
        track, order_id = new_order_with_id
        with allure.step("Принять заказ курьером"):
            response = accept_order(order_id, courier_id)
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        # заказ будет удалён фикстурой new_order_with_id

    @allure.title("Принятие заказа без courierId")
    def test_accept_order_missing_courier_id(self):
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        track = order_response.json()["track"]
        order_resp = get_order_by_track(track)
        order_id = order_resp.json()["order"]["id"]
        with allure.step("Отправить запрос на принятие заказа без courierId"):
            response = requests.put(f"{BASE_URL}/orders/accept/{order_id}")
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_SEARCH_DATA
        with allure.step("Отменить заказ для очистки"):
            cancel_order(track)

    @allure.title("Принятие заказа с неверным courierId")
    def test_accept_order_wrong_courier_id(self):
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        track = order_response.json()["track"]
        order_resp = get_order_by_track(track)
        order_id = order_resp.json()["order"]["id"]
        with allure.step(f"Принять заказ с неверным courierId {NON_EXISTENT_COURIER_ID}"):
            response = accept_order(order_id, NON_EXISTENT_COURIER_ID)
        assert response.status_code == 404
        assert response.json()["message"] == COURIER_NOT_EXISTS
        with allure.step("Отменить заказ для очистки"):
            cancel_order(track)

    @allure.title("Принятие заказа с неверным orderId")
    def test_accept_order_wrong_order_id(self, existing_courier):
        _, courier_id = existing_courier
        with allure.step(f"Принять заказ с неверным orderId {NON_EXISTENT_ORDER_ID}"):
            response = accept_order(NON_EXISTENT_ORDER_ID, courier_id)
        assert response.status_code == 404
        assert response.json()["message"] == ORDER_NOT_EXISTS


@allure.feature("Получение заказа")
class TestGetOrderByTrack:

    @allure.title("Получение заказа по треку")
    def test_get_order_by_track_success(self, new_order):
        track = new_order
        with allure.step(f"Получить заказ по треку {track}"):
            response = get_order_by_track(track)
        assert response.status_code == 200
        assert response.json()["order"]["track"] == track

    @allure.title("Получение заказа без трека")
    def test_get_order_without_track(self):
        with allure.step("Отправить GET-запрос на /orders/track без параметра "):
            response = requests.get(f"{BASE_URL}/orders/track")
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_SEARCH_DATA

    @allure.title("Получение заказа с несуществующим треком")
    def test_get_order_nonexistent_track(self):
        with allure.step(f"Получить заказ по несуществующему треку {NON_EXISTENT_TRACK}"):
            response = get_order_by_track(NON_EXISTENT_TRACK)
        assert response.status_code == 404
        assert response.json()["message"] == ORDER_NOT_FOUND


@allure.feature("Отмена заказа")
class TestCancelOrder:

    @allure.title("Успешная отмена заказа")
    def test_cancel_order_success(self):
        order_payload = get_order_data_base()
        order_response = create_order(order_payload)
        track = order_response.json()["track"]
        with allure.step("Отменить заказ"):
            response = cancel_order(track)
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        # заказ уже отменён, очистка не требуется

    @allure.title("Отмена заказа без трека")
    def test_cancel_order_without_track(self):
        with allure.step("Отправить PUT-запрос на /orders/cancel без параметра track"):
            response = requests.put(f"{BASE_URL}/orders/cancel")
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_SEARCH_DATA

    @allure.title("Отмена несуществующего заказа")
    def test_cancel_nonexistent_order(self):
        with allure.step(f"Отменить заказ с несуществующим треком {NON_EXISTENT_TRACK}"):
            response = cancel_order(NON_EXISTENT_TRACK)
        assert response.status_code == 404
        assert response.json()["message"] == ORDER_NOT_FOUND
