import discord
from .modals import RenameModal


class TempVoicePanel(discord.ui.View):
    def __init__(self, voice_channel_id, text_channel_id, owner_id):
        super().__init__(timeout=None)

        self.voice_channel_id = voice_channel_id
        self.text_channel_id = text_channel_id
        self.owner_id = owner_id

    async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id != self.owner_id:

            await interaction.response.send_message(
                "❌ Ten panel nie należy do Ciebie.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Nazwa",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            RenameModal(self.voice_channel_id)
    )


    @discord.ui.button(
        label="Limit",
        emoji="👥",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👥 Kliknięto Limit",
            ephemeral=True
        )

    @discord.ui.button(
        label="Zablokuj",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔒 Kliknięto Zablokuj",
            ephemeral=True
        )

    @discord.ui.button(
        label="Odblokuj",
        emoji="🔓",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔓 Kliknięto Odblokuj",
            ephemeral=True
        )

    @discord.ui.button(
        label="Wyrzuć",
        emoji="👢",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👢 Kliknięto Wyrzuć",
            ephemeral=True
        )

    @discord.ui.button(
        label="Odbanuj",
        emoji="🚪",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🚪 Kliknięto Odbanuj",
            ephemeral=True
        )

    @discord.ui.button(
        label="Przekaż",
        emoji="👑",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👑 Kliknięto Przekaż",
            ephemeral=True
        )
