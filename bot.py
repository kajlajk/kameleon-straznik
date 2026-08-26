import discord
from discord.ext import commands
import os
import asyncio
import time
import random 
import re
from datetime import timedelta, datetime, timezone
from discord.ext import tasks

TOKEN = os.getenv("TOKEN")

OWNER_ID = 765301434350567426
SZUKAM_CHANNEL = 1515570301172449362        
SZUKAM_ZNAJOMYCH_CHANNEL = 1538598497132089485 
ROLE_SZUKAM_DO_GRY_ID = 1515875177852833872 

CHAT_CHANNEL = 1515567593694691413
ADMIN_CHANNEL = 1515593063639285810
SCREENY_CHANNEL = 1515570115515650068  
LOG_CHANNEL_ID = 1521585275229442178
INFO_CHANNEL_ID = 1542093397593030747

STARTIT_BOT_ID = 572906387382861835
LEVEL_ROLE_ID = 1519678728438026321

post_cooldowns = {} 

warnings = {}
last_random_message = 0
answered_users = set()
last_reply_text = None
last_timeout_entry = None

bump_pending = False
last_bump_time = time.time()

level_messages = [
    "🎉 Gratulacje {mention} za zdobycie **{level} poziomu!** 🦎",
    "⭐ Brawo {mention}! Właśnie osiągnąłeś **{level} poziom**!",
    "🔥 Świetna robota {mention}! Kolejny poziom zdobyty!",
    "🎊 {mention}, gratulacje! Już **{level} poziom**! Tak trzymaj!",
    "💚 Kameleon jest z Ciebie dumny, {mention}! Wbiłeś **{level} poziom**!",
    "🚀 {mention}, wskakujesz na **{level} poziom**! Gratulacje!",
    "🏆 Brawo {mention}! Zdobyłeś **{level} poziom**!",
    "✨ {mention}, kolejny level za Tobą! Gratulacje!",
    "🎯 Świetna robota {mention}! Osiągnąłeś **{level} poziom**!"
]

rare_level_messages = [
    "👑 **LEGENDARNE!** {mention} właśnie zdobył **{level} poziom**! 🎉",
    "🌟 **Ale sztos!** {mention} awansował na **{level} poziom**!",
    "⚡ **Kameleon jest pod ogromnym wrażeniem!** {mention} osiągnął **{level} poziom**!",
    "💎 **Wyjątkowy moment!** {mention} właśnie wbił **{level} poziom**! 🚀",
    "🔥 **To trzeba uczcić!** {mention} zdobył **{level} poziom**! 🥳"
]

level_rewards = {
    10: "🦎 Aktywny Kameleon",
    25: "🐉 Doświadczony Kameleon",
    55: "🦚 Mistrz Kamuflażu",
    80: "👑 Król Kamuflażu",
    120: "🏆 Legenda MECCHA"
}

random_texts = [
    "🦎 Kameleon obserwuje sytuację...",
    "☕ Ciężka ta praca robota.",
    "🛡️ Wszystko pod kontrolą.",
    "👀 Widzę was.",
    "🌡️ Temperatura czatu w normie.",
    "📡 Skanuję serwer...",
    "😴 Chwila spokoju? Podejrzane.",
    "🦎 Kameleon melduje gotowość.",
    "🍃 Pamiętajcie o kulturze rozmowy.",
    "🤔 Ciekawe kto pierwszy napisze na czacie.",
    "🔍 Logi czyste. Przynajmniej na razie.",
    "💾 Zapisywanie stanu serwera... Gotowe.",
    "🧯 W razie dramy, gaśnica jest pod ręką.",
    "📝 Protokół spokoju: aktywny.",
    "🦎 Kameleon wtopił się w tło, piszcie śmiało.",
    "🔋 Baterie naładowane na 100%. Mogę moderować.",
    "☁️ Przelotne opady spamu niewykryte.",
    "🕵️‍♂️ Rutynowa kontrola wątków. Nic tu nie ma.",
    "☕ Ktoś stawia kawę dla bota?"
]

reply_texts = [
    "🦎 Trochę kultury.",
    "👀 To moja praca.",
    "🛡️ Patrol trwa.",
    "☕ Nie przeszkadzaj w pracy.",
    "📋 To trafi do raportu.",
    "🚨 Spokojnie, bohaterze.",
    "🦎 Kameleon wszystko widzi.",
    "🤨 Odważne słowa.",
    "🍃 Zachowaj spokój.",
    "📡 Sygnał odebrany.",
    "👀 Obserwuję sytuację.",
    "🛡️ Wszystko pod kontrolą.",
    "😎 Bez paniki.",
    "📋 Zanotowano.",
    "🚔 Kontynuuj, słucham.",
    "🤨 Aha Gratulacje, wygrywasz bana.",
    "👁️ Widzę, słyszę, nie komentuję.",
    "🤖 Procedury bezpieczeństwa zachowane.",
    "📁 Dodano do bazy danych.",
    "🤷 I co w związku z tym?",
    "⏳ Czas ucieka, a ty dalej tutaj.",
    "🤐 No i po co te nerwy?",
    "🥱 Standardowa odpowiedź dla standardowego użytkownika.",
    "🔋 Poziom mojej uwagi: niski.",
    "🗺️ Przeskanowano teren. Bez zmian.",
    "📝 Kolejny wpis do pamiętnika bota.",
    "🛑 Nic dodać, nic ująć.",
    "🧠 Analizuję poziom tego wątku...",
    "🔍 Wynik analizy: brak argumentów.",
    "🧯 Potrzebna gaśnica do tego pożaru?",
    "🎭 Piękny występ, ale kurtyna opada."
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- KLASY INTERFEJSU OGŁOSZEŃ ---

class EditAdvancedPostModal(discord.ui.Modal, title="Edycja Ogłoszenia"):
    def __init__(self, target_message: discord.Message):
        super().__init__()
        self.target_message = target_message

        embed = self.target_message.embeds[0] if self.target_message.embeds else None
        
        current_desc = ""
        is_profile = False
        current_game = "Gry / Wspólnej zabawy"

        if embed:
            if embed.title and "Wizytówka" in embed.title:
                is_profile = True
            elif embed.title and "Szukamy graczy do" in embed.title:
                current_game = embed.title.replace("🎮 Szukamy graczy do ", "").replace("!", "").strip()

            for field in embed.fields:
                if field.name == "📝 Opis":
                    current_desc = field.value
                    break

        self.is_profile = is_profile

        if not self.is_profile:
            self.game_name = discord.ui.TextInput(
                label="Na co zapraszasz? (Nazwa gry/aktywności)",
                style=discord.TextStyle.short,
                default=current_game,
                max_length=100,
                required=True
            )
            self.add_item(self.game_name)

        self.new_content = discord.ui.TextInput(
            label="Opis wizytówki / ogłoszenia",
            style=discord.TextStyle.paragraph,
            default=current_desc,
            max_length=1000,
            required=False
        )
        self.add_item(self.new_content)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = self.target_message.embeds[0]
            if not self.is_profile:
                embed.title = f"🎮 Szukamy graczy do {self.game_name.value}!"
            
            embed.timestamp = datetime.now(timezone.utc)
            new_desc_value = self.new_content.value if self.new_content.value else "*Brak opisu.*"
            
            description_updated = False
            for i, field in enumerate(embed.fields):
                if field.name == "📝 Opis":
                    embed.set_field_at(i, name="📝 Opis", value=new_desc_value, inline=False)
                    description_updated = True
                    break
            
            if not description_updated:
                embed.add_field(name="📝 Opis", value=new_desc_value, inline=False)

            await self.target_message.edit(embed=embed)
            await interaction.response.send_message("✅ Pomyślnie zaktualizowano!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd podczas edycji: {e}", ephemeral=True)

class AdvancedPostView(discord.ui.View):
    def __init__(self, author_id: int, voice_channel_url: str = None):
        super().__init__(timeout=None)
        self.author_id = author_id

        if voice_channel_url:
            self.add_item(discord.ui.Button(
                label="🔊 Dołącz do kanału głosowego",
                style=discord.ButtonStyle.link,
                url=voice_channel_url
            ))

    @discord.ui.button(label="✏️ Edytuj opis / grę", style=discord.ButtonStyle.secondary)
    async def edit_post(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Tylko autor może to edytować!", ephemeral=True)

        await interaction.response.send_modal(EditAdvancedPostModal(interaction.message))

    @discord.ui.button(label="🗑️ Usuń", style=discord.ButtonStyle.danger)
    async def delete_post(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Tylko autor może to usunąć!", ephemeral=True)

        await interaction.message.delete()


@bot.event
async def on_ready():
    print("BOT ONLINE TEST OK")
    print(f"Zalogowano jako {bot.user}")

    if not check_timeouts.is_running(): check_timeouts.start()
    if not update_member_status.is_running(): update_member_status.start()
    if not bump_timer_check.is_running(): bump_timer_check.start()
    if not cycle_info_channel.is_running(): cycle_info_channel.start()


@bot.event
async def on_message(message):
    global bump_pending, last_bump_time

    if message.author.bot:
        if message.author.id == STARTIT_BOT_ID:
            try:
                if "zdobył(a)" in message.content:
                    tekst = message.content.split("siłę!")[1].strip()
                    nick = tekst.split("zdobył(a)")[0].strip()
                    level = tekst.split("zdobył(a)")[1].split("poziom")[0].strip()

                    member = discord.utils.find(
                        lambda m: m.display_name.lower() == nick.lower() or m.name.lower() == nick.lower(),
                        message.guild.members
                    )
                    if member is None: return

                    role = message.guild.get_role(LEVEL_ROLE_ID)
                    if role not in member.roles: return

                    level_int = int(level)

                    if level_int in level_rewards:
                        await message.channel.send(
                            f"🎉 Gratulacje {member.mention}!\n\n"
                            f"Właśnie zdobyłeś **{level_int} poziom** i odblokowałeś rangę **{level_rewards[level_int]}**! 🏆"
                        )
                    else:
                        if random.randint(1, 100) <= 5: tekst = random.choice(rare_level_messages)
                        else: tekst = random.choice(level_messages)
                        await message.channel.send(tekst.format(mention=member.mention, level=level_int))
            except Exception as e:
                print(f"[LEVEL] Błąd: {e}")
        return

    # --- KANAŁY OGŁOSZEŃ ---
    if message.channel.id in (SZUKAM_CHANNEL, SZUKAM_ZNAJOMYCH_CHANNEL):
        content_lower = message.content.lower()
        
        has_role_ping = len(message.role_mentions) > 0
        has_hashtag = "#szukam do gry" in content_lower or "#szukamdogry" in content_lower
        is_znajomi_channel = message.channel.id == SZUKAM_ZNAJOMYCH_CHANNEL

        if is_znajomi_channel or has_role_ping or has_hashtag:
            now = time.time()
            user_id = message.author.id
            cooldown_key = (user_id, message.channel.id)
            
            # Cooldown 1 godzina
            if cooldown_key in post_cooldowns:
                elapsed = now - post_cooldowns[cooldown_key]
                if elapsed < 3600:
                    remaining_minutes = int((3600 - elapsed) // 60) + 1
                    try:
                        await message.delete()
                        await message.author.send(
                            f"⏳ Na kanale {message.channel.mention} możesz dodawać nowe ogłoszenie raz na **1 godzinę**.\n"
                            f"Musisz poczekać jeszcze około **{remaining_minutes} min**."
                        )
                    except discord.Forbidden:
                        pass
                    return

            try:
                author = message.author
                target_role = message.role_mentions[0] if message.role_mentions else None

                clean_content = re.sub(r'#szukam\s*do\s*gry|#szukamdogry', '', message.content, flags=re.IGNORECASE).strip()
                if target_role:
                    clean_content = clean_content.replace(target_role.mention, '').strip()

                await message.delete()
                post_cooldowns[cooldown_key] = now

                # --- KANAŁ 1: SZUKAM ZNAJOMYCH (CZYSTA WIZYTÓWKA) ---
                if is_znajomi_channel:
                    ping_text = author.mention
                    if not clean_content:
                        clean_content = "Hej, szukam kogoś do pogadania i wspólnego spędzania czasu!"

                    embed = discord.Embed(
                        title=f"✨ Wizytówka: {author.display_name}",
                        description=f"{author.mention}",
                        color=discord.Color.teal(),
                        timestamp=datetime.now(timezone.utc)
                    )

                    embed.set_author(
                        name=f"Wiadomość od {author.display_name}",
                        icon_url=author.display_avatar.url if author.display_avatar else None
                    )
                    embed.set_thumbnail(url=author.display_avatar.url if author.display_avatar else None)
                    embed.add_field(name="📝 Opis", value=clean_content, inline=False)
                    embed.set_footer(text="Kliknij przycisk poniżej, aby edytować wizytówkę!")

                    view = AdvancedPostView(author_id=author.id)
                    await message.channel.send(content=ping_text, embed=embed, view=view)

                # --- KANAŁ 2: SZUKAM DO GRY (Z LOBBY I ROLAMI) ---
                else:
                    if target_role:
                        ping_text = f"{target_role.mention} {author.mention}"
                        game_title = re.sub(r'<[^>]+>', '', target_role.name).strip()
                    else:
                        default_role = message.guild.get_role(ROLE_SZUKAM_DO_GRY_ID)
                        ping_text = f"{default_role.mention} {author.mention}" if default_role else author.mention
                        game_title = "Gry"

                    if not clean_content:
                        clean_content = "Hej, szukam kogoś do pogadania i wspólnego spędzania czasu!"

                    voice_state = author.voice
                    if voice_state and voice_state.channel:
                        voice_channel_name = f"🎙️ {voice_state.channel.name}"
                        user_limit = voice_state.channel.user_limit
                        current_users = len(voice_state.channel.members)
                        
                        osoby_text = "osoba" if current_users == 1 else "osoby" if 2 <= current_users <= 4 else "osób"
                        lobby_status = f"{current_users}/{user_limit} {osoby_text}" if user_limit > 0 else f"{current_users} {osoby_text}"
                        vc_url = f"https://discord.com/channels/{message.guild.id}/{voice_state.channel.id}"
                    else:
                        voice_channel_name = "🎙️ Brak kanału"
                        lobby_status = "Brak informacji"
                        vc_url = None

                    embed = discord.Embed(
                        title=f"🎮 {game_title}!",
                        description=f"{author.mention} szuka osób i zaprasza na kanał!",
                        color=discord.Color.red(),
                        timestamp=datetime.now(timezone.utc)
                    )

                    embed.set_author(
                        name=f"Zaproszenie od {author.display_name}",
                        icon_url=author.display_avatar.url if author.display_avatar else None
                    )
                    embed.set_thumbnail(url=author.display_avatar.url if author.display_avatar else None)

                    embed.add_field(name="📝 Opis", value=clean_content, inline=False)
                    embed.add_field(name="📌 Rola", value=target_role.mention if target_role else "Brak", inline=True)
                    embed.add_field(name="Kanał głosowy", value=voice_channel_name, inline=True)
                    embed.add_field(name="👥 Status lobby", value=lobby_status, inline=False)

                    embed.set_footer(text="Kliknij przycisk poniżej, aby dołączyć do kanału lub edytować ogłoszenie!")

                    view = AdvancedPostView(author_id=author.id, voice_channel_url=vc_url)
                    await message.channel.send(content=ping_text, embed=embed, view=view)

            except Exception as e:
                print(f"[BŁĄD OGŁOSZEŃ]: {e}")
            return

    if message.channel.id == CHAT_CHANNEL and bump_pending:
        try:
            embed = discord.Embed(
                title="🚀 Przypomnienie o podbijaniu serwera!",
                description="Pamiętajcie o wsparciu naszego serwera! Podbij go wpisując komendę:\n\n👉 **`/bump`** od bota **Dzik** na kanale dla botów!",
                color=discord.Color.og_blurple()
            )
            embed.set_footer(text="KameleonBot • Przypomnienie co 3h", icon_url=bot.user.display_avatar.url)
            embed.timestamp = datetime.now(timezone.utc)

            await message.channel.send(embed=embed)
            bump_pending = False
            last_bump_time = time.time()
        except Exception as e:
            print(f"[BŁĄD BUMP SEND]: {e}")

    if message.channel.id == SCREENY_CHANNEL:
        content = message.content.lower()
        media = (
            len(message.attachments) > 0
            or "medal.tv" in content or "medal.com" in content
            or "youtu.be" in content or "youtube.com" in content
            or "clips.twitch.tv" in content or "tiktok.com" in content or "streamable.com" in content
        )
        if media:
            try:
                await message.add_reaction("👍")
                await message.add_reaction("😂")
                await message.add_reaction("❤️")
            except:
                pass

    global last_random_message, answered_users, last_reply_text
    now = time.time()

    if (message.channel.id == CHAT_CHANNEL and now - last_random_message > 3600 and random.randint(1, 100) <= 10):
        bot_msg = await message.channel.send(random.choice(random_texts))
        last_bot_message_id = bot_msg.id
        answered_users.clear()
        last_random_message = now

    if message.reference and message.channel.id == CHAT_CHANNEL:   
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            if replied_message.author.id == bot.user.id:
                if message.author.id not in answered_users:
                    response = random.choice(reply_texts)
                    if len(reply_texts) > 1:
                        while (last_reply_text is not None and response == last_reply_text):
                            response = random.choice(reply_texts)
                    await message.reply(response)
                    last_reply_text = response
                    answered_users.add(message.author.id)
        except Exception as e:
            print(f"Błąd odpowiedzi: {e}")   

    if message.content.lower() == "/spokojnie":
        if (message.author.id == OWNER_ID and message.channel.id == ADMIN_CHANNEL):
            channel = bot.get_channel(CHAT_CHANNEL)
            teksty = [
                "🤖 Materiał dowodowy sam się nie zbierze.",
                "🤖 Proszę kontynuować, raport nie napisze się sam.",
                "🤖 Administracja z zainteresowaniem śledzi rozwój wydarzeń."
            ]
            try:
                await channel.send(random.choice(teksty))
                await message.delete()
            except Exception as e:
                print(f"Błąd komendy /spokojnie: {e}")
        return

    if len(message.mentions) > 3 and message.author.id != OWNER_ID:
        try:
            await message.delete()
            await message.author.send("Możesz oznaczyć maksymalnie 3 osoby w jednej wiadomości.")
        except Exception:
            pass
        return

    await bot.process_commands(message)


@tasks.loop(seconds=5)
async def check_timeouts():
    global last_timeout_entry
    try:
        if not bot.guilds: return
        guild = bot.guilds[0]
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel is None: return

        if last_timeout_entry is None:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                last_timeout_entry = entry.id
            return

        actions = []
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
            if entry.id == last_timeout_entry: break
            actions.append(entry)

        if not actions: return
        last_timeout_entry = actions[0].id

        for entry in reversed(actions):
            before_timeout = entry.before.timed_out_until
            after_timeout = entry.after.timed_out_until
            if before_timeout == after_timeout: continue

            moderator = entry.user
            user = entry.target
            reason = entry.reason or "Brak powodu"
            avatar_url = user.display_avatar.url if user.display_avatar else None

            if after_timeout is None:
                embed = discord.Embed(title="🔓 Zdjęto timeout", color=discord.Color.green())
                if avatar_url: embed.set_author(name=str(user), icon_url=avatar_url)
                embed.add_field(name="👤 Użytkownik", value=user.mention, inline=False)
                embed.add_field(name="🛡️ Moderator", value=moderator.mention, inline=False)
                embed.add_field(name="📝 Powód", value=reason, inline=False)
                embed.timestamp = datetime.now(timezone.utc)
                embed.set_footer(text=f"ID użytkownik: {user.id}")
                await log_channel.send(embed=embed)
            else:
                timestamp = int(after_timeout.timestamp())
                remaining = after_timeout - datetime.now(timezone.utc)
                seconds = int(remaining.total_seconds())
                
                if seconds <= 70: duration = "60 sekund"
                elif seconds <= 310: duration = "5 minut"
                elif seconds <= 610: duration = "10 minut"
                elif seconds <= 3610: duration = "1 godzina"
                elif seconds <= 86410: duration = "1 dzień"
                else: duration = "1 tydzień"
            
                embed = discord.Embed(title="🔇 Nadano timeout", color=discord.Color.orange())
                if avatar_url: embed.set_author(name=str(user), icon_url=avatar_url)
                embed.add_field(name="👤 Użytkownik", value=user.mention, inline=False)
                embed.add_field(name="🛡️ Pomocnik", value=moderator.mention, inline=False)
                embed.add_field(name="⏳ Czas", value=duration, inline=False)
                embed.add_field(name="🕒 Wygasa", value=f"<t:{timestamp}:F>", inline=False)
                embed.add_field(name="📝 Powód", value=reason, inline=False)
                embed.timestamp = datetime.now(timezone.utc)
                embed.set_footer(text=f"ID użytkownika: {user.id}")
                await log_channel.send(embed=embed)
    except Exception as e:
        print(f"[BŁĄD TIMEOUT LOOP]: {e}")


@tasks.loop(minutes=10)
async def update_member_status():
    try:
        if not bot.guilds: return
        guild = bot.guilds[0]
        member_count = guild.member_count
        activity = discord.CustomActivity(name=f"🛡️ Pilnuje: {member_count} użytkowników 🦎")
        await bot.change_presence(activity=activity)
    except Exception as e:
        pass


@tasks.loop(minutes=1)
async def bump_timer_check():
    global bump_pending, last_bump_time
    try:
        if not bump_pending:
            if time.time() - last_bump_time >= 10800:
                bump_pending = True
    except Exception as e:
        pass


@tasks.loop(minutes=8)
async def cycle_info_channel():
    try:
        if not bot.guilds: return
        guild = bot.guilds[0]
        channel = guild.get_channel(INFO_CHANNEL_ID)
        if not channel: return

        teksty = [
            "✨ Dodaj sobie Role!",
            "💚 Fajnie ze jestescie z nami",
            "💬 Miłego pisania na czacie!",
            "🦎 Kameleon Krewetka Pozdrawia"
        ]

        if not hasattr(bot, "info_index"):
            bot.info_index = 0

        napis = teksty[bot.info_index]
        
        if channel.name != napis:
            await channel.edit(name=napis)

        bot.info_index = (bot.info_index + 1) % len(teksty)

    except Exception as e:
        print(f"[BŁĄD KANAŁU INFO]: {e}")


async def main():
    async with bot:
        await bot.load_extension("tempvoice.manager")
        await bot.start(TOKEN)

asyncio.run(main())
