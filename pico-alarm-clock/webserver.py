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
    alarm_time = f"{config.data['alarm'][0]}:{config.data['alarm'][1]}" if (config.data["alarm"] is not None) else None
    if alarm_time is not None and len(alarm_time) < 5:
        alarm_time = "0" + alarm_time # Add leading zero
   
    alarm_set = alarm_time is not None

    return Template('index.html').render(alarm_time, alarm_set)

async def run():
    await app.start_server(host='0.0.0.0', port=80)
