import discord

from .database import get_owner


def is_owner(data: dict, channel_id: int, user_id: int) -> bool:
    """
    Sprawdza czy użytkownik jest właścicielem pokoju.
    """
    owner = get_owner(data, channel_id)

    if owner is None:
        return False

    return owner == user_id


def get_room(data: dict, channel_id: int):
    """
    Zwraca dane pokoju lub None.
    """
    return data.get(str(channel_id))


def room_exists(data: dict, channel_id: int) -> bool:
    """
    Sprawdza czy kanał jest pokojem TempVoice.
    """
    return str(channel_id) in data


def get_owner_member(guild: discord.Guild, data: dict, channel_id: int):
    """
    Zwraca obiekt Member właściciela.
    """
    owner = get_owner(data, channel_id)

    if owner is None:
        return None

    return guild.get_member(owner)


def is_room_empty(channel: discord.VoiceChannel) -> bool:
    """
    Czy kanał jest pusty.
    """
    return len(channel.members) == 0


def first_member(channel: discord.VoiceChannel):
    """
    Zwraca pierwszego użytkownika na kanale.
    """
    if len(channel.members) == 0:
        return None

    return channel.members[0]


def can_manage_room(data: dict, channel_id: int, user_id: int) -> bool:
    """
    Sprawdza czy użytkownik może zarządzać pokojem.
    Owner lub współwłaściciel.
    """

    room = get_room(data, channel_id)

    if room is None:
        return False

    if room["owner"] == user_id:
        return True

    co_owner = room.get("co_owner")

    if co_owner == user_id:
        return True

    return False


def create_embed(
    owner: discord.Member,
    channel: discord.VoiceChannel,
    room_data: dict
):
    """
    Tworzy główny panel TempVoice.
    """

    embed = discord.Embed(
        title="🦎 TempVoice",
        description="Zarządzaj swoim pokojem za pomocą przycisków poniżej.",
        color=discord.Color.green()
    )

    embed.add_field(
        name="👑 Owner",
        value=owner.mention,
        inline=False
    )

    embed.add_field(
        name="🔊 Kanał",
        value=channel.name,
        inline=False
    )

    limit = "∞" if channel.user_limit == 0 else channel.user_limit

    embed.add_field(
        name="👥 Osoby",
        value=f"{len(channel.members)} / {limit}",
        inline=False
    )

    status = []

    if room_data.get("private"):
        status.append("🔐 Prywatny")
    else:
        status.append("🌐 Publiczny")

    if room_data.get("locked"):
        status.append("🔒 Zablokowany")
    else:
        status.append("🔓 Otwarty")

    embed.add_field(
        name="Status",
        value="\n".join(status),
        inline=False
    )

    description = room_data.get("description")

    if description:
        embed.add_field(
            name="📝 Opis",
            value=description,
            inline=False
        )

    embed.set_footer(
        text="TempVoice • Meccha Chameleon Polska"
    )

    return embed
