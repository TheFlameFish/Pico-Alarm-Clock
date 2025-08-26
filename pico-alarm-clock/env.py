import json

env_vars = {}

try:
    with open("env.json", "r") as config:
        env_vars = json.load(config)
except:
    raise Exception("File env.json has not been created! Please create it following the instructions in README.md")

try:
    wifi = (env_vars["ssid"], env_vars["ssid_password"])
    geolocation_key = env_vars["date_time_api"]
    time_zone = env_vars["time_zone"]
except Exception as e:
    raise Exception(f"env.json appears to be misconfigured: {e}")

