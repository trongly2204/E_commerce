import requests
from requests.auth import HTTPBasicAuth

def payment_check():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    client_id = "CLIENTID" //Replace your Client id and secret on paypal sandbox account
    client_secret = "CLIENTSECRET"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret))
    if response.status_code == 200:
        print("Access token:", response.json()['access_token'])
        return response.json()['access_token']
    else:
        print("Error:", response.status_code, response.text)
        return None


def create_paypal_order(access_token, total_with_shipping):
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "intent": "CAPTURE",  # or "AUTHORIZE"
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": f"{total_with_shipping:.2f}"
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        result = response.json()
        order_id = result["id"]  
        print("Payment ID (Order ID):", order_id)
        return order_id
    else:
        print("Error creating order:", response.status_code, response.text)
        return None
