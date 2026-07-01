import discord
from .data import temp_channels

class KickUserSelect(discord.ui.Select):
    def __init__(self, voice_channel: discord.VoiceChannel, owner: discord.Member):
        options = []
        
        
        # Filtrowanie użytkowników: tylko osoby na tym kanale, bez właściciela i bez botów
        for member in voice_channel.members:
            if member.id != owner.id and not member.bot:
                options.append(discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id),
                    description=f"@{member.name}"
                ))
        
        # Zapobieganie błędowi pustej listy w discord.ui.Select
        if not options:
            options.append(discord.SelectOption(
                label="Brak użytkowników do wyrzucenia",
                value="none"
            ))
            super().__init__(
                placeholder="Kanał jest pusty...", 
                min_values=1, 
                max_values=1, 
                options=options, 
                disabled=True
            )
        else:
            super().__init__(
                placeholder="Wybierz użytkownika, którego chcesz wyrzucić...", 
                min_values=1, 
                max_values=1, 
                options=options
            )
            
        self.voice_channel = voice_channel
        

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("Nie możesz wykonać tej akcji.", ephemeral=True)
            return

        member_id = int(self.values[0])
        member = self.voice_channel.guild.get_member(member_id)
        
        if not member:
            await interaction.response.send_message("Nie znaleziono użytkownika na serwerze.", ephemeral=True)
            return

        # Sprawdzenie, czy użytkownik nadal znajduje się na kanale głosowym
        if member not in self.voice_channel.members:
            await interaction.response.send_message("Ten użytkownik zdążył już opuścić kanał.", ephemeral=True)
            return

        try:
            # 1. Rozłączenie użytkownika z kanału głosowego
            await member.move_to(None, reason="Wyrzucony przez właściciela kanału TempVoice.")
            
            # 2. Zablokowanie możliwości ponownego wejścia (connect=False) dla tego konkretnego użytkownika
            await self.voice_channel.set_permissions(member, connect=False, reason="Ban na kanał TempVoice.")
            
            # 3. Zapis ID użytkownika do listy zbanowanych w temp_channels
            if self.voice_channel.id in temp_channels:
                temp_channels[self.voice_channel.id]["banned"].add(member_id)

            await interaction.response.send_message(f"Pomyślnie wyrzucono i zablokowano użytkownika {member.mention}.", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("Bot nie posiada wystarczających uprawnień (Zarządzanie kanałami / Wyrzucanie członków), aby wykonać tę akcję.", ephemeral=True)
        except Exception:
            await interaction.response.send_message(
                "❌ Wystąpił nieoczekiwany błąd.",
                ephemeral=True
            )

class UnbanUserSelect(discord.ui.Select):
    def __init__(self, voice_channel: discord.VoiceChannel):
        self.voice_channel = voice_channel

        options = []

        data = temp_channels.get(voice_channel.id)

        if data:
            for user_id in data["banned"]:

                member = voice_channel.guild.get_member(user_id)

                if member:
                    label = member.display_name
                    description = f"@{member.name}"
                else:
                    label = "Nieznany użytkownik"
                    description = str(user_id)

                options.append(
                    discord.SelectOption(
                        label=label,
                        value=str(user_id),
                        description=description
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(
                    label="Brak zbanowanych użytkowników",
                    value="none"
                )
            )

            super().__init__(
                placeholder="Brak osób do odbanowania",
                options=options,
                disabled=True
            )

        else:
            super().__init__(
                placeholder="Wybierz użytkownika...",
                options=options,
                min_values=1,
                max_values=1
            )
            
    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "none":
            await interaction.response.send_message(
                "❌ Nie ma nikogo do odbanowania.",
                ephemeral=True
            )
            return

        user_id = int(self.values[0])

        member = interaction.guild.get_member(user_id)

        if member:
            await self.voice_channel.set_permissions(
                member,
                overwrite=None
            )

        if self.voice_channel.id in temp_channels:
            temp_channels[self.voice_channel.id]["banned"].discard(user_id)

        await interaction.response.send_message(
            "✅ Użytkownik został odbanowany.",
            ephemeral=True
        )
