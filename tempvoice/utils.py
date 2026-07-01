import discord




# ==================================================
# UPRAWNIENIA
# ==================================================

def is_owner(db, channel_id: int, user_id: int) -> bool:
    owner = db.get_owner(channel_id)

    if owner is None:
        return False

    return owner == user_id


def is_co_owner(db, channel_id: int, user_id: int) -> bool:
    co_owner = db.get_co_owner(channel_id)

    if co_owner is None:
        return False

    return co_owner == user_id


def can_manage(db, channel_id: int, user_id: int) -> bool:
    return (
        is_owner(db, channel_id, user_id)
        or
        is_co_owner(db, channel_id, user_id)
    )


# ==================================================
# KANAŁ
# ==================================================

def is_room_empty(channel: discord.VoiceChannel) -> bool:
    return len(channel.members) == 0


def first_member(channel: discord.VoiceChannel):

    if len(channel.members) == 0:
        return None

    return channel.members[0]


def get_owner_member(
    db,
    guild,
    channel_id
):

    owner = db.get_owner(channel_id)

    if owner is None:
        return None

    return guild.get_member(owner)


# ==================================================
# EMBED
# ==================================================

def create_panel_embed(
    db,
    channel
):

    room = db.get_room(channel.id)

    if room is None:
        return discord.Embed(
            title="❌ Błąd",
            description="Nie znaleziono danych pokoju.",
            color=discord.Color.red()
        )

    owner = get_owner_member(
        db,
        channel.guild,
        channel.id
    )

    embed = discord.Embed(
        title="🦎 TempVoice",
        description="Zarządzaj swoim pokojem za pomocą przycisków poniżej.",
        color=discord.Color.green()
    )

    if owner:

        embed.add_field(
            name="👑 Właściciel",
            value=owner.mention,
            inline=False
        )

    embed.add_field(
        name="🔊 Kanał",
        value=channel.name,
        inline=False
    )

    limit = channel.user_limit

    if limit == 0:
        limit = "∞"

    embed.add_field(
        name="👥 Osoby",
        value=f"{len(channel.members)} / {limit}",
        inline=False
    )

    status = []

    if room["private"]:
        status.append("🔐 Prywatny")
    else:
        status.append("🌐 Publiczny")

    if room["locked"]:
        status.append("🔒 Zablokowany")
    else:
        status.append("🔓 Otwarty")

    embed.add_field(
        name="Status",
        value="\n".join(status),
        inline=False
    )

    if room["description"]:

        embed.add_field(
            name="📝 Opis",
            value=room["description"],
            inline=False
        )

    embed.set_footer(
        text="TempVoice • Meccha Chameleon Polska"
    )

    return embed


# ==================================================
# ODŚWIEŻANIE PANELU
# ==================================================

async def refresh_panel(
    db,
    message,
    channel,
    view
):

    embed = create_panel_embed(
        db,
        channel
    )

    await message.edit(
        embed=embed,
        view=view
    )
