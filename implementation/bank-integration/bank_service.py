import requests
import json

# <secret>
api_key = "Bearer mvxpzjOnI7pFj0sb6MsHM6hMW5taOEcq4zhOzntv"
headers = {"accept": "application/vnd.api+json", "Authorization": api_key}
# </secret>

base_url = "https://finance.lutzen.dk/api/v1"
customers_url = f"{base_url}/customers"
payments_url = f"{base_url}/payments"


def get_customers():
    r = requests.get(customers_url, headers=headers)
    obj = r.json()
    return obj["data"]


def get_customer_payments(customer_id: int):
    r = requests.get(
        customers_url + "/" + str(customer_id) + "/payments", headers=headers
    )
    obj = r.json()
    return obj["data"]


def update_payment(payment_id: int, new_status: str = "", new_amount: int = -1):
    payment = {}
    payment["data"] = {}
    payment["data"]["type"] = "payments"
    payment["data"]["id"] = str(payment_id)
    payment["data"]["attributes"] = {}
    if new_status != "":
        payment["data"]["attributes"]["status"] = new_status
    if new_amount != -1:
        payment["data"]["attributes"]["amount"] = new_amount

    r = requests.patch(
        payments_url + "/" + str(payment_id), data=json.dumps(payment), headers=headers
    )
    return r.json()["data"]

def get_payment(payment_id: int):
    # this is a hack
    return update_payment(payment_id = payment_id)

def get_customer_from_payment(payment_id: int):
    # this is a hack
    payment = update_payment(payment_id)
    customer_url = payment["relationships"]["customer"]["links"]["related"]
    r = requests.get(customer_url, headers=headers)

    return r.json()["data"]["id"]

def get_customer_by_id(customer_id: int):
    # This endpoint is not officially supported
    r = requests.get(
        customers_url + "/" + str(customer_id), headers=headers
    )
    obj = r.json()
    return obj["data"]
