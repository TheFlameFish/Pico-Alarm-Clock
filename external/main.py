from gpiozero import Button
import requests
from signal import pause
from dotenv import load_dotenv
import os

load_dotenv()

hostname = os.getenv("PICO_ALARM_HOST")

button = Button(18)

url = f"http://{hostname}/api/stop-alarm"

def send_request():
    print("Sending request!")
    requests.post(url)

button.when_activated = send_request

pause()
