import json
import os

DATABASE_FILE = "tempvoice_data.json"


class RoomDatabase:

    def __init__(self):
        self.data = self.load()

    # ==================================================
    # PLIK
    # ==================================================

    def load(self):

        if not os.path.exists(DATABASE_FILE):
            return {}

        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)

        except Exception:
            return {}

    def save(self):

        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ==================================================
    # POKOJE
    # ==================================================

    def exists(self, channel_id: int):

        return str(channel_id) in self.data

    def get_room(self, channel_id: int):

        return self.data.get(str(channel_id))

    def create_room(
        self,
        channel_id: int,
        owner_id: int
    ):

        self.data[str(channel_id)] = {

            "owner": owner_id,

            "co_owner": None,

            "description": "",

            "locked": False,

            "private": False,

            "limit": 0,

            "banned": [],

            "panel_channel": None,

            "panel_message": None

        }

        self.save()

    def delete_room(
        self,
        channel_id: int
    ):

        self.data.pop(
            str(channel_id),
            None
        )

        self.save()

    # ==================================================
    # OWNER
    # ==================================================

    def get_owner(self, channel_id: int):

        room = self.get_room(channel_id)

        if room is None:
            return None

        return room["owner"]

    def set_owner(
        self,
        channel_id: int,
        owner_id: int
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["owner"] = owner_id

        self.save()

    # ==================================================
    # CO OWNER
    # ==================================================

    def get_co_owner(self, channel_id: int):

        room = self.get_room(channel_id)

        if room is None:
            return None

        return room["co_owner"]

    def set_co_owner(
        self,
        channel_id: int,
        user_id: int
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["co_owner"] = user_id

        self.save()

    def remove_co_owner(
        self,
        channel_id: int
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["co_owner"] = None

        self.save()

    # ==================================================
    # OPIS
    # ==================================================

    def get_description(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return ""

        return room["description"]

    def set_description(
        self,
        channel_id: int,
        description: str
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["description"] = description

        self.save()

    # ==================================================
    # LIMIT
    # ==================================================

    def get_limit(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return 0

        return room["limit"]

    def set_limit(
        self,
        channel_id: int,
        limit: int
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["limit"] = limit

        self.save()

    # ==================================================
    # LOCK
    # ==================================================

    def is_locked(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return False

        return room["locked"]

    def set_locked(
        self,
        channel_id: int,
        value: bool
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["locked"] = value

        self.save()

    # ==================================================
    # PRIVATE
    # ==================================================

    def is_private(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return False

        return room["private"]

    def set_private(
        self,
        channel_id: int,
        value: bool
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["private"] = value

        self.save()

    # ==================================================
    # BANY
    # ==================================================

    def get_banned(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return []

        return room["banned"]

    def add_ban(
        self,
        channel_id: int,
        user_id: int
    ):

        if not self.exists(channel_id):
            return

        banned = self.data[str(channel_id)]["banned"]

        if user_id not in banned:
            banned.append(user_id)

        self.save()

    def remove_ban(
        self,
        channel_id: int,
        user_id: int
    ):

        if not self.exists(channel_id):
            return

        banned = self.data[str(channel_id)]["banned"]

        if user_id in banned:
            banned.remove(user_id)

        self.save()

    # ==================================================
    # PANEL
    # ==================================================

    def get_panel_channel(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return None

        return room["panel_channel"]

    def set_panel_channel(
        self,
        channel_id: int,
        value: int
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["panel_channel"] = value

        self.save()

    def get_panel_message(
        self,
        channel_id: int
    ):

        room = self.get_room(channel_id)

        if room is None:
            return None

        return room["panel_message"]

    def set_panel_message(
        self,
        channel_id: int,
        message_id: int
    ):

        if not self.exists(channel_id):
            return

        self.data[str(channel_id)]["panel_message"] = message_id

        self.save()
