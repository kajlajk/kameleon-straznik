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
                placeholder="Wybierz nowego właściciela...",
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
            await interaction.followup.send("❌ Nie znaleziono danych kanału.", ephemeral=True)
            return

        new_owner_id = int(self.values[0])
        old_owner_id = temp_channels[self.voice_channel.id]["owner"]

        new_owner = interaction.guild.get_member(new_owner_id)
        old_owner = interaction.guild.get_member(old_owner_id)

        if new_owner is None:
            await interaction.followup.send("❌ Nie znaleziono nowego właściciela.", ephemeral=True)
            return

        text_channel_id = temp_channels[self.voice_channel.id]["text_channel"]
        text_channel = interaction.guild.get_channel(text_channel_id)

        if text_channel is None:
            await interaction.followup.send("❌ Nie znaleziono kanału tekstowego.", ephemeral=True)
            return

        # 1. Zmiana właściciela w pamięci bota
        temp_channels[self.voice_channel.id]["owner"] = new_owner.id

        # 2. Aktualizacja uprawnień do kanału tekstowego (stary traci, nowy zyskuje)
        if old_owner:
            await text_channel.set_permissions(old_owner, overwrite=None)

        await text_channel.set_permissions(
            new_owner,
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )

        # 3. Odświeżenie embedu w panelu zarządczym
        try:
            panel_message_id = temp_channels[self.voice_channel.id]["panel_message"]
            panel_message = await text_channel.fetch_message(panel_message_id)

            embed = discord.Embed(
                title="🎛 Zarządzanie kanałem",
                description="Użyj przycisków poniżej, aby zarządzać swoim kanałem.",
                color=discord.Color.green()
            )
            embed.add_field(name="👑 Właściciel", value=new_owner.mention, inline=False)

            await panel_message.edit(embed=embed)
        except Exception:
            pass
        
        await interaction.followup.send(
            f"👑 Właścicielem kanału został {new_owner.mention}.",
            ephemeral=True
        )
