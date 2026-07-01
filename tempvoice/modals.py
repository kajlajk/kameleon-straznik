import discord


class RenameModal(discord.ui.Modal, title="Zmień nazwę kanału"):

    new_name = discord.ui.TextInput(
        label="Nowa nazwa",
        placeholder="Wpisz nazwę kanału...",
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.user.voice.channel.edit(
            name=self.new_name.value
        )

        await interaction.response.send_message(
            "✅ Nazwa kanału została zmieniona.",
            ephemeral=True
        )
