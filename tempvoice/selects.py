import discord


# ==========================
# KICK
# ==========================

class KickSelect(discord.ui.Select):

    def __init__(self, members):

        options = []

        for member in members:
            options.append(
                discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id)
                )
            )

        super().__init__(
            placeholder="👢 Wybierz użytkownika...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            "🚧 Kick będzie działał w następnym etapie.",
            ephemeral=True
        )


class KickView(discord.ui.View):

    def __init__(self, members):

        super().__init__(timeout=60)

        self.add_item(
            KickSelect(members)
        )


# ==========================
# BAN
# ==========================

class BanSelect(discord.ui.Select):

    def __init__(self, members):

        options = []

        for member in members:
            options.append(
                discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id)
                )
            )

        super().__init__(
            placeholder="🚫 Wybierz użytkownika...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):

        await interaction.response.send_message(
            "🚧 Ban będzie działał w następnym etapie.",
            ephemeral=True
        )


class BanView(discord.ui.View):

    def __init__(self, members):

        super().__init__(timeout=60)

        self.add_item(
            BanSelect(members)
        )


# ==========================
# UNBAN
# ==========================

class UnbanSelect(discord.ui.Select):

    def __init__(self, users):

        options = []

        if len(users) == 0:

            options.append(
                discord.SelectOption(
                    label="Brak zbanowanych",
                    value="0"
                )
            )

        else:

            for user in users:

                options.append(
                    discord.SelectOption(
                        label=user.display_name,
                        value=str(user.id)
                    )
                )

        super().__init__(
            placeholder="✅ Wybierz użytkownika...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):

        await interaction.response.send_message(
            "🚧 Unban będzie działał w następnym etapie.",
            ephemeral=True
        )


class UnbanView(discord.ui.View):

    def __init__(self, users):

        super().__init__(timeout=60)

        self.add_item(
            UnbanSelect(users)
        )


# ==========================
# OWNER
# ==========================

class OwnerSelect(discord.ui.Select):

    def __init__(self, members):

        options = []

        for member in members:

            options.append(
                discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id)
                )
            )

        super().__init__(
            placeholder="👑 Nowy owner...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):

        await interaction.response.send_message(
            "🚧 Transfer ownera będzie działał w następnym etapie.",
            ephemeral=True
        )


class OwnerView(discord.ui.View):

    def __init__(self, members):

        super().__init__(timeout=60)

        self.add_item(
            OwnerSelect(members)
        )


# ==========================
# CO OWNER
# ==========================

class CoOwnerSelect(discord.ui.Select):

    def __init__(self, members):

        options = []

        for member in members:

            options.append(
                discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id)
                )
            )

        super().__init__(
            placeholder="⭐ Wybierz współwłaściciela...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):

        await interaction.response.send_message(
            "🚧 Współwłaściciel będzie działał w następnym etapie.",
            ephemeral=True
        )


class CoOwnerView(discord.ui.View):

    def __init__(self, members):

        super().__init__(timeout=60)

        self.add_item(
            CoOwnerSelect(members)
        )
