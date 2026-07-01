import discord

from discord.ext import commands

from .config import *

from .database import RoomDatabase

from .utils import (
    is_room_empty,
    first_member,
)


class TempVoiceManager(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.db = RoomDatabase()

    # ==================================================
    # TWORZENIE POKOJU
    # ==================================================

    async def create_room(
        self,
        member: discord.Member
    ):

        category = member.guild.get_channel(
            CATEGORY_ID
        )

        channel = await member.guild.create_voice_channel(
            name=f"{CHANNEL_PREFIX} {member.display_name}",
            category=category,
            user_limit=DEFAULT_USER_LIMIT
        )

        await member.move_to(channel)

        self.db.create_room(
            channel.id,
            member.id
        )

        return channel

    # ==================================================
    # USUWANIE POKOJU
    # ==================================================

    async def delete_room(
        self,
        channel: discord.VoiceChannel
    ):

        if not self.db.exists(channel.id):
            return

        self.db.delete_room(channel.id)

        await channel.delete()

    # ==================================================
    # ZMIANA OWNERA
    # ==================================================

    async def transfer_owner(
        self,
        channel: discord.VoiceChannel
    ):

        if not self.db.exists(channel.id):
            return

        if is_room_empty(channel):

            await self.delete_room(channel)

            return

        new_owner = first_member(channel)

        if new_owner is None:
            return

        self.db.set_owner(
            channel.id,
            new_owner.id
        )

        try:

            await new_owner.send(
                f"👑 Jesteś teraz właścicielem kanału **{channel.name}**."
            )

        except Exception:
            pass

    # ==================================================
    # VOICE UPDATE
    # ==================================================

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):

        if before.channel == after.channel:
            return

        # ==========================
        # Tworzenie kanału
        # ==========================

        if after.channel:

            if after.channel.id == CREATE_CHANNEL_ID:

                await self.create_room(
                    member
                )

        # ==========================
        # Opuszczenie kanału
        # ==========================

        if before.channel is None:
            return

        if not self.db.exists(before.channel.id):
            return

        # Kanał pusty -> usuń

        if is_room_empty(before.channel):

            await self.delete_room(
                before.channel
            )

            return

        # Owner opuścił kanał

        owner = self.db.get_owner(
            before.channel.id
        )

        if owner == member.id:

            await self.transfer_owner(
                before.channel
            )

        # ==========================
        # Sprawdzenie bana
        # ==========================

        if after.channel:

            if self.db.exists(after.channel.id):

                banned = self.db.get_banned(
                    after.channel.id
                )

                if member.id in banned:

                    try:

                        await member.move_to(None)

                        await member.send(
                            f"🚫 Jesteś zbanowany z pokoju **{after.channel.name}**."
                        )

                    except Exception:
                        pass
