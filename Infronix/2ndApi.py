import requests
import threading
import time
import json
from twilio.rest import Client

# Twilio credentials
ACCOUNT_ID = "AC31f959907fcb5f60c1cd02ba302d4a2f"
AUTH_TOKEN = "8a4603db3ec9a2cd1bdde91692db90f1"
TWILIO_NUMBER = "+15179552271"
TO_MOBILE_NUMBER = "+919896830917"

# Twilio Client
client = Client(ACCOUNT_ID, AUTH_TOKEN)

# ESP Server IP
ESP_SERVER_IP = "192.168.26.249"

# Tracking UID and time
last_uid = None
last_uid_timestamp = 0
lock = threading.Lock()  # Ensure thread safety


def send_json_to_esp(response_value):
    """Send a response value to the ESP8266 via HTTP GET request."""
    url = f"http://{ESP_SERVER_IP}/1010?response={response_value}"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        try:
            print("Response from ESP8266:", response.json())
        except json.JSONDecodeError:
            print(f"ESP8266 returned non-JSON response: {response.text}")

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)


def get_posts():
    """Fetch UID and ESP ID from ESP8266 and process new data based on timing conditions."""
    global last_uid, last_uid_timestamp
    url = f"http://{ESP_SERVER_IP}/uid"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()

        try:
            posts = response.json()
            uid = posts.get('uid')
            espid = posts.get('espid')
            balance = requests.get(f"/balance", params={"uid": uid})
            # deductible = requests.get(f"{url}/{espid}?reponse={uid}")
            print(balance)

            if uid and espid:
                current_time = time.time()

                with lock:
                    # If it's a new UID or 30 seconds have passed since the last UID, process it
                    if uid != last_uid or (current_time - last_uid_timestamp >= 30):
                        last_uid = uid
                        last_uid_timestamp = current_time
                        print(f"Processing UID: {uid}, ESP ID: {espid}")
                        threading.Thread(target=send_json_to_esp, args=(10,)).start()
                    else:
                        print(f"UID {uid} ignored (same as last and within 30 seconds)")

        except json.JSONDecodeError:
            print(f"Invalid JSON response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts: {e}")


def main():
    """Main loop to fetch data periodically."""
    while True:
        get_posts()
        time.sleep(1)  # Prevent overwhelming the ESP server


if __name__ == '_main_':
    main()