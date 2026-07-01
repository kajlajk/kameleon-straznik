import discord


class TempVoicePanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Nazwa",
        emoji="✏️",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def rename(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Ta funkcja jest jeszcze w budowie.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Limit",
        emoji="👥",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def limit(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Ta funkcja jest jeszcze w budowie.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Usuń",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def delete(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Ta funkcja jest jeszcze w budowie.",
            ephemeral=True
        )
