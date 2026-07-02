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
        await interaction.response.defer(ephemeral=True)

        if self.values[0] == "none":
            await interaction.followup.send("❌ Nie możesz wykonać tej akcji.", ephemeral=True)
            return

        member_id = int(self.values[0])
        member = self.voice_channel.guild.get_member(member_id)
        
        if not member:
            await interaction.followup.send("❌ Nie znaleziono użytkownika na serwerze.", ephemeral=True)
            return

        if member not in self.voice_channel.members:
            await interaction.followup.send("⚠️ Ten użytkownik zdążył już opuścić kanał.", ephemeral=True)
            return

        try:
            # 1. Rozłączenie użytkownika z kanału głosowego
            await member.move_to(None, reason="Wyrzucony przez właściciela kanału TempVoice.")
            
            # 2. Zablokowanie możliwości ponownego wejścia za pomocą jednoznacznego Overwrite
            overwrite = discord.PermissionOverwrite(connect=False)
            await self.voice_channel.set_permissions(member, overwrite=overwrite, reason="Ban na kanał TempVoice.")
            
            # 3. Zapis ID użytkownika do listy zbanowanych w temp_channels
            if self.voice_channel.id in temp_channels:
                temp_channels[self.voice_channel.id]["banned"].add(member_id)

            await interaction.followup.send(f"👢 Pomyślnie wyrzucono i zablokowano użytkownika {member.mention}.", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Bot nie posiada uprawnień (Zarządzanie kanałami / Wyrzucanie), aby wykonać tę akcję.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Wystąpił nieoczekiwany błąd.", ephemeral=True)
        

class UnbanUserSelect(discord.ui.Select):
    def __init__(self, voice_channel: discord.VoiceChannel):
        self.voice_channel = voice_channel
        options = []
        data = temp_channels.get(voice_channel.id)

        if data:
            # Zabezpieczenie: Maksymalnie 25 opcji w Menu rozwijanym
            for user_id in list(data["banned"])[:25]:
                member = voice_channel.guild.get_member(user_id)
                if member:
                    label = member.display_name
                    description = f"@{member.name}"
                else:
                    label = "Nieznany użytkownik"
                    description = f"ID: {user_id}"

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
                placeholder="Wybierz użytkownika, którego chcesz odbanować...",
                options=options,
                min_values=1,
                max_values=1
            )
            
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.values[0] == "none":
            await interaction.followup.send("❌ Nie ma nikogo do odbanowania.", ephemeral=True)
            return

        user_id = int(self.values[0])
        member = interaction.guild.get_member(user_id)

        try:
            # Usuwamy indywidualne nadpisanie uprawnień (zarówno dla obecnych na serwerze, jak i tych, co wyszli)
            target = member if member else discord.Object(id=user_id)
            await self.voice_channel.set_permissions(target, overwrite=None)

            if self.voice_channel.id in temp_channels:
                temp_channels[self.voice_channel.id]["banned"].discard(user_id)

            await interaction.followup.send("✅ Użytkownik został pomyślnie odbanowany.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ Wystąpił błąd podczas odbanowywania.", ephemeral=True)


class TransferOwnerSelect(discord.ui.Select):
    def __init__(self, voice_channel: discord.VoiceChannel, owner: discord.Member):
        self.voice_channel = voice_channel
        options = []

        for member in voice_channel.members:
            if member.id != owner.id and not member.bot:
                options.append(
                    discord.SelectOption(
                        label=member.display_name,
                        value=str(member.id),
                        description=f"@{member.name}"
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(
                    label="Brak użytkowników",
                    value="none"
                )
            )
            super().__init__(
                placeholder="Nie ma komu przekazać kanału",
                options=options,
                disabled=True
            )
        else:
            super().__init__(
                placeholder="Wybierz nowego właściciela kanału...",
                options=options,
                min_values=1,
                max_values=1
            )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.values[0] == "none":
            await interaction.followup.send("❌ Nie ma komu przekazać kanału.", ephemeral=True)
            return

        if self.voice_channel.id not in temp_channels:
            await interaction.followup.send("❌ Nie znaleziono danych tego kanału w pamięci bota.", ephemeral=True)
            return

        # Sprawdzenie, czy osoba klikająca to wciąż ta sama osoba, która figuruje jako właściciel
        actual_old_owner_id = temp_channels[self.voice_channel.id]["owner"]
        if interaction.user.id != actual_old_owner_id:
            await interaction.followup.send("❌ Nie jesteś już właścicielem tego kanału.", ephemeral=True)
            return

        new_owner_id = int(self.values[0])
        
        # Jeśli ktoś wybrał samego siebie (teoretycznie odfiltrowane, ale na wszelki wypadek)
        if new_owner_id == actual_old_owner_id:
            await interaction.followup.send("👑 Już jesteś właścicielem tego kanału.", ephemeral=True)
            return

        new_owner = interaction.guild.get_member(new_owner_id)
        old_owner = interaction.guild.get_member(actual_old_owner_id)

        if new_owner is None:
            await interaction.followup.send("❌ Nie znaleziono nowego właściciela na tym serwerze.", ephemeral=True)
            return

        text_channel_id = temp_channels[self.voice_channel.id]["text_channel"]
        text_channel = interaction.guild.get_channel(text_channel_id)

        if text_channel is None:
            await interaction.followup.send("❌ Nie znaleziono powiązanego kanału tekstowego.", ephemeral=True)
            return

        # Zmiana właściciela w pamięci bota – robimy to PRZED jakimkolwiek API, by baza była stabilna
        temp_channels[self.voice_channel.id]["owner"] = new_owner.id

        # Pakujemy całą komunikację z Discordem w potężny try/except, by uniknąć wiecznego zawieszenia interakcji
        try:
            # 1. Aktualizacja uprawnień do kanału tekstowego
            if old_owner:
                await text_channel.set_permissions(old_owner, overwrite=None)

            await text_channel.set_permissions(
                new_owner,
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

            # 2. Zmiana nazwy kanału głosowego (opcjonalnie, bez crashowania bota przy Rate Limitach)
            try:
                await self.voice_channel.edit(name=f"🔊 {new_owner.display_name}")
            except Exception:
                pass

            # 3. Odświeżenie embedu w panelu zarządczym
            panel_message_id = temp_channels[self.voice_channel.id]["panel_message"]
            panel_message = await text_channel.fetch_message(panel_message_id)

            embed = discord.Embed(
                title="🎛 Zarządzanie kanałem",
                description="Użyj przycisków poniżej, aby zarządzać swoim kanałem.",
                color=discord.Color.green()
            )
            embed.add_field(name="👑 Właściciel", value=new_owner.mention, inline=False)

            await panel_message.edit(embed=embed)

        except discord.HTTPException as e:
            # Gdy złapiemy Rate Limit (kod błędu HTTP 429), zdejmujemy klepsydrę i informujemy użytkownika
            await interaction.followup.send("⚠️ Korona została przekazana w pamięci, ale Discord ogranicza prędkość bota (Rate Limit). Wygląd panelu zaktualizuje się za chwilę.", ephemeral=True)
            return
        except Exception:
            # Wszelkie inne błędy (np. brak uprawnień) nie zablokują odpowiedzi bota
            pass
        
        # Kluczowe zakończenie interakcji – zdejmuje status "Kameleon Guard myśli..."
        await interaction.followup.send(
            f"👑 Korona przekazana! Nowym właścicielem kanału został {new_owner.mention}.",
            ephemeral=True
        )
