import json
import os

FILE_NAME = "tempvoice_data.json"


def load_data():
    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
