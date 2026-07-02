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
SZUKAM_ROLE = 1515875177852833872
SCREENY_CHANNEL = 1515570115515650068  
LOG_CHANNEL_ID = 1521585275229442178

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
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("BOT ONLINE TEST OK")
    print("NOWA WERSJA BOTA")
    print(f"Zalogowano jako {bot.user}")

    if not check_timeouts.is_running():
        check_timeouts.start()
    

@bot.event
async def on_message(message):
    if message.author.bot:
        # Obsługa wiadomości od StartIT
        if message.author.id == STARTIT
