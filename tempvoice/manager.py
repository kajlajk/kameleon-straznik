from .views import TempVoiceView

import discord
from discord.ext import commands

from .config import *
from .database import RoomDatabase
from .utils import (
    is_room_empty,
    get_next_owner,
    create_panel_embed,
)


class TempVoiceManager(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.db = RoomDatabase()

    # ==========================================
    # TWORZENIE POKOJU
    # ==========================================

    async def create_room(
        self,
        member: discord.Member
    ):

        category = member.guild.get_channel(
            CATEGORY_ID
        )

        if category is None:
            return

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

        await self.send_panel(channel)

        return channel

    # ==========================================
    # USUWANIE
    # ==========================================

    async def delete_room(
        self,
        channel
    ):

        if not self.db.exists(channel.id):
            return

        self.db.delete_room(
            channel.id
        )

        await channel.delete()

    # ==========================================
    # ZMIANA OWNERA
    # ==========================================

    async def transfer_owner(
        self,
        channel
    ):

        if not self.db.exists(channel.id):
            return

        owner = get_next_owner(channel)

        if owner is None:

            await self.delete_room(channel)

            return

        self.db.set_owner(
            channel.id,
            owner.id
        )

        try:

            await owner.send(
                OWNER_CHANGED
            )

        except Exception:
            pass

    # ==========================================
    # PANEL
    # ==========================================

    async def send_panel(self, channel):

        panel_channel = self.bot.get_channel(PANEL_CHANNEL_ID)

        if panel_channel is None:
            return

        embed = create_panel_embed(
            self.db,
            channel
        )

    
        message = await panel_channel.send(
            embed=embed,
            view=TempVoiceView(
                self,
                channel
            )
        )

        self.db.set_panel_message(
            channel.id,
            message.id
        )


    async def update_panel(self, channel):

        panel_channel = self.bot.get_channel(PANEL_CHANNEL_ID)

        if panel_channel is None:
            return

        message_id = self.db.get_panel_message(
            channel.id
        )

        if message_id is None:
            return

        try:

            message = await panel_channel.fetch_message(
                message_id
            )

        except discord.NotFound:
            return

        except discord.Forbidden:
            return


        embed = create_panel_embed(
            self.db,
            channel
        )

        await message.edit(
            embed=embed,
            view=TempVoiceView(
                self,
                channel
            )
        )
