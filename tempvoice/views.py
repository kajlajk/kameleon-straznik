import discord

from .modals import (
    RenameRoomModal,
    DescriptionModal,
    LimitModal
)


class MainPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    # ==========================
    # RZĄD 1
    # ==========================

    @discord.ui.button(
        emoji="✏️",
        label="Nazwa",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def rename(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            RenameRoomModal()
        )

    @discord.ui.button(
        emoji="📝",
        label="Opis",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def description(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            DescriptionModal()
        )

    @discord.ui.button(
        emoji="👥",
        label="Limit",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def limit(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            LimitModal()
        )

    # ==========================
    # RZĄD 2
    # ==========================

    @discord.ui.button(
        emoji="👢",
        label="Kick",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Kick będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="🚫",
        label="Ban",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Ban będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="✅",
        label="Unban",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def unban(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Unban będzie w następnym etapie.",
            ephemeral=True
        )

    # ==========================
    # RZĄD 3
    # ==========================

    @discord.ui.button(
        emoji="➡️",
        label="Następna",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            view=SettingsPanel()
        )


class SettingsPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        emoji="🔒",
        label="Lock",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def lock(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Lock będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="🔓",
        label="Unlock",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def unlock(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Unlock będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="🔐",
        label="Prywatny",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def private(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Prywatny pokój będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="🌐",
        label="Publiczny",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def public(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Publiczny pokój będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="👑",
        label="Owner",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def owner(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Transfer ownera będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="⭐",
        label="Współwłaściciel",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def co_owner(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Współwłaściciel będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="🗑️",
        label="Usuń",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def delete(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🚧 Potwierdzenie usunięcia będzie w następnym etapie.",
            ephemeral=True
        )

    @discord.ui.button(
        emoji="⬅️",
        label="Powrót",
        style=discord.ButtonStyle.secondary,
        row=3
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            view=MainPanel()
        )
