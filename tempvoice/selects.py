import discord


# ==================================================
# KICK
# ==================================================

class KickSelect(discord.ui.UserSelect):

    def __init__(self, manager, channel):

        super().__init__(
            placeholder="👢 Wybierz użytkownika...",
            min_values=1,
            max_values=1
        )

        self.manager = manager
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):

        member = self.values[0]

        await self.manager.kick_member(
            interaction,
            self.channel,
            member
        )


class KickView(discord.ui.View):

    def __init__(self, manager, channel):

        super().__init__(timeout=60)

        self.add_item(
            KickSelect(manager, channel)
        )


# ==================================================
# BAN
# ==================================================

class BanSelect(discord.ui.UserSelect):

    def __init__(self, manager, channel):

        super().__init__(
            placeholder="🚫 Wybierz użytkownika...",
            min_values=1,
            max_values=1
        )

        self.manager = manager
        self.channel = channel

    async def callback(self, interaction):

        member = self.values[0]

        await self.manager.ban_member(
            interaction,
            self.channel,
            member
        )


class BanView(discord.ui.View):

    def __init__(self, manager, channel):

        super().__init__(timeout=60)

        self.add_item(
            BanSelect(manager, channel)
        )


# ==================================================
# OWNER
# ==================================================

class OwnerSelect(discord.ui.UserSelect):

    def __init__(self, manager, channel):

        super().__init__(
            placeholder="👑 Wybierz nowego ownera...",
            min_values=1,
            max_values=1
        )

        self.manager = manager
        self.channel = channel

    async def callback(self, interaction):

        member = self.values[0]

        await self.manager.change_owner(
            interaction,
            self.channel,
            member
        )


class OwnerView(discord.ui.View):

    def __init__(self, manager, channel):

        super().__init__(timeout=60)

        self.add_item(
            OwnerSelect(manager, channel)
        )


# ==================================================
# CO OWNER
# ==================================================

class CoOwnerSelect(discord.ui.UserSelect):

    def __init__(self, manager, channel):

        super().__init__(
            placeholder="⭐ Wybierz współwłaściciela...",
            min_values=1,
            max_values=1
        )

        self.manager = manager
        self.channel = channel

    async def callback(self, interaction):

        member = self.values[0]

        await self.manager.set_co_owner(
            interaction,
            self.channel,
            member
        )


class CoOwnerView(discord.ui.View):

    def __init__(self, manager, channel):

        super().__init__(timeout=60)

        self.add_item(
            CoOwnerSelect(manager, channel)
        )
