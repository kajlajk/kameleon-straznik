import discord

from .modals import (
    RenameModal,
    DescriptionModal,
    LimitModal
)


class ActionSelect(discord.ui.Select):

    def __init__(self, manager, channel):

        self.manager = manager
        self.channel = channel

        options = [

            discord.SelectOption(
                label="Zmień nazwę",
                emoji="✏️",
                value="rename"
            ),

            discord.SelectOption(
                label="Zmień opis",
                emoji="📝",
                value="description"
            ),

            discord.SelectOption(
                label="Zmień limit",
                emoji="👥",
                value="limit"
            ),

            discord.SelectOption(
                label="Wyrzuć użytkownika",
                emoji="👢",
                value="kick"
            ),

            discord.SelectOption(
                label="Zbanuj użytkownika",
                emoji="🚫",
                value="ban"
            ),

            discord.SelectOption(
                label="Przekaż ownera",
                emoji="👑",
                value="owner"
            ),

            discord.SelectOption(
                label="Ustaw współwłaściciela",
                emoji="⭐",
                value="co_owner"
            ),

            discord.SelectOption(
                label="Zablokuj pokój",
                emoji="🔒",
                value="lock"
            ),

            discord.SelectOption(
                label="Odblokuj pokój",
                emoji="🔓",
                value="unlock"
            ),

            discord.SelectOption(
                label="Prywatny",
                emoji="🔐",
                value="private"
            ),

            discord.SelectOption(
                label="Publiczny",
                emoji="🌐",
                value="public"
            ),

            discord.SelectOption(
                label="Usuń pokój",
                emoji="🗑️",
                value="delete"
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

        # kolejne opcje dopiszemy w manager.py


class TempVoiceView(discord.ui.View):

    def __init__(self, manager, channel):

        super().__init__(timeout=None)

        self.add_item(
            ActionSelect(
                manager,
                channel
            )
        )
