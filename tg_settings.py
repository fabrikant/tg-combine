import json
from types import SimpleNamespace
import yaml

def load_settings(filename):
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
        return json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))


settings = load_settings("settings.yml")
