import discord
from discord.ext import commands

from .data import temp_channels
from .views import TempVoicePanel

CREATE_CHANNEL_ID = 1521930171353923787

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # 1. Tworzenie kanału
        if after.channel and after.channel.id == CREATE_CHANNEL_ID:
            category = after.channel.category

            # Kanał głosowy
            voice_channel = await category.create_voice_channel(
                name=f"🎤 {member.display_name}"
            )

            # Uprawnienia kanału tekstowego
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                ),
                member: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),
                member.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            }

            # Kanał tekstowy
            text_channel = await category.create_text_channel(
                name=f"🎛-{member.name.lower()}",
                overwrites=overwrites
            )

            # Zapamiętanie danych
            temp_channels[voice_channel.id] = {
                "owner": member.id,
                "banned": set(),
                "text_channel": text_channel.id
            }

            # Przeniesienie użytkownika
            await member.move_to(voice_channel)

            # Panel
            embed = discord.Embed(
                title="🎛 Zarządzanie kanałem",
                description="Użyj przycisków poniżej, aby zarządzać swoim kanałem.",
                color=discord.Color.green()
            )

            embed.add_field(
                name="👑 Właściciel",
                value=member.mention,
                inline=False
            )

            panel_message = await text_channel.send(
                embed=embed,
                view=TempVoicePanel(
                    voice_channel.id,
                    text_channel.id,
                    member.id
                )
            )
            
            temp_channels[voice_channel.id]["panel_message"] = panel_message.id

        # 2. Automatyczne przekazanie właściciela
        if before.channel and before.channel.id in temp_channels:
            channel_data = temp_channels[before.channel.id]

            # Czy z kanału wyszedł właściciel i czy ktoś jeszcze został na kanale?
            if member.id == channel_data["owner"] and len(before.channel.members) > 0:
                new_owner = before.channel.members[0]
                old_owner_id = channel_data["owner"]
                
                # Zmień właściciela w pamięci
                channel_data["owner"] = new_owner.id
        
                text_channel = member.guild.get_channel(channel_data["text_channel"])
        
                if text_channel:
                    old_owner = member.guild.get_member(old_owner_id)
        
                    if old_owner:
                        await text_channel.set_permissions(
                            old_owner,
                            overwrite=None
                        )
        
                    await text_channel.set_permissions(
                        new_owner,
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True
                    )
        
                    # Zmień nazwę kanałów (głosowy i tekstowy)
                    try:
                        await before.channel.edit(
                            name=f"🎤 {new_owner.display_name}"
                        )
                    
                        await text_channel.edit(
                            name=f"🎛-{new_owner.name.lower()}"
                        )
                    except discord.Forbidden:
                        pass
        
                    # Zaktualizuj panel
                    try:
                        panel_message = await text_channel.fetch_message(
                            channel_data["panel_message"]
                        )
            
                        embed = discord.Embed(
                            title="🎛 Zarządzanie kanałem",
                            description="Użyj przycisków poniżej, aby zarządzać swoim kanałem.",
                            color=discord.Color.green()
                        )
            
                        embed.add_field(
                            name="👑 Właściciel",
                            value=new_owner.mention,
                            inline=False
                        )
            
                        # Usuń stary panel
                        await panel_message.delete()
                    
                        # Wyślij nowy panel
                        new_panel = await text_channel.send(
                            embed=embed,
                            view=TempVoicePanel(
                                before.channel.id,
                                text_channel.id,
                                new_owner.id
                            )
                        )
                    
                        # Zapisz ID nowego panelu
                        channel_data["panel_message"] = new_panel.id
                    
                    except (discord.NotFound, discord.Forbidden):
                        pass
        
        # 3. Usuwanie kanału
        if before.channel and before.channel.id in temp_channels:
            if len(before.channel.members) == 0:
                text_channel_id = temp_channels[before.channel.id]["text_channel"]
                text_channel = member.guild.get_channel(text_channel_id)

                if text_channel:
                    await text_channel.delete()

                del temp_channels[before.channel.id]
                await before.channel.delete()

async def setup(bot):
    await bot.add_cog(TempVoice(bot))
