from microdot.microdot import Microdot, Request, Response
from microdot.utemplate import Template
import asyncio
import sys
import machine

import config

# I hate this word.
alarm_stop_queued = False 

# Note: for some reason it heckin' dies if you try to connect over https, so don't do that.

app = Microdot()
Response.default_content_type = "text/html"

@app.get('/')
async def index(request : Request):
    if config.get("alarm") is not None:
        alarm_hr = str(config._data['alarm'][0])
        if len(alarm_hr) < 2:
            alarm_hr = "0" + alarm_hr

        alarm_min = str(config._data['alarm'][1])
        if len(alarm_min) < 2:
            alarm_min = "0" + alarm_min
        
        alarm_time = f"{alarm_hr}:{alarm_min}"
    else:
        alarm_time = None
    
    if alarm_time is not None and len(alarm_time) < 5:
        alarm_time = "0" + alarm_time # Add leading zero
   
    alarm_set = alarm_time is not None
    hostname = config.get("hostname")
    snooze_minutes = config.get("snooze_minutes")
    snooze_enabled = config.get("snooze_enabled")

    return Template('index.html').render(alarm_time, alarm_set, hostname, snooze_minutes, snooze_enabled)

@app.post('/api/set-alarm')
async def set_alarm(request : Request):
    print(request.form)
    if not request.form:
        return "Invalid request body", 400

    alarm_time = None

    if request.form.get("alarm_enabled", False):
        alarm_time_arr = request.form.get("alarm_time_set", "00:00").split(":") # type: ignore
        alarm_time = [int(alarm_time_arr[0]), int(alarm_time_arr[1])]

    config.set("alarm", alarm_time)
    stat = "Alarm set to " + str(config.get("alarm"))

    config.set("snooze_enabled", request.form.get("snooze_enabled", False))
    stat += f"\nSet snooze_toggle to {config.get('snooze_enabled')}."

    snooze_time = request.form.get("snooze_time_set")
    if snooze_time is not None and float(snooze_time) >= 1:
        config.set("snooze_minutes", int(float(snooze_time)))
        stat += f"\nSet snooze_minutes to {config.get('snooze_minutes')}."


    print(stat)
    return stat

@app.post('/api/set-hostname')
async def set_hostname(request : Request):
    if not request.form:
        return "Invalid request body", 400
    
    if request.form.get("hostname"):
        config.set("hostname", request.form.get("hostname"))

    stat = "Hostname set to " + str(config.get("hostname"))

    print(stat)
    return stat

@app.post('/api/stop-alarm')
async def stop_alarm(request : Request):
    global alarm_stop_queued

    alarm_stop_queued = True

    return "Alarm stop queued"

@app.route('/api/reset', ['GET', 'POST'])
async def reset_route(request : Request):
    asyncio.create_task(reset())
    return "Clock will reset in 5 seconds."

async def reset():
    await asyncio.sleep(5)
    machine.reset()

async def run():
    await app.start_server(host='0.0.0.0', port=80)
