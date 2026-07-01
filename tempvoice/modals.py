import discord

from .config import (
    CHANNEL_PREFIX,
    MAX_ROOM_NAME,
    MAX_DESCRIPTION,
    MAX_USER_LIMIT,
    ROOM_RENAMED,
    DESCRIPTION_CHANGED,
    LIMIT_CHANGED
)


class RenameModal(discord.ui.Modal, title="✏️ Zmień nazwę pokoju"):

    room_name = discord.ui.TextInput(
        label="Nowa nazwa",
        max_length=MAX_ROOM_NAME,
        required=True
    )

    def __init__(self, manager, channel):

        super().__init__()

        self.manager = manager
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):

        name = self.room_name.value.strip()

        if name.startswith(CHANNEL_PREFIX):
            name = name[len(CHANNEL_PREFIX):].strip()

        await self.channel.edit(
            name=f"{CHANNEL_PREFIX} {name}"
        )

        await interaction.response.send_message(
            ROOM_RENAMED,
            ephemeral=True
        )

        await self.manager.update_panel(self.channel)


class DescriptionModal(discord.ui.Modal, title="📝 Zmień opis pokoju"):

    description = discord.ui.TextInput(
        label="Opis pokoju",
        style=discord.TextStyle.paragraph,
        max_length=MAX_DESCRIPTION,
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
            DESCRIPTION_CHANGED,
            ephemeral=True
        )

        await self.manager.update_panel(self.channel)


class LimitModal(discord.ui.Modal, title="👥 Zmień limit użytkowników"):

    limit = discord.ui.TextInput(
        label="Limit",
        placeholder="0 = bez limitu",
        required=True,
        max_length=2
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
                "❌ Musisz wpisać liczbę.",
                ephemeral=True
            )

            return

        if limit < 0 or limit > MAX_USER_LIMIT:

            await interaction.response.send_message(
                f"❌ Limit musi być od 0 do {MAX_USER_LIMIT}.",
                ephemeral=True
            )

            return

        await self.channel.edit(
            user_limit=limit
        )

        await interaction.response.send_message(
            LIMIT_CHANGED,
            ephemeral=True
        )

        await self.manager.update_panel(self.channel)
