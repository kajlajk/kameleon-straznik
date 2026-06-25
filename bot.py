
import discord
from discord.ext import commands
import os
import time
import random 
from datetime import timedelta

TOKEN = os.getenv("TOKEN")

OWNER_ID = 765301434350567426
SZUKAM_CHANNEL = 1515570301172449362
CHAT_CHANNEL = 1515567593694691413
SZUKAM_ROLE = 1515875177852833872
SCREENY_CHANNEL = 1515570115515650068  

STARTIT_BOT_ID = 572906387382861835
LEVEL_ROLE_ID = 1519678728438026321

channel_cooldowns = {}
warnings = {}
last_random_message = 0
answered_users = {}
last_reply_text = None
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
    "🤔 Ciekawe kto pierwszy napisze na czacie."
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
    "🤨 Aha Gratulacje, wygrywasz bana."
]



intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:

    # Obsługa wiadomości od StartIT
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
            except discord.Forbidden:
                pass
            except discord.HTTPException:
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
        answered_users = {}

        last_random_message = now

    if message.reference:
        

        try:
            replied_message = await message.channel.fetch_message(
                message.reference.message_id
            )

            if replied_message.author.id == bot.user.id:
                

                replied_id = replied_message.id

                if replied_id not in answered_users:
                    answered_users[replied_id] = set()

                if message.author.id not in answered_users[replied_id]:
                    

                    response = random.choice(reply_texts)

                    while (
                        last_reply_text is not None
                        and response == last_reply_text
                    ):
                        response = random.choice(reply_texts)

                    
                    await message.reply(response)
                    

                    last_reply_text = response
                    answered_users[replied_id].add(message.author.id)

        except Exception as e:
            print(f"Błąd odpowiedzi: {e}")   
 
    if message.content.lower() =="/spokojnie":
        if (
            message.author.id == OWNER_ID
            and message.channel.id == 1515593063639285810
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
                "🤖 Speedrun do ciekawego wpisu w logach.",
                "🤖 Wykryto nietypową aktywność użytkowników.",
                "🤖 Kontynuujcie, jestem zaintrygowany.",
                "🤖 Kameleon nie ocenia. Kameleon obserwuje. 🦎"
            ]
            await channel.send(random.choice(teksty))

            await message.delete()

        return

    if len(message.mentions) > 3:
        await message.delete()

        try:
            await message.author.send(
                "Możesz oznaczyć maksymalnie 3 osoby w jednej wiadomości."
                    )
        except:
            pass

        return

    role_pinged = any(role.id == SZUKAM_ROLE for role in message.role_mentions)
    
    if role_pinged:

        # Ping poza #szukam-do-gry
        if message.channel.id != SZUKAM_CHANNEL:
            await message.delete()
    
            warnings[message.author.id] = warnings.get(message.author.id, 0) + 1
    
            if warnings[message.author.id] == 1:
                try:
                    await message.author.send(
                        f"{message.author.mention} Rola Szukam do gry może być używana tylko na kanale Szukam do gry."
                    )
                except:
                    pass
    
            elif warnings[message.author.id] == 2:
                await message.author.timeout(
                    timedelta(minutes=20),
                    reason="Pingowanie roli poza #szukam-do-gry"
                )
    
            elif warnings[message.author.id] >= 3:
                await message.author.timeout(
                    timedelta(hours=1),
                    reason="Wielokrotne pingowanie roli poza #szukam-do-gry"
                )
    
            return

        # Cooldown na kanał głosowy
        if message.channel.id == SZUKAM_CHANNEL:

            if not message.author.voice:
                await message.delete()

                try:
                    await message.author.send(
                        "Aby użyć @Szukam do gry, musisz siedzieć na kanale głosowym."
                    )
                except:
                    pass

                return

            voice_channel = message.author.voice.channel
            now = time.time()

            if voice_channel.id in channel_cooldowns:
                if now - channel_cooldowns[voice_channel.id] < 1200:

                    await message.delete()

                    try:
                        await message.author.send(
                            "Ktoś z twojego kanału głosowego użył już @Szukam do gry w ciągu ostatnich 20 minut."
                        )
                    except:
                        pass

                    return

            channel_cooldowns[voice_channel.id] = now        
            
    await bot.process_commands(message)


bot.run(TOKEN)

