from microdot.microdot import Microdot, Request, Response
from microdot.utemplate import Template
import asyncio
import sys

import config

# Note: for some reason it heckin' dies if you try to connect over https, so don't do that.

app = Microdot()
Response.default_content_type = "text/html"

@app.get('/')
async def index(request : Request):
    alarm_time = f"{config._data['alarm'][0]}:{config._data['alarm'][1]}" if (config._data["alarm"] is not None) else None
    if alarm_time is not None and len(alarm_time) < 5:
        alarm_time = "0" + alarm_time # Add leading zero
   
    alarm_set = alarm_time is not None

    return Template('index.html').render(alarm_time, alarm_set)

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

    print(stat)
    return stat

async def run():
    await app.start_server(host='0.0.0.0', port=80)
