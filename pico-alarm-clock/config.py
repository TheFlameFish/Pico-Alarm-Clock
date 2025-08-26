import json
import asyncio

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "alarm": None,
}

data = {}

def read_config():
    global data
    try:
        with open(CONFIG_PATH, "r") as f:
            data : dict = json.load(f)

        for key in DEFAULT_CONFIG.keys():
            if not key in data.keys():
                data[key] = DEFAULT_CONFIG[key]
                print(f"Config previously missing {key}. Added as default.")
    except Exception as e:
        print("WARN: Failed to open config.\n", e)
        data = DEFAULT_CONFIG

    write_config()
    
def write_config():
    with open(CONFIG_PATH, "w") as f:
        f.write(json.dumps(data))

read_config()
print(data)
