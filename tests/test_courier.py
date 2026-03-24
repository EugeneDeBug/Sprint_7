import allure
import pytest
from helpers import (
    create_courier, login_courier, delete_courier,
    get_courier_data_valid, get_courier_data_no_login, get_courier_data_no_password,
    get_login_data_valid, get_login_data_no_login, get_login_data_no_password,
    get_login_data_wrong_password, get_login_data_wrong_login,
    NON_EXISTENT_COURIER_ID
)
from data.messages import (
    LOGIN_ALREADY_USED, INSUFFICIENT_DATA, INSUFFICIENT_LOGIN_DATA,
    ACCOUNT_NOT_FOUND, COURIER_NOT_FOUND
)

@allure.feature("Создание курьера")
class TestCreateCourier:

    @allure.title("Создание курьера с валидными данными")
    def test_create_courier_success(self, new_courier):
        payload, response = new_courier
        assert response.status_code == 201
        assert response.json() == {"ok": True}

    @allure.title("Создание курьера с повторяющимся логином")
    def test_create_courier_duplicate_login(self, new_courier):
        payload, _ = new_courier
        duplicate_payload = {
            "login": payload["login"],
            "password": "another",
            "firstName": "Another"
        }
        with allure.step("Попытаться создать второго курьера с тем же логином"):
            response = create_courier(duplicate_payload)
        assert response.status_code == 409
        assert response.json()["message"] == LOGIN_ALREADY_USED

    @allure.title("Создание курьера без поля login")
    def test_create_courier_missing_login(self):
        payload = get_courier_data_no_login()
        with allure.step("Отправить запрос без поля login"):
            response = create_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_DATA

    @allure.title("Создание курьера без поля password")
    def test_create_courier_missing_password(self):
        payload = get_courier_data_no_password()
        with allure.step("Отправить запрос без поля password"):
            response = create_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_DATA


@allure.feature("Логин курьера")
class TestLoginCourier:

    @allure.title("Успешный логин курьера")
    def test_login_success(self, new_courier):
        payload, _ = new_courier
        login = payload["login"]
        password = payload["password"]
        payload_login = get_login_data_valid(login, password)
        with allure.step("Выполнить логин"):
            response = login_courier(payload_login)
        assert response.status_code == 200
        assert "id" in response.json()

    @allure.title("Логин с неверным паролем")
    def test_login_wrong_password(self, new_courier):
        payload, _ = new_courier
        login = payload["login"]
        payload_login = get_login_data_wrong_password(login)
        with allure.step("Выполнить логин с неверным паролем"):
            response = login_courier(payload_login)
        assert response.status_code == 404
        assert response.json()["message"] == ACCOUNT_NOT_FOUND

    @allure.title("Логин с несуществующим логином")
    def test_login_wrong_login(self):
        payload = get_login_data_wrong_login()
        with allure.step("Выполнить логин с несуществующим логином"):
            response = login_courier(payload)
        assert response.status_code == 404
        assert response.json()["message"] == ACCOUNT_NOT_FOUND

    @allure.title("Логин без поля login")
    def test_login_missing_login(self):
        payload = get_login_data_no_login()
        with allure.step("Выполнить логин без поля login"):
            response = login_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_LOGIN_DATA

    @allure.title("Логин без поля password")
    def test_login_missing_password(self):
        payload = get_login_data_no_password()
        with allure.step("Выполнить логин без поля password"):
            response = login_courier(payload)
        assert response.status_code == 400
        assert response.json()["message"] == INSUFFICIENT_LOGIN_DATA


@allure.feature("Удаление курьера")
class TestDeleteCourier:

    @allure.title("Успешное удаление курьера (код ответа)")
    def test_delete_courier_returns_ok(self, new_courier):
        payload, _ = new_courier
        login_resp = login_courier({"login": payload["login"], "password": payload["password"]})
        courier_id = login_resp.json()["id"]
        with allure.step("Удалить курьера"):
            response = delete_courier(courier_id)
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    @allure.title("После удаления курьер не может авторизоваться")
    def test_deleted_courier_cannot_login(self, new_courier):
        payload, _ = new_courier
        login_resp = login_courier({"login": payload["login"], "password": payload["password"]})
        courier_id = login_resp.json()["id"]
        with allure.step("Удалить курьера"):
            delete_courier(courier_id)
        with allure.step("Попытаться залогиниться после удаления"):
            second_login = login_courier({"login": payload["login"], "password": payload["password"]})
        assert second_login.status_code == 404

    @allure.title("Удаление несуществующего курьера")
    def test_delete_nonexistent_courier(self):
        with allure.step("Удалить несуществующего курьера"):
            response = delete_courier(NON_EXISTENT_COURIER_ID)
        assert response.status_code == 404
        assert response.json()["message"] == COURIER_NOT_FOUND

    @allure.title("Удаление курьера без id")
    def test_delete_courier_without_id(self):
        with allure.step("Удалить курьера без id (пустой id в URL)"):
            response = delete_courier("")
        assert response.status_code == 404
