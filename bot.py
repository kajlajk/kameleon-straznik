
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

channel_cooldowns = {}
warnings = {}
last_random_message = 0
last_bot_message_id = None
answered_users = {}
last_reply_text = None

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
    global last_bot_message_id
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

