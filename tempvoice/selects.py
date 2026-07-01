import discord

from .data import temp_channels


class KickSelect(discord.ui.Select):
    def __init__(self, voice_channel_id):

        self.voice_channel_id = voice_channel_id

        options = []

        super().__init__(
            placeholder="Wybierz użytkownika...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        channel = interaction.guild.get_channel(self.voice_channel_id)

        if channel is None:
            await interaction.response.send_message(
                "❌ Nie znaleziono kanału.",
                ephemeral=True
            )
            return

        member = interaction.guild.get_member(int(self.values[0]))

        if member is None:
            await interaction.response.send_message(
                "❌ Nie znaleziono użytkownika.",
                ephemeral=True
            )
            return

        await member.move_to(None)

        await channel.set_permissions(
            member,
            connect=False
        )

        temp_channels[self.voice_channel_id]["banned"].add(member.id)

        await interaction.response.send_message(
            f"👢 {member.mention} został wyrzucony z kanału.",
            ephemeral=True
        )


class KickView(discord.ui.View):
    def __init__(self, voice_channel_id):
        super().__init__(timeout=60)

        channel = None

        self.select = KickSelect(voice_channel_id)

        self.add_item(self.select)
