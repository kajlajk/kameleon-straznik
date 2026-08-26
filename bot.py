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
SZUKAM_CHANNEL = 1515570301172449362        # Kanał "Szukam do gry"
SZUKAM_ZNAJOMYCH_CHANNEL = 1538598497132089485 # Kanał "Szukam znajomych"

# PODMIEŃ TO NA ID ROLI, KTÓRĄ BOT MA PINGOWAĆ:
ROLE_SZUKAM_DO_GRY_ID = 1515875177852833872

CHAT_CHANNEL = 1515567593694691413
ADMIN_CHANNEL = 1515593063639285810
SCREENY_CHANNEL = 1515570115515650068  
LOG_CHANNEL_ID = 1521585275229442178

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

# --- KLASY INTERFEJSU DLA OGŁOSZEŃ ---

class EditPostModal(discord.ui.Modal, title="Edycja ogłoszenia"):
    def __init__(self, target_message: discord.Message):
        super().__init__()
        self.target_message = target_message
        
        current_text = ""
        if self.target_message.embeds:
            current_text = self.target_message.embeds[0].description or ""

        self.new_content = discord.ui.TextInput(
            label="Nowa treść ogłoszenia",
            style=discord.TextStyle.paragraph,
            default=current_text,
            max_length=2000,
            required=True
        )
        self.add_item(self.new_content)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = self.target_message.embeds[0]
            embed.description = self.new_content.value
            embed.timestamp = datetime.now(timezone.utc)
            
            await self.target_message.edit(embed=embed)
            await interaction.response.send_message("✅ Pomyślnie zaktualizowano Twoje ogłoszenie!", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ Nie znaleziono oryginalnego ogłoszenia.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Wystąpił błąd podczas edycji: {e}", ephemeral=True)

class PostView(discord.ui.View):
    def __init__(self, post_message: discord.Message, author_id: int):
        super().__init__(timeout=None)
        self.post_message = post_message
        self.author_id = author_id

    @discord.ui.button(label="✏️ Edytuj treść", style=discord.ButtonStyle.primary)
    async def edit_post(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Tylko autor ogłoszenia może je edytować!", ephemeral=True)
            
        await interaction.response.send_modal(EditPostModal(self.post_message))

    @discord.ui.button(label="🗑️ Usuń ogłoszenie", style=discord.ButtonStyle.danger)
    async def delete_post(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Tylko autor ogłoszenia może je usunąć!", ephemeral=True)
            
        try:
            await self.post_message.delete()
            await interaction.response.send_message("🗑️ Ogłoszenie zostało pomyślnie usunięte.", ephemeral=True)
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
        except discord.NotFound:
            await interaction.response.send_message("ℹ️ Ogłoszenie zostało już wcześniej usunięte.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Nie udało się usunąć ogłoszenia: {e}", ephemeral=True)


@bot.event
async def on_ready():
    print("BOT ONLINE TEST OK")
    print("NOWA WERSJA BOTA")
    print(f"Zalogowano jako {bot.user}")

    if not check_timeouts.is_running():
        check_timeouts.start()
        
    if not update_member_status.is_running():
        update_member_status.start()

    if not bump_timer_check.is_running():
        bump_timer_check.start()


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

                    print(f"[LEVEL] Nick z wiadomości: {nick}")
                    print(f"[LEVEL] Poziom: {level}")

                    member = discord.utils.find(
                        lambda m:
                        m.display_name.lower() == nick.lower()
                        or m.name.lower() == nick.lower(),
                        message.guild.members
                    )

                    if member is None:
                        print("[LEVEL] Nie znaleziono użytkownika.")
                        return

                    print(f"[LEVEL] Znaleziono: {member}")

                    role = message.guild.get_role(LEVEL_ROLE_ID)

                    if role not in member.roles:
                        print("[LEVEL] Użytkownik nie ma roli Levele.")
                        return

                    level_int = int(level)

                    if level_int in level_rewards:
                        await message.channel.send(
                            f"🎉 Gratulacje {member.mention}!\n\n"
                            f"Właśnie zdobyłeś **{level_int} poziom** i odblokowałeś rangę **{level_rewards[level_int]}**! 🏆"
                        )
                    else:
                        if random.randint(1, 100) <= 5:
                            tekst = random.choice(rare_level_messages)
                        else:
                            tekst = random.choice(level_messages)

                        await message.channel.send(
                            tekst.format(
                                mention=member.mention,
                                level=level_int
                            )
                        )

            except Exception as e:
                print(f"[LEVEL] Błąd: {e}")

        return

    # --- OBSŁUGA KANAŁÓW: SZUKAM DO GRY & SZUKAM ZNAJOMYCH ---
    if message.channel.id in (SZUKAM_CHANNEL, SZUKAM_ZNAJOMYCH_CHANNEL):
        content_lower = message.content.lower()

        if "#szukam do gry" in content_lower or "#szukamdogry" in content_lower:
            now = time.time()
            user_id = message.author.id
            cooldown_key = (user_id, message.channel.id)
            
            # Cooldown 1 godzina (3600s)
            if cooldown_key in post_cooldowns:
                elapsed = now - post_cooldowns[cooldown_key]
                if elapsed < 3600:
                    remaining_minutes = int((3600 - elapsed) // 60) + 1
                    try:
                        await message.delete()
                        await message.author.send(
                            f"⏳ Na kanale {message.channel.mention} możesz dodawać nowe ogłoszenie raz na **1 godzinę**.\n"
                            f"Musisz poczekać jeszcze około **{remaining_minutes} min**.\n"
                            "💡 *Pamiętaj, że istniejące ogłoszenie możesz edytować z poziomu wiadomości od bota!*"
                        )
                    except discord.Forbidden:
                        pass
                    return

            try:
                # Oczyszczanie wiadomości z komendy
                clean_content = re.sub(r'#szukam\s*do\s*gry', '', message.content, flags=re.IGNORECASE).strip()
                if not clean_content:
                    clean_content = message.content

                author = message.author
                await message.delete()
                post_cooldowns[cooldown_key] = now

                # Tworzenie pingu dla roli i gracza
                if message.channel.id == SZUKAM_CHANNEL:
                    embed_color = discord.Color.purple()
                    embed_title = f"🎮 Ogłoszenie gracza: {author.display_name}"
                    ping_content = f"<@&{ROLE_SZUKAM_DO_GRY_ID}> {author.mention}"
                else:
                    embed_color = discord.Color.teal()
                    embed_title = f"✨ Wizytówka: {author.display_name}"
                    ping_content = author.mention

                embed = discord.Embed(
                    description=clean_content,
                    color=embed_color,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_author(
                    name=embed_title,
                    icon_url=author.display_avatar.url if author.display_avatar else None
                )
                embed.set_thumbnail(url=author.display_avatar.url if author.display_avatar else None)
                embed.set_footer(text=f"ID Użytkownika: {author.id}")

                # Wysyłanie panelu z pingiem roli
                sent_message = await message.channel.send(content=ping_content, embed=embed)

                dm_embed = discord.Embed(
                    title="🚀 Twoje ogłoszenie zostało opublikowane!",
                    description=(
                        f"Twoja treść trafiła na kanał {message.channel.mention}.\n\n"
                        "Poniżej znajdziesz przyciski pozwalające Ci **edytować** treść ogłoszenia lub je **usunąć**."
                    ),
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="📝 Aktualna treść:", value=clean_content[:1024], inline=False)

                view = PostView(post_message=sent_message, author_id=author.id)
                
                try:
                    await author.send(embed=dm_embed, view=view)
                except discord.Forbidden:
                    pass

            except Exception as e:
                print(f"[BŁĄD OGŁOSZEŃ]: {e}")
            return

    # Przypomnienie o bumpie po aktywności
    if message.channel.id == CHAT_CHANNEL and bump_pending:
        try:
            embed = discord.Embed(
                title="🚀 Przypomnienie o podbijaniu serwera!",
                description=(
                    "Pamiętajcie o wsparciu naszego serwera! Podbij go wpisując komendę:\n\n"
                    "👉 **`/bump`** od bota **Dzik** na kanale dla botów!"
                ),
                color=discord.Color.og_blurple()
            )
            embed.set_footer(text="KameleonBot • Przypomnienie co 3h", icon_url=bot.user.display_avatar.url)
            embed.timestamp = datetime.now(timezone.utc)

            await message.channel.send(embed=embed)
            print("[BUMP] Wysłano przypomnienie o bumpie po aktywności użytkownika.")
            
            bump_pending = False
            last_bump_time = time.time()
        except Exception as e:
            print(f"[BŁĄD BUMP SEND]: {e}")

    if message.channel.id == SCREENY_CHANNEL:
        content = message.content.lower()

        media = (
            len(message.attachments) > 0
            or "medal.tv" in content
            or "medal.com" in content
            or "youtu.be" in content
            or "youtube.com" in content
            or "clips.twitch.tv" in content
            or "tiktok.com" in content
            or "streamable.com" in content
        )

        if media:
            try:
                await message.add_reaction("👍")
                await message.add_reaction("😂")
                await message.add_reaction("❤️")
            except (discord.Forbidden, discord.HTTPException):
                pass

    global last_random_message
    global answered_users
    global last_reply_text

    now = time.time()

    if (
        message.channel.id == CHAT_CHANNEL
        and now - last_random_message > 3600
        and random.randint(1, 100) <= 10
    ):
        bot_msg = await message.channel.send(
            random.choice(random_texts)
        )

        last_bot_message_id = bot_msg.id
        answered_users.clear()
        last_random_message = now

    if message.reference and message.channel.id == CHAT_CHANNEL:   
        try:
            replied_message = await message.channel.fetch_message(
                message.reference.message_id
            )

            if replied_message.author.id == bot.user.id:
                if message.author.id not in answered_users:
                    response = random.choice(reply_texts)

                    if len(reply_texts) > 1:
                        while (
                            last_reply_text is not None
                            and response == last_reply_text
                        ):
                            response = random.choice(reply_texts)

                    await message.reply(response)

                    last_reply_text = response
                    answered_users.add(message.author.id)

        except Exception as e:
            print(f"Błąd odpowiedzi: {e}")   

    if message.content.lower() == "/spokojnie":
        if (
            message.author.id == OWNER_ID
            and message.channel.id == ADMIN_CHANNEL
        ):
            channel = bot.get_channel(CHAT_CHANNEL)

            teksty = [
                "🤖 Materiał dowodowy sam się nie zbierze.",
                "🤖 Proszę kontynuować, raport nie napisze się sam.",
                "🤖 Administracja z zainteresowaniem śledzi rozwój wydarzeń.",
                "🤖 Nie przerywajcie, fabuła się zagęszcza.",
                "🤖 Spokojnie, wszystko trafia do akt.",
                "🤖 To będzie ciekawy wpis w raporcie.",
                "🤖 Obserwuję i udaję, że mnie tu nie ma.",
                "🤖 Interesujący obrót wydarzeń.",
                "🤖 Ktoś tu gotuje i zaczyna pachnieć dramatem.",
                "🤖 Raport sytuacyjny został zaktualizowany.",
                "🤖 Poproszę streszczenie dla spóźnionych.",
                "🤖 Nie mam kontekstu, ale brzmi poważnie.",
                "🤖 Ten czat ma potencjał.",
                "🤖 Zdecydowanie jedna z rozmów wszech czasów.",
                "🤖 Kulturalnie przypominam, że czytam.",
                "🤖 Właśnie wszedłem. Co się tu dzieje?",
                "🤖 Dokumentacja sama się nie uzupełni.",
                "🤖 Obywatelu, kontynuuj wypowiedź.",
                "🤖 To może być ważne dla śledztwa.",
                "🤖 Zbieram materiał do raportu.",
                "🤖 Ciekawa ta wasza rozmowa.",
                "🤖 Notuję. Bardzo skrupulatnie notuję.",
                "🤖 Emocje wykryte. Analizuję sytuację.",
                "🤖 To będzie długi raport.",
                "🤖 System monitoringu czatu działa prawidłowo.",
                "🤖 Administratorzy siedzą z popcornem. 🍿",
                "🤖 Speedrun do ciekawa wpisu w logach.",
                "🤖 Wykryto nietypową aktywność użytkowników.",
                "🤖 Kontynuujcie, jestem zaintrygowany.",
                "🤖 Kameleon nie ocenia. Kameleon obserwuje. 🦎",
                "🤖 Wykryto podwyższone tętno sekcji tekstowej. Monitoruję.",
                "🤖 Analiza nastrojów... zalecane ochłodzenie emocji.",
                "🤖 Czytanie tego wątku wymaga ode mnie restartu procesora.",
                "🤖 Uwaga: Logi systemowe zapełniają się w zastraszającym tempie.",
                "🤖 Wpis w kartotece: 'Brak panowania nad klawiaturą'.",
                "🤖 Ciekawy dobór słów. Moderatorzy na pewno to docenią.",
                "🤖 Spokojnie, po prostu robię zrzuty ekranu.",
                "🤖 Ktoś tu bardzo chce przetestować system automatycznych kar.",
                "🤖 Nie przeszkadzajcie sobie, algorytm bacznie notuje każde słowo.",
                "🤖 Oho, widzę, że regulamin znowu stał się tylko sugestią.",
                "🤖 Sprawa jest rozwojowa. Czekam na dalsze zeznania.",
                "🤖 Dział skarg i zażaleń bota jest aktualnie nieczynny.",
                "🤖 Temperatura dyskusji przekracza normy fabryczne.",
                "🤖 Człowieku, nie denerwuj maszyny.",
                "🤖 Zgłoszenie przyjęte. Trwa przetwarzanie winowajców..."
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
            await message.author.send(
                "Możesz oznaczyć maksymalnie 3 osoby w jednej wiadomości."
            )
        except Exception:
            pass
        return

    await bot.process_commands(message)


@tasks.loop(seconds=5)
async def check_timeouts():
    global last_timeout_entry

    try:
        if not bot.guilds:
            return

        guild = bot.guilds[0]
        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if log_channel is None:
            return

        if last_timeout_entry is None:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                last_timeout_entry = entry.id
            return

        actions = []
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
            if entry.id == last_timeout_entry:
                break
            actions.append(entry)

        if not actions:
            return

        last_timeout_entry = actions[0].id

        for entry in reversed(actions):
            before_timeout = entry.before.timed_out_until
            after_timeout = entry.after.timed_out_until

            if before_timeout == after_timeout:
                continue

            moderator = entry.user
            user = entry.target
            reason = entry.reason or "Brak powodu"
            avatar_url = user.display_avatar.url if user.display_avatar else None

            if after_timeout is None:
                embed = discord.Embed(
                    title="🔓 Zdjęto timeout",
                    color=discord.Color.green()
                )

                if avatar_url:
                    embed.set_author(name=str(user), icon_url=avatar_url)

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
            
                embed = discord.Embed(
                    title="🔇 Nadano timeout",
                    color=discord.Color.orange()
                )

                if avatar_url:
                    embed.set_author(name=str(user), icon_url=avatar_url)

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
        if not bot.guilds:
            return
            
        guild = bot.guilds[0]
        member_count = guild.member_count
        
        activity = discord.CustomActivity(
            name=f"🛡️ Pilnuje: {member_count} użytkowników 🦎"
        )
        
        await bot.change_presence(activity=activity)
        print(f"[STATUS] Zaktualizowano liczbę członków serwera: {member_count}")
        
    except Exception as e:
        print(f"[BŁĄD MEMBER STATUS LOOP]: {e}")


@tasks.loop(minutes=1)
async def bump_timer_check():
    global bump_pending, last_bump_time
    try:
        if not bump_pending:
            if time.time() - last_bump_time >= 10800:
                bump_pending = True
                print("[BUMP] Minęły 3 godziny. Oczekiwanie na aktywność użytkownika...")
    except Exception as e:
        print(f"[BŁĄD BUMP TIMER LOOP]: {e}")


async def main():
    async with bot:
        await bot.load_extension("tempvoice.manager")
        await bot.start(TOKEN)

asyncio.run(main())
