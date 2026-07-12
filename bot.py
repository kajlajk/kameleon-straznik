import discord
from discord.ext import commands
import os
import asyncio
import time
import random 
from datetime import timedelta, datetime, timezone
from discord.ext import tasks

TOKEN = os.getenv("TOKEN")

OWNER_ID = 765301434350567426
SZUKAM_CHANNEL = 1515570301172449362
CHAT_CHANNEL = 1515567593694691413
ADMIN_CHANNEL = 1515593063639285810
SCREENY_CHANNEL = 1515570115515650068  
LOG_CHANNEL_ID = 1521585275229442178

SZUKAM_ROLES_IDS = {
    1515875177852833872,  
    1523300055430332467,  
    1523305698031698153,  
    1523304847452143697,  
    1523305849009999993
}

STARTIT_BOT_ID = 572906387382861835
LEVEL_ROLE_ID = 1519678728438026321

channel_cooldowns = {}
warnings = {}
last_random_message = 0
answered_users = set()
last_reply_text = None
last_timeout_entry = None

level_messages = [
    "🎉 Gratulacje {mention} za zdobycie **{level} poziomu!** 🦎",
    "⭐ Brawo {mention}! Właśnie osiągnąłeś **{level} poziom**!",
    "🔥 Świetna robota {mention}! Kolejny poziom zdobyty!",
    "🎊 {mention}, gratulacje! Już **{level} poziom**! Tak timaj!",
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


@bot.event
async def on_ready():
    print("BOT ONLINE TEST OK")
    print("NOWA WERSJA BOTA")
    print(f"Zalogowano jako {bot.user}")

    # Uruchomienie pętli od timeoutów
    if not check_timeouts.is_running():
        check_timeouts.start()
        
    # URUCHOMIENIE NOWEJ PĘTLI STATUSU (Liczba osób na serwerze)
    if not update_member_status.is_running():
        update_member_status.start()
    

@bot.event
async def on_message(message):
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

    if message.reference:   
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

    if len(message.mentions) > 3:
        try:
            await message.delete()
            await message.author.send(
                "Możesz oznaczyć maksymalnie 3 osoby w jednej wiadomości."
            )
        except Exception:
            pass
        return

    role_pinged = any(role.id in SZUKAM_ROLES_IDS for role in message.role_mentions)
    
    if role_pinged:
        if message.channel.id != SZUKAM_CHANNEL:
            try:
                await message.delete()
                warnings[message.author.id] = warnings.get(message.author.id, 0) + 1
        
                if warnings[message.author.id] == 1:
                    await message.author.send(
                        f"{message.author.mention} Role z kategorii 'Szukam do gry' mogą być używane tylko na dedykowanym kanale Szukam do gry."
                    )
        
                elif warnings[message.author.id] == 2:
                    await message.author.timeout(
                        timedelta(minutes=20),
                        reason="Pingowanie roli Szukam do gry poza wyznaczonym kanałem"
                    )
        
                elif warnings[message.author.id] >= 3:
                    await message.author.timeout(
                        timedelta(hours=1),
                        reason="Wielokrotne pingowanie roli Szukam do gry poza wyznaczonym kanałem"
                    )
            except Exception as e:
                print(f"Błąd moderacji pingu roli: {e}")
        
            return

        if message.channel.id == SZUKAM_CHANNEL:
            if not message.author.voice:
                try:
                    await message.delete()
                    await message.author.send(
                        "Aby użyć roli Szukam do gry, musisz przebywać na kanale głosowym."
                    )
                except Exception:
                    pass
                return

            voice_channel = message.author.voice.channel
            now = time.time()

            if voice_channel.id in channel_cooldowns:
                if now - channel_cooldowns[voice_channel.id] < 1200:
                    try:
                        await message.delete()
                        await message.author.send(
                            "Ktoś z twojego kanału głosowego użył już roli Szukam do gry w ciągu ostatnich 20 minut."
                        )
                    except Exception:
                        pass
                    return

            channel_cooldowns[voice_channel.id] = now        
            
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
                embed.set_footer(text=f"ID użytkownika: {user.id}")

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


# ==============================================================================
# PĘTLA AKTUALIZACJI STATUSU (CO 10 MINUT)
# ==============================================================================
@tasks.loop(minutes=10)
async def update_member_status():
    """Pętla aktualizująca status bota na podstawie liczby osób na serwerze."""
    try:
        if not bot.guilds:
            return
            
        guild = bot.guilds[0]
        member_count = guild.member_count
        
        # Ogląda: X użytkowników 🦎
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"{member_count} użytkowników 🦎"
        )
        
        await bot.change_presence(activity=activity)
        print(f"[STATUS] Zaktualizowano liczbę członków serwera: {member_count}")
        
    except Exception as e:
        print(f"[BŁĄD MEMBER STATUS LOOP]: {e}")


async def main():
    async with bot:
        await bot.load_extension("tempvoice.manager")
        await bot.start(TOKEN)

asyncio.run(main())
