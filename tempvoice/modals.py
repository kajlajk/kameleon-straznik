import discord


class RenameRoomModal(discord.ui.Modal, title="✏️ Zmień nazwę pokoju"):

    room_name = discord.ui.TextInput(
        label="Nowa nazwa pokoju",
        placeholder="Np. Gramy Ranked",
        min_length=1,
        max_length=30,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            "🚧 Ta funkcja będzie dostępna w następnym etapie.",
            ephemeral=True
        )


class DescriptionModal(discord.ui.Modal, title="📝 Zmień opis pokoju"):

    description = discord.ui.TextInput(
        label="Opis pokoju",
        placeholder="Np. Zapraszamy do wspólnej gry!",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            "🚧 Ta funkcja będzie dostępna w następnym etapie.",
            ephemeral=True
        )


class LimitModal(discord.ui.Modal, title="👥 Zmień limit osób"):

    limit = discord.ui.TextInput(
        label="Limit (0-99)",
        placeholder="0 = bez limitu",
        min_length=1,
        max_length=2,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            "🚧 Ta funkcja będzie dostępna w następnym etapie.",
            ephemeral=True
        )
