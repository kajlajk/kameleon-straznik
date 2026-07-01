import discord

class RenameModal(discord.ui.Modal, title="Zmień nazwę kanału"):
    def __init__(self, voice_channel_id):
        super().__init__()
        self.voice_channel_id = voice_channel_id

    new_name = discord.ui.TextInput(
        label="Nowa nazwa",
        placeholder="Wpisz nazwę kanału...",
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Informujemy Discorda, że przetwarzamy żądanie (zapobiega czerwonej ramce błędu)
        await interaction.response.defer(ephemeral=True, thinking=True)

        channel = interaction.guild.get_channel(self.voice_channel_id)

        if channel is None:
            await interaction.followup.send(
                "❌ Nie znaleziono kanału.",
                ephemeral=True
            )
            return

        try:
            await channel.edit(name=self.new_name.value)
        except discord.HTTPException as e:
            # Specjalna obsługa limitu Discorda (2 zmiany nazwy na 10 minut)
            if e.status == 429:
                await interaction.followup.send(
                    "⚠️ Osiągnięto limit Discorda! Nazwę kanału można zmienić maksymalnie 2 razy na 10 minut. Spróbuj ponownie za chwilę.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Błąd API ({e.status}): {e.text}",
                    ephemeral=True
                )
            return
        except Exception as e:
            await interaction.followup.send(
                f"❌ {type(e).__name__}: {e}",
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            f"✅ Zmieniono nazwę kanału na **{self.new_name.value}**.",
            ephemeral=True
        )


class LimitModal(discord.ui.Modal, title="Ustaw limit kanału"):
    def __init__(self, voice_channel_id):
        super().__init__()
        self.voice_channel_id = voice_channel_id

    limit = discord.ui.TextInput(
        label="Limit osób",
        placeholder="Podaj liczbę od 0 do 99",
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Tutaj również odraczamy interakcję dla świętego spokoju i stabilności bota
        await interaction.response.defer(ephemeral=True, thinking=True)

        channel = interaction.guild.get_channel(self.voice_channel_id)

        if channel is None:
            await interaction.followup.send(
                "❌ Nie znaleziono kanału.",
                ephemeral=True
            )
            return

        try:
            limit = int(self.limit.value)
        except ValueError:
            await interaction.followup.send(
                "❌ Musisz podać liczbę od 0 do 99.",
                ephemeral=True
            )
            return

        if limit < 0 or limit > 99:
            await interaction.followup.send(
                "❌ Limit musi być z zakresu 0-99.",
                ephemeral=True
            )
            return

        try:
            await channel.edit(user_limit=limit)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Nie udało się zmienić limitu: {e}",
                ephemeral=True
            )
            return

        if limit == 0:
            tekst = "✅ Usunięto limit kanału."
        else:
            tekst = f"✅ Ustawiono limit na **{limit}** osób."

        await interaction.followup.send(
            tekst,
            ephemeral=True
        )
