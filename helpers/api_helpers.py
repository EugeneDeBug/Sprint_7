import requests
from faker import Faker
from config import BASE_URL

fake = Faker(locale='ru_RU')

# несуществующие ID
NON_EXISTENT_COURIER_ID = 999999
NON_EXISTENT_ORDER_ID = 999999
NON_EXISTENT_TRACK = 999999999

# генераторы данных для курьера
def get_courier_data_valid():
    return {
        "login": fake.user_name() + str(fake.random_int(min=100, max=999)),
        "password": fake.password(length=10),
        "firstName": fake.first_name()
    }

def get_courier_data_no_login():
    return {
        "password": fake.password(length=10),
        "firstName": fake.first_name()
    }

def get_courier_data_no_password():
    return {
        "login": fake.user_name() + str(fake.random_int(min=100, max=999)),
        "firstName": fake.first_name()
    }

def get_login_data_valid(login, password):
    return {"login": login, "password": password}

def get_login_data_no_login():
    return {"password": fake.password(length=10)}

def get_login_data_no_password():
    return {"login": fake.user_name(), "password":""}

def get_login_data_wrong_password(login):
    return {"login": login, "password": "wrongpassword"}

def get_login_data_wrong_login():
    return {"login": "nonexistent_user", "password": fake.password(length=10)}

# генераторы данных для заказа
def get_order_data_base():
    return {
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "address": fake.street_address(),
        "metroStation": fake.random_int(min=1, max=200),
        "phone": fake.phone_number(),
        "rentTime": fake.random_int(min=1, max=7),
        "deliveryDate": fake.date_between(start_date='+1d', end_date='+30d').isoformat(),
        "comment": fake.text(max_nb_chars=100),
        "color": ["BLACK"]
    }

def get_order_data_black():
    data = get_order_data_base()
    data["color"] = ["BLACK"]
    return data

def get_order_data_grey():
    data = get_order_data_base()
    data["color"] = ["GREY"]
    return data

def get_order_data_both_colors():
    data = get_order_data_base()
    data["color"] = ["BLACK", "GREY"]
    return data

def get_order_data_no_color():
    data = get_order_data_base()
    data.pop("color", None)
    return data

def get_order_data_missing_firstname():
    data = get_order_data_base()
    data.pop("firstName", None)
    return data

# отправка запросов 
def create_courier(payload):
    return requests.post(f"{BASE_URL}/courier", json=payload)

def login_courier(payload):
    return requests.post(f"{BASE_URL}/courier/login", json=payload)

def delete_courier(courier_id):
    return requests.delete(f"{BASE_URL}/courier/{courier_id}")

def create_order(payload):
    return requests.post(f"{BASE_URL}/orders", json=payload)

def get_orders(params=None):
    return requests.get(f"{BASE_URL}/orders", params=params)

def get_order_by_track(track):
    return requests.get(f"{BASE_URL}/orders/track", params={"t": track})

def cancel_order(track):
    return requests.put(f"{BASE_URL}/orders/cancel", params={"track": track})

def accept_order(order_id, courier_id):
    return requests.put(f"{BASE_URL}/orders/accept/{order_id}", params={"courierId": courier_id})
