import allure
import pytest
from helpers import (
    create_courier, login_courier, delete_courier,
    get_courier_data_valid, get_courier_data_no_login, get_courier_data_no_password,
    get_login_data_valid, get_login_data_no_login, get_login_data_no_password,
    get_login_data_wrong_password, get_login_data_wrong_login,
    NON_EXISTENT_COURIER_ID
)

@allure.feature("Курьер")
class TestCreateCourier:    

    @allure.title("Создание курьера с валидными данными")
    def test_create_courier_success(self):    
        payload = get_courier_data_valid()
        response = create_courier(payload)
        assert response.status_code == 201
        assert response.json() == {"ok": True}
    
        login_resp = login_courier({"login": payload["login"], "password": payload["password"]})
        assert login_resp.status_code == 200
        delete_courier(login_resp.json()["id"])

    @allure.title("Создание курьера с повторяющимся логином")
    def test_create_courier_duplicate_login(self):        
        first_payload = get_courier_data_valid()
        create_courier(first_payload)
        duplicate_payload = {
        "login": first_payload["login"],
        "password": "another",
        "firstName": "Another"
        }
        response = create_courier(duplicate_payload)
        assert response.status_code == 409
        assert response.json()["message"] == "Этот логин уже используется. Попробуйте другой."        
        login_resp = login_courier({"login": first_payload["login"], "password": first_payload["password"]})
        assert login_resp.status_code == 200
        delete_courier(login_resp.json()["id"])

    @allure.title("Создание курьера без поля login")
    def test_create_courier_missing_login(self):        
        payload = get_courier_data_no_login()
        response = create_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для создания учетной записи"

    @allure.title("Создание курьера без поля password")
    def test_create_courier_missing_password(self):        
        payload = get_courier_data_no_password()
        response = create_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для создания учетной записи"


@allure.feature("Курьер")
class TestLoginCourier:    

    @allure.title("Успешный логин курьера")
    def test_login_success(self, new_courier):        
        login = new_courier["login"]
        password = new_courier["password"]
        payload = get_login_data_valid(login, password)
        response = login_courier(payload)
        assert response.status_code == 200
        assert "id" in response.json()

    @allure.title("Логин с неверным паролем")
    def test_login_wrong_password(self, new_courier):        
        login = new_courier["login"]
        payload = get_login_data_wrong_password(login)
        response = login_courier(payload)
        assert response.status_code == 404
        assert response.json()["message"] == "Учетная запись не найдена"

    @allure.title("Логин с несуществующим логином")
    def test_login_wrong_login(self):        
        payload = get_login_data_wrong_login()
        response = login_courier(payload)
        assert response.status_code == 404
        assert response.json()["message"] == "Учетная запись не найдена"

    @allure.title("Логин без поля login")
    def test_login_missing_login(self):        
        payload = get_login_data_no_login()
        response = login_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для входа"

    @allure.title("Логин без поля password")
    def test_login_missing_password(self):        
        payload = get_login_data_no_password()
        response = login_courier(payload)        
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для входа"


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
        
        second_login = login_courier({"login": payload["login"], "password": payload["password"]})
        assert second_login.status_code == 404

    @allure.title("Удаление несуществующего курьера")
    def test_delete_nonexistent_courier(self):
        response = delete_courier(NON_EXISTENT_COURIER_ID)
        assert response.status_code == 404
        assert response.json()["message"] == "Курьера с таким id нет."

    @allure.title("Удаление курьера без id")
    def test_delete_courier_without_id(self):
        response = delete_courier("")
        assert response.status_code == 404
