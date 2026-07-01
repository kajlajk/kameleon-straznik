print("TEMPVOICE MANAGER ZAŁADOWANY")

import discord
from discord.ext import commands

from .config import *
from .database import RoomDatabase
from .utils import (
    is_room_empty,
    get_next_owner,
    create_panel_embed,
)
from .views import TempVoiceView


class TempVoiceManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = RoomDatabase()
        print("COG START")

    # ==========================================
    # CREATE ROOM
    # ==========================================

    async def create_room(self, member: discord.Member):

        category = member.guild.get_channel(CATEGORY_ID)
        if category is None:
            return

        channel = await member.guild.create_voice_channel(
            name=f"{CHANNEL_PREFIX} {member.display_name}",
            category=category,
            user_limit=DEFAULT_USER_LIMIT
        )

        await member.move_to(channel)

        self.db.create_room(channel.id, member.id)

        await self.send_panel(channel)

        return channel

    # ==========================================
    # DELETE ROOM
    # ==========================================

    async def delete_room(self, channel):

        if not self.db.exists(channel.id):
            return

        self.db.delete_room(channel.id)
        await channel.delete()

    # ==========================================
    # TRANSFER OWNER
    # ==========================================

    async def transfer_owner(self, channel):

        if not self.db.exists(channel.id):
            return

        owner = get_next_owner(channel)

        if owner is None:
            await self.delete_room(channel)
            return

        self.db.set_owner(channel.id, owner.id)

        try:
            await owner.send(OWNER_CHANGED)
        except:
            pass

    # ==========================================
    # PANEL SYSTEM
    # ==========================================

    async def send_panel(self, channel):

        guild = channel.guild

        panel_channel = await guild.create_text_channel(
            name=f"{VOICE_PANEL_PREFIX}{channel.id}",
            category=channel.category
        )

        embed = create_panel_embed(self.db, channel)

        message = await panel_channel.send(
            embed=embed,
            view=TempVoiceView(self, channel)
        )

        self.db.set_panel_message(channel.id, message.id)
        self.db.set_panel_channel(channel.id, panel_channel.id)

    async def update_panel(self, channel):

        panel_channel_id = self.db.get_panel_channel(channel.id)
        if not panel_channel_id:
            return

        panel_channel = self.bot.get_channel(panel_channel_id)
        if not panel_channel:
            return

        message_id = self.db.get_panel_message(channel.id)
        if not message_id:
            return

        try:
            message = await panel_channel.fetch_message(message_id)
        except:
            return

        embed = create_panel_embed(self.db, channel)

        await message.edit(
            embed=embed,
            view=TempVoiceView(self, channel)
        )

    # ==========================================
    # VOICE EVENTS
    # ==========================================

@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):

    print("VOICE:", after.channel.id if after.channel else None)

    if after.channel and after.channel.id == CREATE_CHANNEL_ID:
        await self.create_room(member)

    # ======================================
    # TWORZENIE POKOJU
    # ======================================

    if after.channel and after.channel.id == CREATE_CHANNEL_ID:
        await self.create_room(member)
        return

    # ======================================
    # USUWANIE / OWNER SYSTEM
    # ======================================

    if before.channel and self.db.exists(before.channel.id):

        # jeśli kanał pusty
        if is_room_empty(before.channel):

            if DELETE_EMPTY_CHANNELS:
                await self.delete_room(before.channel)
            else:
                await self.transfer_owner(before.channel)

        return

    # ======================================
    # BAN CHECK
    # ======================================

    if after.channel and self.db.exists(after.channel.id):

        banned = self.db.get_banned(after.channel.id)

        if member.id in banned:

            try:
                await member.move_to(None)
                await member.send(ROOM_BANNED)
            except:
                pass

async def setup(bot):
    await bot.add_cog(TempVoiceManager(bot))                
