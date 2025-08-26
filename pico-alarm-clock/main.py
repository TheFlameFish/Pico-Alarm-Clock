import utime
from machine import SoftI2C, Pin, RTC, PWM
import network
import urequests
import asyncio

from lib.lcd_api import LcdApi
from lib.pico_i2c_lcd import I2cLcd

import env
import webserver
import config

print("Hai wurld :3")

rtc = RTC()

# LCD Setup
LCD_ADDR = 0x27
LCD_ROWS = 2
LCD_COLS = 16
lcd_i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=400000) # For some reason it dies if I try to use normal I2C :p
lcd = I2cLcd(lcd_i2c, LCD_ADDR, LCD_ROWS, LCD_COLS)

# Buzzer setup
ALARM_BUZZ_FREQ = 900
BUZZER_DUTY_CYCLE = int(65536*0.2)

buzzer = PWM(Pin(16))

# Button setup
button = Pin(22, Pin.IN, Pin.PULL_UP)
alarm_screaming = False

def connect_wifi():
    hostname = "placeholderalarm" # TODO This'll be smth you can adjust in config
    network.hostname(hostname)

    wlan = network.WLAN(network.STA_IF)
    wlan.config(hostname=hostname)
    wlan.active(True)
    wlan.connect(env.wifi[0], env.wifi[1])

    print("Connecting to Wifi...")
    while not wlan.isconnected():
        utime.sleep(1)
        print("...")

    print("Connected: ", wlan.ifconfig())

def sync_time_api(rtc: RTC):
    url = f'http://api.ipgeolocation.io/timezone?apiKey={env.geolocation_key}&tz={env.time_zone}'
    response = urequests.get(url)
    data : dict = response.json()

    print("Geolocation API response:", data)

    if "date_time" in data:
        current_time : str = data["date_time"]
        print("Current Time:", current_time)

        if " " in current_time:
            date, time = current_time.split(" ")
            year, month, day = map(int, date.split("-"))
            hours, minutes, seconds = map(int, time.split(":"))

            week_day = data.get("day_of_week", 0) # Defaults to 0
            rtc.datetime((year, month, day, week_day, hours, minutes, seconds, 0)) # Ig it'll be a teensy bit off because the API doesn't give ms
            print("RTC time after setting:", rtc.datetime()) # Both a getter and a setter
        else:
            print("Error getting time: Unexpected time format:", current_time)
    else:
        print("Error: Response does not contain required data:", data)

async def update_display(rtc : RTC):
    lcd.backlight_on()
    previous_time_str = ""
    pervious_date_str = ""

    while True:
        current_time = rtc.datetime()
        # Scary string formatting!
        time_str = f"{current_time[4]:02}:{current_time[5]:02}:{current_time[6]:02}"  # HH:MM:SS
        date_str = f"{current_time[2]:02}/{current_time[1]:02}/{current_time[0]}"  # DD/MM/YYYY

        # Don't refresh unnesecarily
        if time_str != previous_time_str:
            lcd.move_to(0, 0)
            lcd.putstr(time_str)

        if date_str != pervious_date_str:
            lcd.move_to(0, 1)
            lcd.putstr(date_str)

        previous_time_str = time_str
        pervious_date_str = date_str

        await asyncio.sleep(1) # It'd be rather silly to refresh this more than once per second (Read: Future me, don't do that.)

async def alarm():
    global alarm_screaming
    while True:
        print("Alarm tick")
        alarm_hr, alarm_min = (None, None)

        if config.data["alarm"] != None:
            alarm_hr, alarm_min = config.data["alarm"][0], config.data["alarm"][1]
        
        time = rtc.datetime()
        if time[4] == alarm_hr and time[5] == alarm_min and time[6] <= 3:
            print("BEEEP")
            alarm_screaming = True
            asyncio.create_task(sound_alarm())

            while button.value() == 1: # While button is unpressed
                await asyncio.sleep(0)

            alarm_screaming = False
            print("Ok i eep now")

        await asyncio.sleep(60 - rtc.datetime()[6] + 1) # Added second to make sure time is past the minute mark

async def sound_alarm():
    print("Alarm go brrrrrrr")
    pattern = (
        ([(0.5,0.5)] * 8) # 8 long beeps
        + (([(0.1,0.1)] * 3 + [(0.1, 0.5)]) * 4) # 32 short beeps in groups of 4
    )
    
    i = 0
    while alarm_screaming:
        if len(pattern) > 1:
            times = pattern[i % (len(pattern)-1)]
        else:
            times = pattern[0]
        buzzer.duty_u16(BUZZER_DUTY_CYCLE)
        buzzer.freq(ALARM_BUZZ_FREQ)
        await asyncio.sleep(times[0])

        buzzer.duty_u16(0)
        await asyncio.sleep(times[1])
        i += 1

async def startup_beep():
    buzzer.duty_u16(BUZZER_DUTY_CYCLE)
    buzzer.freq(ALARM_BUZZ_FREQ)
    await asyncio.sleep(0.1)
    buzzer.duty_u16(0)

async def main():
    connect_wifi()
    sync_time_api(rtc)

    # loop
    asyncio.create_task(update_display(rtc))
    asyncio.create_task(alarm())
    asyncio.create_task(webserver.run_server())
    asyncio.create_task(startup_beep())

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
