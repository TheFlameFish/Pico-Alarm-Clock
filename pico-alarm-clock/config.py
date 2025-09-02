import json
import asyncio

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "alarm": None,
    "hostname": "picoalarm",
    "snooze_minutes": 2,
    "snooze_enabled": True,
    "alarm_scream_duration": 5 * 60,
}

_data = {}

def read_config():
    global _data
    try:
        with open(CONFIG_PATH, "r") as f:
            _data : dict = json.load(f)

        for key in DEFAULT_CONFIG.keys():
            if not key in _data.keys():
                _data[key] = DEFAULT_CONFIG[key]
                print(f"Config previously missing {key}. Added as default.")
    except Exception as e:
        print("WARN: Failed to open config.\n", e)
        _data = DEFAULT_CONFIG

    write_config()
    
def write_config():
    with open(CONFIG_PATH, "w") as f:
        f.write(json.dumps(_data))

def get(key, default = None):
    return _data.get(key, default)

def set(key, value):
    if key not in _data.keys():
        raise ValueError(f"Invalid config key: {key}")
    
    _data[key] = value
    write_config()

read_config()
print(_data)
