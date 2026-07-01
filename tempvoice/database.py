import json
import os

FILE_NAME = "tempvoice_data.json"


def load_data():
    if not os.path.exists(FILE_NAME):
        return {}

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def create_room(data, channel_id, owner_id):
    data[str(channel_id)] = {
        "owner": owner_id,
        "co_owner": None,
        "description": "",
        "locked": False,
        "private": False,
        "banned": [],
        "panel_message": None
    }

    save_data(data)


def delete_room(data, channel_id):
    data.pop(str(channel_id), None)
    save_data(data)


def room_exists(data, channel_id):
    return str(channel_id) in data


def get_room(data, channel_id):
    return data.get(str(channel_id))


def get_owner(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return None

    return room["owner"]


def set_owner(data, channel_id, owner_id):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["owner"] = owner_id
    save_data(data)


def get_co_owner(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return None

    return room["co_owner"]


def set_co_owner(data, channel_id, user_id):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["co_owner"] = user_id
    save_data(data)


def remove_co_owner(data, channel_id):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["co_owner"] = None
    save_data(data)


def get_description(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return ""

    return room["description"]


def set_description(data, channel_id, description):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["description"] = description
    save_data(data)


def is_locked(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return False

    return room["locked"]


def set_locked(data, channel_id, value):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["locked"] = value
    save_data(data)


def is_private(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return False

    return room["private"]


def set_private(data, channel_id, value):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["private"] = value
    save_data(data)


def get_banned(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return []

    return room["banned"]


def add_ban(data, channel_id, user_id):
    if not room_exists(data, channel_id):
        return

    banned = data[str(channel_id)]["banned"]

    if user_id not in banned:
        banned.append(user_id)

    save_data(data)


def remove_ban(data, channel_id, user_id):
    if not room_exists(data, channel_id):
        return

    banned = data[str(channel_id)]["banned"]

    if user_id in banned:
        banned.remove(user_id)

    save_data(data)


def set_panel_message(data, channel_id, message_id):
    if not room_exists(data, channel_id):
        return

    data[str(channel_id)]["panel_message"] = message_id
    save_data(data)


def get_panel_message(data, channel_id):
    room = get_room(data, channel_id)

    if room is None:
        return None

    return room["panel_message"]
