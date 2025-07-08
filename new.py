import requests
import threading
import time
import json
import tkinter as tk
from tkinter import messagebox
from twilio.rest import Client

# Twilio credentials
ACCOUNT_ID = "AC31f959907fcb5f60c1cfdjknsdjkd02ba302d4a2f"
AUTH_TOKEN = "8a4603db3ec9a2cd1jksdfnsdbdde91692db90f1"
TWILIO_NUMBER = "+1517955345342271"
TO_MOBILE_NUMBER = "+919191919929929"

# Twilio Client
client = Client(ACCOUNT_ID, AUTH_TOKEN)

# ESP Server IP
ESP_SERVER_IP = "192.168.105.249"

# Tracking UID and time
last_uid = None
last_uid_timestamp = 0
lock = threading.Lock()  # Ensure thread safety

# GUI Components
running = False  # Controls the fetch loop
response_amount = 10  # Default response amount


def send_json_to_esp(response_value):
    """Send a response value to the ESP8266 via HTTP GET request."""
    url = f"http://{ESP_SERVER_IP}/1010?response={response_value}"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        try:
            log_message(f"ESP8266 Response: {response.json()}")
        except json.JSONDecodeError:
            log_message(f"ESP8266 returned non-JSON response: {response.text}")

    except requests.exceptions.RequestException as e:
        log_message(f"Request failed: {e}")


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

            if uid and espid:
                current_time = time.time()

                with lock:
                    # If it's a new UID or 30 seconds have passed since the last UID, process it
                    if uid != last_uid or (current_time - last_uid_timestamp >= 30):
                        last_uid = uid
                        last_uid_timestamp = current_time
                        log_message(f"Processing UID: {uid}, ESP ID: {espid}")
                        threading.Thread(target=send_json_to_esp, args=(response_amount,)).start()
                    else:
                        log_message(f"UID {uid} ignored (same as last and within 30 seconds)")

                update_labels(uid, espid)

        except json.JSONDecodeError:
            log_message(f"Invalid JSON response: {response.text}")

    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching posts: {e}")
        
def call4():
    """Send a GET request to /call and make a Twilio call if the flag is true."""
    url = f"http://{ESP_SERVER_IP}/call"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # Raise an error for bad responses

        try:
            data = response.json()
            print(f"Response from /call: {data}")

            # Check if the flag is true in the JSON response
            if data.get("flag") is True:
                print("Flag is true, making a Twilio call...")
                make_twilio_call()
            else:
                print("Flag is false, not making a call.")

        except json.JSONDecodeError:
            print(f"Non-JSON response from /call: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error calling /call: {e}")


def make_twilio_call():
    """Make a call using Twilio API to the specified mobile number."""
    try:
        call = client.calls.create(
            to=TO_MOBILE_NUMBER,
            from_=TWILIO_NUMBER,
            twiml="<Response><Say>Hello, your Location is IIIT Delhi</Say></Response>"
        )
        print(f"Call initiated successfully. Call SID: {call.sid}")

    except Exception as e:
        print(f"Error making the call: {e}")


# Call the function


def fetch_loop():
    """Continuously fetch data if running is True."""
    while running:
        get_posts()
        time.sleep(1)  # Prevent overwhelming the ESP server
        call4()



def start_fetching():
    """Start fetching data in a separate thread."""
    global running
    if not running:
        running = True
        threading.Thread(target=fetch_loop, daemon=True).start()
        log_message("Started fetching data...")


def stop_fetching():
    """Stop fetching data."""
    global running
    running = False
    
    log_message("Stopped fetching data.")


def send_manual_response():
    """Send manually entered response value to ESP."""
    global response_amount
    try:
        response_amount = int(response_entry.get())
        send_json_to_esp(response_amount)
        log_message(f"Sent manual response: {response_amount}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number")


def log_message(message):
    """Log messages in the GUI."""
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)


def update_labels(uid, espid):
    """Update UID and ESP ID labels in the GUI."""
    uid_label.config(text=f"UID: {uid}")
    espid_label.config(text=f"ESP ID: {espid}")


# ---------- GUI Setup ----------
root = tk.Tk()
root.title("ESP8266 RFID Manager")
root.geometry("500x400")

# UID & ESP ID Labels
uid_label = tk.Label(root, text="UID: -", font=("Arial", 12))
uid_label.pack(pady=5)

espid_label = tk.Label(root, text="ESP ID: -", font=("Arial", 12))
espid_label.pack(pady=5)

# Manual Response Entry
tk.Label(root, text="Set Response Amount:", font=("Arial", 10)).pack()
response_entry = tk.Entry(root)
response_entry.pack(pady=5)
response_entry.insert(0, str(response_amount))  # Default value

send_button = tk.Button(root, text="Send Response", command=send_manual_response)
send_button.pack(pady=5)

# Start/Stop Buttons
start_button = tk.Button(root, text="Start Fetching", command=start_fetching, bg="green", fg="white")
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Fetching", command=stop_fetching, bg="red", fg="white")
stop_button.pack(pady=5)

# Log Display
log_text = tk.Text(root, height=10, width=60)
log_text.pack(pady=5)

# Run the GUI
root.mainloop()
