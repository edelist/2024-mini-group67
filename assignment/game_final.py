from machine import Pin
import time
import random
import json
import urequests
import network

# Wi-Fi credentials
SSID = "Wads7"
PASSWORD = "Trevelock#69"

# Firebase configuration
FIREBASE_API_KEY = "AIzaSyBGQm_2LYd0AYTzQ0B3ckG10HeYgFNR50c"
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/ec463-exercise03/databases/(default)/documents"

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print('Still connecting to Wi-Fi...')
    print('Network connected:', wlan.ifconfig())

def create_user_with_email_and_password(email: str, password: str):
    """Create a new user with email and password using Firebase REST API."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = urequests.post(url, json=payload)
        response_data = response.json()
        if 'idToken' in response_data and 'localId' in response_data:
            print(f"Successfully created user {email}")
            return response_data['idToken'], response_data['localId']
        else:
            print(f"Failed to create user: {response_data.get('error', {}).get('message')}")
            return None, None
    except Exception as e:
        print(f"User creation failed: {e}")
        return None, None

def sign_in_with_email_and_password(email: str, password: str):
    """Sign in a user with email and password using Firebase REST API."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = urequests.post(url, json=payload)
        response_data = response.json()
        if 'idToken' in response_data and 'localId' in response_data:
            print(f"Successfully signed in as {email}")
            return response_data['idToken'], response_data['localId']
        else:
            print(f"Failed to sign in: {response_data.get('error', {}).get('message')}")
            return None, None
    except Exception as e:
        print(f"Sign-in failed: {e}")
        return None, None

def get_user_input():
    """Collect user email and password."""
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    return email, password

def send_data_to_firebase(uid, id_token, data):
    """Upload data to Firebase Firestore with authentication."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"
    }
    url = f"{FIREBASE_URL}/users/{uid}/response_times"

    formatted_data = {
        "fields": {
            "Minimum response time": {"doubleValue": data.get("Minimum response time", 0.0)},
            "Maximum response time": {"doubleValue": data.get("Maximum response time", 0.0)},
            "Average response time": {"doubleValue": data.get("Average response time", 0.0)},
            "Score": {"doubleValue": data.get("Score", 0.0)},
            "Misses": {"integerValue": data.get("Misses", 0)},
            "Total flashes": {"integerValue": data.get("Total flashes", 0)},
            "Response times": {
                "arrayValue": {
                    "values": [{"integerValue": rt} for rt in data.get("Response times", []) if rt is not None]
                }
            }
        }
    }
    
    try:
        print('Sending data to Firebase...')
        response = urequests.post(url, headers=headers, json=formatted_data)
        response_data = response.json()
        if response_data.get('error'):
            print("Firebase Response Error:", response_data['error'])
        else:
            print("Data sent to Firebase successfully.")
            print("Firebase Response:", response.text)
    except Exception as e:
        print(f"Failed to send data to Firebase. Error: {e}")

N = 3  # Number of trials
sample_ms = 10.0
on_ms = 500

def random_time_interval(tmin: float, tmax: float) -> float:
    """Return a random time interval between tmin and tmax."""
    return random.uniform(tmin, tmax)

def blinker(N: int, led: Pin) -> None:
    """Blink the LED N times to signal the start or end."""
    print(f'Blinking LED {N} times.')
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)
    print('Blinking completed.')

def scorer(t: list[int | None], id_token: str, uid: str) -> None:
    """Calculate statistics and upload the response times."""
    print('Calculating results...')
    # Calculate the number of misses
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]

    # Calculate minimum, maximum, average response time and score
    if t_good: 
        min_time = min(t_good)
        max_time = max(t_good)
        avg_time = sum(t_good) / len(t_good)
    else: 
        min_time, max_time, avg_time = None, None, None
    
    score = len(t_good) / len(t)

    # Prepare the data to be uploaded
    data = {
        "Minimum response time": min_time,
        "Maximum response time": max_time, 
        "Average response time": avg_time,
        "Score": score,
        "Misses": misses,
        "Total flashes": len(t),
        "Response times": t
    }

    print('Data ready for upload:')
    print(data)

    # Upload the data to Firebase
    send_data_to_firebase(uid, id_token, data)

if __name__ == "__main__":
    print('Starting the Reaction Time Game...')
    led = Pin("LED", Pin.OUT)  # Use built-in LED
    button = Pin(16, Pin.IN, Pin.PULL_UP)  # Button on GPIO 16

    t = []  # Store reaction times

    print('Connecting to Wi-Fi...')
    connect_to_wifi()  # Connect to Wi-Fi

    print('Signing in or creating a new user...')
    email, password = get_user_input()

    id_token, uid = sign_in_with_email_and_password(email, password)

    if not id_token or not uid:
        print('User not found or sign-in failed, trying to create a new user...')
        id_token, uid = create_user_with_email_and_password(email, password)

    if id_token and uid:
        print('Starting game...')
        blinker(3, led)  # Blink to signal the game start

        for i in range(N):
            print(f'Trial {i + 1}/{N}...')
            time.sleep(random_time_interval(0.5, 5.0))

            led.high()
            tic = time.ticks_ms()
            t0 = None
            while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
                if button.value() == 0:  # Button pressed
                    t0 = time.ticks_diff(time.ticks_ms(), tic)
                    led.low()
                    break
            if t0 is not None:
                print(f'Reaction time: {t0} ms')
            else:
                print('No reaction detected.')

            t.append(t0)  # Store reaction time (None if missed)

            led.low()

        print('Game over.')
        blinker(5, led)  # Blink to signal the game end

        scorer(t, id_token, uid)  # Calculate and upload results
    else:
        print("Failed to authenticate or create user.")
