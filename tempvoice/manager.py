import discord
from discord.ext import commands

from .data import temp_channels
from .views import TempVoicePanel

CREATE_CHANNEL_ID = 1521876957795455107


class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # Tworzenie kanału
        if after.channel and after.channel.id == CREATE_CHANNEL_ID:

            category = after.channel.category

            # Kanał głosowy
            voice_channel = await category.create_voice_channel(
                name=f"🎤 {member.display_name}"
            )

            # Uprawnienia kanału tekstowego
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                ),
                member: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),
                member.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            }

            # Kanał tekstowy
            text_channel = await category.create_text_channel(
                name=f"🎛-{member.name.lower()}",
                overwrites=overwrites
            )

            # Zapamiętanie danych
            temp_channels[voice_channel.id] = {
                "owner": member.id,
                "banned": set(),
                "text_channel": text_channel.id
            }

            # Przeniesienie użytkownika
            await member.move_to(voice_channel)

            # Panel
            embed = discord.Embed(
                title="🎛 Zarządzanie kanałem",
                description="Użyj przycisków poniżej, aby zarządzać swoim kanałem.",
                color=discord.Color.green()
            )

            embed.add_field(
                name="👑 Właściciel",
                value=member.mention,
                inline=False
            )

            await text_channel.send(
                embed=embed,
                view=TempVoicePanel(
                    voice_channel.id,
                    text_channel.id,
                    member.id
                )
            )

        # Usuwanie kanału
        if before.channel and before.channel.id in temp_channels:

            if len(before.channel.members) == 0:

                text_channel_id = temp_channels[before.channel.id]["text_channel"]

                text_channel = member.guild.get_channel(text_channel_id)

                if text_channel:
                    await text_channel.delete()

                del temp_channels[before.channel.id]

                await before.channel.delete()


async def setup(bot):
    await bot.add_cog(TempVoice(bot))
