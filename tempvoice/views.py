import discord

from .modals import (
    RenameModal,
    DescriptionModal,
    LimitModal
)


class TempVoiceSelect(discord.ui.Select):

    def __init__(self, manager, channel):

        self.manager = manager
        self.channel = channel

        options = [

            discord.SelectOption(
                label="✏️ Zmień nazwę",
                value="rename"
            ),

            discord.SelectOption(
                label="📝 Zmień opis",
                value="description"
            ),

            discord.SelectOption(
                label="👥 Zmień limit",
                value="limit"
            ),

            discord.SelectOption(
                label="🚫 Zbanuj użytkownika",
                value="ban"
            )

        ]

        super().__init__(
            placeholder="🎛️ Zarządzaj pokojem...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        value = self.values[0]

        if value == "rename":

            await interaction.response.send_modal(
                RenameModal(
                    self.manager,
                    self.channel
                )
            )

            return

        if value == "description":

            await interaction.response.send_modal(
                DescriptionModal(
                    self.manager,
                    self.channel
                )
            )

            return

        if value == "limit":

            await interaction.response.send_modal(
                LimitModal(
                    self.manager,
                    self.channel
                )
            )

            return

        if value == "ban":

            await self.manager.open_ban_menu(
                interaction,
                self.channel
            )


class TempVoiceView(discord.ui.View):

    def __init__(self, manager, channel):

        super().__init__(timeout=None)

        self.add_item(
            TempVoiceSelect(
                manager,
                channel
            )
        )
