import discord

from .config import (
    PANEL_TITLE,
    PANEL_DESCRIPTION,
    PANEL_COLOR,
    PANEL_FOOTER
)


# ==================================================
# KANAŁ
# ==================================================

def is_room_empty(channel: discord.VoiceChannel) -> bool:
    return len(channel.members) == 0


def get_next_owner(channel: discord.VoiceChannel):

    if len(channel.members) == 0:
        return None

    return channel.members[0]


# ==================================================
# EMBED
# ==================================================

def create_panel_embed(db, channel: discord.VoiceChannel):

    room = db.get_room(channel.id)

    embed = discord.Embed(
        title=PANEL_TITLE,
        description=PANEL_DESCRIPTION,
        color=PANEL_COLOR
    )

    owner = None

    if room:
        owner = channel.guild.get_member(room["owner"])

    embed.add_field(
        name="👑 Właściciel",
        value=owner.mention if owner else "Brak",
        inline=False
    )

    embed.add_field(
        name="🔊 Kanał",
        value=channel.name,
        inline=False
    )

    limit = channel.user_limit if channel.user_limit else "∞"

    embed.add_field(
        name="👥 Użytkownicy",
        value=f"{len(channel.members)} / {limit}",
        inline=False
    )

    if room:

        description = room["description"]

        if description:

            embed.add_field(
                name="📝 Opis",
                value=description,
                inline=False
            )

    embed.set_footer(
        text=PANEL_FOOTER
    )

    return embed


# ==================================================
# UPRAWNIENIA
# ==================================================

def is_owner(db, channel_id: int, user_id: int):

    owner = db.get_owner(channel_id)

    return owner == user_id


# ==================================================
# ODŚWIEŻANIE PANELU
# ==================================================

async def refresh_panel(message, db, channel, view):

    embed = create_panel_embed(
        db,
        channel
    )

    await message.edit(
        embed=embed,
        view=view
    )
