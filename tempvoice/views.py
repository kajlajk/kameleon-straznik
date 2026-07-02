import discord
from .data import temp_channels
from .modals import RenameModal, LimitModal
from .selects import KickUserSelect, UnbanUserSelect, TransferOwnerSelect

class KickUserView(discord.ui.View):
    def __init__(self, voice_channel: discord.VoiceChannel, owner: discord.Member):
        super().__init__(timeout=60)
        self.add_item(KickUserSelect(voice_channel, owner))

class UnbanUserView(discord.ui.View):
    def __init__(self, voice_channel: discord.VoiceChannel):
        super().__init__(timeout=60)
        self.add_item(UnbanUserSelect(voice_channel))

class TransferOwnerView(discord.ui.View):
    def __init__(self, voice_channel: discord.VoiceChannel, owner: discord.Member):
        super().__init__(timeout=60)
        self.add_item(TransferOwnerSelect(voice_channel, owner))

class TempVoicePanel(discord.ui.View):
    def __init__(self, voice_channel_id: int, text_channel_id: int):
        # Usunięto owner_id z inita, ponieważ pobieramy go dynamicznie ze słownika
        super().__init__(timeout=None)
        self.voice_channel_id = voice_channel_id
        self.text_channel_id = text_channel_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.voice_channel_id not in temp_channels:
            await interaction.response.send_message(
                "❌ Nie znaleziono danych kanału w bazie bota.",
                ephemeral=True
            )
            return False
    
        current_owner = temp_channels[self.voice_channel_id].get("owner")
    
        if interaction.user.id != current_owner:
            await interaction.response.send_message(
                "❌ Ten panel zarządzania nie należy do Ciebie.",
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
        await interaction.response.send_modal(RenameModal(self.voice_channel_id))

    @discord.ui.button(
        label="Limit",
        emoji="👥",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LimitModal(self.voice_channel_id))
       
    @discord.ui.button(
        label="Zablokuj",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.guild.get_channel(self.voice_channel_id)
        if channel is None:
            await interaction.response.send_message("❌ Nie znaleziono kanału.", ephemeral=True)
            return

        await channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 Kanał został zablokowany dla wszystkich.", ephemeral=True)

    @discord.ui.button(
        label="Odblokuj",
        emoji="🔓",
        style=discord.ButtonStyle.success,
        row=0  # Przeniesiono do row=0, żeby kłódki były obok siebie
    )
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.guild.get_channel(self.voice_channel_id)
        if channel is None:
            await interaction.response.send_message("❌ Nie znaleziono kanału.", ephemeral=True)
            return

        await channel.set_permissions(interaction.guild.default_role, connect=None)
        await interaction.response.send_message("🔓 Kanał został odblokowany.", ephemeral=True)

    @discord.ui.button(
        label="Wyrzuć",
        emoji="👢",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = interaction.guild.get_channel(self.voice_channel_id)
        if voice_channel is None:
            await interaction.response.send_message("❌ Nie znaleziono kanału.", ephemeral=True)
            return
    
        view = KickUserView(voice_channel, interaction.user)
        await interaction.response.send_message(
            "👢 Wybierz użytkownika z listy, którego chcesz wyrzucić.",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Odbanuj",
        emoji="🚪",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = interaction.guild.get_channel(self.voice_channel_id)
        if voice_channel is None:
            await interaction.response.send_message("❌ Nie znaleziono kanału.", ephemeral=True)
            return
    
        view = UnbanUserView(voice_channel)
        await interaction.response.send_message(
            "🚪 Wybierz użytkownika, któremu chcesz cofnąć blokadę wstępu.",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Przekaż",
        emoji="👑",
        style=discord.ButtonStyle.success,
        row=1  # Przeniesiono do row=1, panel zmieści się teraz idealnie w dwóch rzędach
    )
    async def transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = interaction.guild.get_channel(self.voice_channel_id)
        if voice_channel is None:
            await interaction.response.send_message("❌ Nie znaleziono kanału.", ephemeral=True)
            return
    
        view = TransferOwnerView(voice_channel, interaction.user)
        await interaction.response.send_message(
            "👑 Wybierz osobę, której chcesz oddać koronę właściciela kanału.",
            view=view,
            ephemeral=True
        )
