import json
import os


class Config:
    COMIC_VINE_API_KEY = None
    CALIBRE_DB_PATH = None
    UNIQUE_AGENT_ID = None

    def __init__(self, f):
        config = json.load(f)
        self.COMIC_VINE_API_KEY = config.get("COMIC_VINE_API_KEY")
        self.CALIBRE_DB_PATH = config.get("CALIBRE_DB_PATH")
        self.UNIQUE_AGENT_ID = config.get("UNIQUE_AGENT_ID")

config_path = os.path.join(os.path.dirname(__file__), "config.json")
config = Config(open(config_path, "r"))
