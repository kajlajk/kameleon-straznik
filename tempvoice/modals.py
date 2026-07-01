import discord


class RenameModal(discord.ui.Modal, title="✏️ Zmień nazwę pokoju"):

    room_name = discord.ui.TextInput(
        label="Nowa nazwa",
        placeholder="Np. Gramy Ranked",
        min_length=1,
        max_length=30,
        required=True
    )

    def __init__(self, manager, channel):
        super().__init__()

        self.manager = manager
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):

        await self.channel.edit(
            name=f"🔊 {self.room_name.value}"
        )

        await interaction.response.send_message(
            "✅ Nazwa pokoju została zmieniona.",
            ephemeral=True
        )

        await self.manager.update_panel(self.channel)


class DescriptionModal(discord.ui.Modal, title="📝 Zmień opis pokoju"):

    description = discord.ui.TextInput(
        label="Opis pokoju",
        placeholder="Np. Zapraszamy do wspólnej gry!",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=False
    )

    def __init__(self, manager, channel):
        super().__init__()

        self.manager = manager
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):

        self.manager.db.set_description(
            self.channel.id,
            self.description.value
        )

        await interaction.response.send_message(
            "✅ Opis został zapisany.",
            ephemeral=True
        )

        await self.manager.update_panel(self.channel)


class LimitModal(discord.ui.Modal, title="👥 Zmień limit osób"):

    limit = discord.ui.TextInput(
        label="Limit osób",
        placeholder="0 = bez limitu",
        min_length=1,
        max_length=2,
        required=True
    )

    def __init__(self, manager, channel):
        super().__init__()

        self.manager = manager
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):

        try:

            limit = int(self.limit.value)

        except ValueError:

            await interaction.response.send_message(
                "❌ Wpisz poprawną liczbę.",
                ephemeral=True
            )

            return

        if limit < 0 or limit > 99:

            await interaction.response.send_message(
                "❌ Limit musi być od 0 do 99.",
                ephemeral=True
            )

            return

        await self.channel.edit(
            user_limit=limit
        )

        self.manager.db.set_limit(
            self.channel.id,
            limit
        )

        await interaction.response.send_message(
            "✅ Limit został zmieniony.",
            ephemeral=True
        )

        await self.manager.update_panel(self.channel)
