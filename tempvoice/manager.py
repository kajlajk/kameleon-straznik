import discord
from discord.ext import commands

from .data import temp_channels

CREATE_CHANNEL_ID = 0  # tutaj później wpiszemy ID kanału "➕ Utwórz pokój"


class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # Tworzenie kanału
        if after.channel and after.channel.id == CREATE_CHANNEL_ID:

            category = after.channel.category

            channel = await category.create_voice_channel(
                name=f"🎤 {member.display_name}"
            )

            temp_channels[channel.id] = {
                "owner": member.id,
                "banned": set()
            }

            await member.move_to(channel)

        # Usuwanie kanału
        if before.channel and before.channel.id in temp_channels:

            if len(before.channel.members) == 0:

                del temp_channels[before.channel.id]

                await before.channel.delete()


async def setup(bot):
    await bot.add_cog(TempVoice(bot))
