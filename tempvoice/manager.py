import discord
from discord.ext import commands

from .config import *

temp_channels = {}


class TempVoiceManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(TempVoiceManager(bot))
