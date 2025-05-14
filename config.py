import tomllib

CONFIG_FILE = "config.toml"

def load_config():
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)

config = load_config()

class Config:
    TOKEN = config["bot"]["token"]
    DEBUG = config["bot"]["debug"]
    CHANNELS = list(config["channels"].values())

    POLL_QUESTION = config["poll"]["question"]
    POLL_OPTIONS = config["poll"]["options"]

    HOUR = config["schedule"]["hour"]
    MINUTE = config["schedule"]["minute"]
    DB_FILE = "poll_results.db"
