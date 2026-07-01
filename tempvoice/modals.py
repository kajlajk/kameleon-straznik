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

        await channel.edit(name=self.new_name.value)

        await interaction.response.send_message(
            f"✅ Zmieniono nazwę kanału na **{self.new_name.value}**.",
            ephemeral=True
        )


class LimitModal(discord.ui.Modal, title="Ustaw limit kanału"):
    def __init__(self, voice_channel_id):
        super().__init__()

        self.voice_channel_id = voice_channel_id

    limit = discord.ui.TextInput(
        label="Limit osób",
        placeholder="Podaj liczbę od 0 do 99",
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.guild.get_channel(self.voice_channel_id)

        if channel is None:
            await interaction.response.send_message(
                "❌ Nie znaleziono kanału.",
                ephemeral=True
            )
            return

        try:
            limit = int(self.limit.value)
        except ValueError:
            await interaction.response.send_message(
                "❌ Musisz podać liczbę od 0 do 99.",
                ephemeral=True
            )
            return

        if limit < 0 or limit > 99:
            await interaction.response.send_message(
                "❌ Limit musi być z zakresu 0-99.",
                ephemeral=True
            )
            return

        await channel.edit(user_limit=limit)

        if limit == 0:
            tekst = "✅ Usunięto limit kanału."
        else:
            tekst = f"✅ Ustawiono limit na **{limit}** osób."

        await interaction.response.send_message(
            tekst,
            ephemeral=True
        )
