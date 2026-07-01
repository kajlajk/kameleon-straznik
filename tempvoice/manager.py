import discord
from discord.ext import commands

from .config import *
from .database import load_data, save_data


class TempVoiceManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # Użytkownik nie zmienił kanału
        if before.channel == after.channel:
            return

        # ==========================
        # Tworzenie kanału
        # ==========================

        if after.channel and after.channel.id == CREATE_CHANNEL_ID:

            category = member.guild.get_channel(CATEGORY_ID)

            channel = await member.guild.create_voice_channel(
                name=f"{CHANNEL_PREFIX} {member.display_name}",
                category=category,
                user_limit=DEFAULT_USER_LIMIT
            )

            await member.move_to(channel)

            self.data[str(channel.id)] = {
                "owner": member.id
            }

            save_data(self.data)

        # ==========================
        # Usuwanie pustych kanałów
        # ==========================

        if before.channel:

            if str(before.channel.id) in self.data:

                if len(before.channel.members) == 0:

                    del self.data[str(before.channel.id)]
                    save_data(self.data)

                    await before.channel.delete()


async def setup(bot):
    await bot.add_cog(TempVoiceManager(bot))
