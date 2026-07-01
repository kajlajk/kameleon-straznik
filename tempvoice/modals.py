import discord


class RenameModal(discord.ui.Modal, title="Zmień nazwę kanału"):
    def __init__(self, voice_channel_id):
        super().__init__()

        self.voice_channel_id = voice_channel_id

    new_name = discord.ui.TextInput(
        label="Nowa nazwa",
        placeholder="Wpisz nazwę kanału...",
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.guild.get_channel(self.voice_channel_id)

        if channel is None:
            await interaction.response.send_message(
                "❌ Nie znaleziono kanału.",
                ephemeral=True
            )
            return

        await channel.edit(
            name=self.new_name.value
        )

        await interaction.response.send_message(
            f"✅ Zmieniono nazwę kanału na **{self.new_name.value}**.",
            ephemeral=True
        )
