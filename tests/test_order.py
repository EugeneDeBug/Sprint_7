import allure
import pytest
import requests
from helpers import (
    create_order, get_orders, get_order_data_black, get_order_data_grey,
    get_order_data_both_colors, get_order_data_no_color, get_order_data_missing_firstname,
    cancel_order, BASE_URL, NON_EXISTENT_COURIER_ID
)

@allure.feature("Заказы")
class TestCreateOrder:    

    @allure.title("Создание заказа с разными цветами")
    @pytest.mark.parametrize("color_func", [
        get_order_data_black,
        get_order_data_grey,
        get_order_data_both_colors,
        get_order_data_no_color
    ])
    def test_create_order_with_colors(self, color_func):        
        payload = color_func()
        response = create_order(payload)
        assert response.status_code == 201
        assert "track" in response.json()        
        track = response.json()["track"]
        cancel_order(track)

    @allure.title("Создание заказа без обязательного поля firstName")
    def test_create_order_missing_firstname(self):        
        payload = get_order_data_missing_firstname()
        response = create_order(payload)
        #  заказ создаётся даже без firstName
        assert response.status_code == 201
        assert "track" in response.json()        
        track = response.json()["track"]
        cancel_order(track)


@allure.feature("Заказы")
class TestListOrders:    

    @allure.title("Получение списка заказов без параметров")
    def test_get_orders_without_params(self):        
        response = get_orders()
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert isinstance(data["orders"], list)

    @allure.title("Получение заказов по courierId (курьер без заказов)")
    def test_get_orders_with_courier_id(self, existing_courier):       
        _, courier_id = existing_courier
        response = get_orders(params={"courierId": courier_id})
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert len(data["orders"]) == 0

    @allure.title("Получение заказов с несуществующим courierId")
    def test_get_orders_with_nonexistent_courier(self):       
        response = get_orders(params={"courierId": NON_EXISTENT_COURIER_ID})
        assert response.status_code == 404
        assert "не найден" in response.json()["message"]
