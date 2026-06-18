
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

cooldowns = {}
warnings = {}
last_random_message = 0

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

    global last_random_message

    now = time.time()

    if (
        message.channel.id == CHAT_CHANNEL
        and now - last_random_message > 3600
        and random.randint(1, 50) == 1
    ):
        await message.channel.send(
            random.choice(random_texts)
        )

        last_random_message = now

    if message.content.lower() == "/spokojnie":
        if (
            message.author.id == OWNER_ID
            and message.channel.id == 1515593063639285810
        ):

            channel = bot.get_channel(CHAT_CHANNEL)

            await channel.send(
                "Spokojnie, bo cię odholuje."
            )

            await message.delete()

        return

        if len(message.mentions) > 3:
            await message.delete()

            try:
                    await message.author.send(
                "❌ Możesz oznaczyć maksymalnie 3 osoby w jednej wiadomości."
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
                        f"{message.author.mention}, UWAGAA! Rola Szukam do gry może być używana tylko na Kanale Szukam do gry."
                    )
                except:
                    pass
    
            elif warnings[message.author.id] == 2:
                await message.author.timeout(
                    timedelta(minutes=10),
                    reason="Pingowanie roli poza #szukam-do-gry"
                )
    
            elif warnings[message.author.id] >= 3:
                await message.author.timeout(
                    timedelta(hours=1),
                    reason="Wielokrotne pingowanie roli poza #szukam-do-gry"
                )
    
            return
        # Cooldown na #szukam-do-gry
        if message.channel.id == SZUKAM_CHANNEL:
            now = time.time()

            if message.author.id in cooldowns:
                if now - cooldowns[message.author.id] < 600:
                    await message.delete()

                    msg = await message.channel.send(
                        f"{message.author.mention}, możesz pingować @Szukam do gry tylko raz na 10 minut."
                    )

                    await msg.delete(delay=10)
                    return

            cooldowns[message.author.id] = now

    await bot.process_commands(message)


bot.run(TOKEN)

