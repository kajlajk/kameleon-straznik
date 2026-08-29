import discord
from discord.ext import commands
import os
import asyncio
import time
import random 
import re
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
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

# --- SKONFIGUROWANE ID DLA EVENTÓW I MODERACJI ---
EVENT_CHANNEL_ID = 1543224283633811497  
ROLE_EVENT_ID = 1543224655698075728     
ROLE_MODERACJA_ID = 1525953762441822370

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


# --- POMOCNICZE FUNKCJE ---

def can_manage_events(user: discord.Member) -> bool:
    if user.id == OWNER_ID or user.guild_permissions.administrator:
        return True
    mod_role = user.guild.get_role(ROLE_MODERACJA_ID)
    return mod_role in user.roles if mod_role else False

def parse_event_datetime(date_str: str) -> datetime:
    """Konwertuje tekst daty na obiekt ze strefą UTC, wymuszając polski czas (Europe/Warsaw)."""
    date_str = date_str.strip()
    
    poland_tz = ZoneInfo("Europe/Warsaw")
    now_pl = datetime.now(poland_tz)

    dt_pl = None

    if re.match(r'^\d{1,2}:\d{2}$', date_str):
        h, m = map(int, date_str.split(':'))
        dt_pl = now_pl.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt_pl < now_pl:
            dt_pl += timedelta(days=1)
    else:
        formats = [
            "%d.%m.%Y %H:%M", "%d.%m.%Y %H:%M:%S",
            "%d.%m %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M"
        ]
        for fmt in formats:
            try:
                dt_parsed = datetime.strptime(date_str, fmt)
                if dt_parsed.year == 1900:
                    dt_parsed = dt_parsed.replace(year=now_pl.year)
                dt_pl = dt_parsed.replace(tzinfo=poland_tz)
                break
            except ValueError:
                continue

    if dt_pl:
        return dt_pl.astimezone(timezone.utc)
    
    return None


# --- KLASY INTERFEJSU EVENTÓW ---

class EventSignUpView(discord.ui.View):
    def __init__(self, author_id: int = None, target_timestamp: int = None, last_ping_msg_id: int = None):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.target_timestamp = target_timestamp
        self.last_ping_msg_id = last_ping_msg_id

    @discord.ui.button(label="Zapisz się 🙋", style=discord.ButtonStyle.success, custom_id="event_signup_btn")
    async def sign_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_EVENT_ID)
        if not role:
            return await interaction.response.send_message("❌ Rola eventowa nie została odnaleziona!", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.response.send_message("ℹ️ Jesteś już zapisany/a na ten event!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Zapisano na event! Otrzymujesz rolę {role.mention}.", ephemeral=True)

    @discord.ui.button(label="Wypisz się ❌", style=discord.ButtonStyle.danger, custom_id="event_signout_btn")
    async def sign_out(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_EVENT_ID)
        if not role:
            return await interaction.response.send_message("❌ Rola eventowa nie została odnaleziona!", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🗑️ Wypisano z eventu. Rola została usunięta.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Nie byłeś/aś zapisany/a na ten event.", ephemeral=True)

    @discord.ui.button(label="🔔 Przypomnij (@Event)", style=discord.ButtonStyle.secondary, custom_id="event_ping_btn")
    async def manual_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.author_id and interaction.user.id != self.author_id and not can_manage_events(interaction.user):
            return await interaction.response.send_message("❌ Tylko organizator eventu lub moderator może użyć tego przycisku!", ephemeral=True)

        if self.last_ping_msg_id:
            try:
                old_msg = await interaction.channel.fetch_message(self.last_ping_msg_id)
                await old_msg.delete()
            except Exception:
                pass

        role = interaction.guild.get_role(ROLE_EVENT_ID)
        role_ping = role.mention if role else "@here"
        
        remaining_str = ""
        if self.target_timestamp:
            now_ts = int(time.time())
            if self.target_timestamp > now_ts:
                remaining_str = f"\n⏳ **Pozostały czas do startu:** <t:{self.target_timestamp}:R> (<t:{self.target_timestamp}:t>)"
            else:
                remaining_str = "\n🔥 **Event właśnie się rozpoczyna lub trwa!**"

        new_ping_msg = await interaction.channel.send(
            f"🔔 **PRZYPOMNIENIE O EVENTOWYM SPOTKANIU!** {role_ping}\n"
            f"Zapraszamy do dołączenia!{remaining_str}"
        )
        self.last_ping_msg_id = new_ping_msg.id

        await interaction.response.send_message("✅ Przypomnienie zostało wysłane!", ephemeral=True)

    @discord.ui.button(label="✏️ Edytuj event", style=discord.ButtonStyle.primary, custom_id="event_edit_btn")
    async def edit_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.author_id and interaction.user.id != self.author_id and not can_manage_events(interaction.user):
            return await interaction.response.send_message("❌ Tylko organizator lub moderator może edytować to wydarzenie!", ephemeral=True)

        await interaction.response.send_modal(EditEventModal(interaction.message, self))

    @discord.ui.button(label="🗑️ Usuń event", style=discord.ButtonStyle.danger, custom_id="event_delete_btn")
    async def delete_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.author_id and interaction.user.id != self.author_id and not can_manage_events(interaction.user):
            return await interaction.response.send_message("❌ Tylko organizator lub moderator może usunąć ten event!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        # 1. Czyszczenie roli eventowej uczestnikom
        role = interaction.guild.get_role(ROLE_EVENT_ID)
        cleaned_members = 0
        if role:
            for member in role.members:
                try:
                    await member.remove_roles(role)
                    cleaned_members += 1
                except Exception:
                    pass

        # 2. Usuwanie ewentualnego ostatniego przypomnienia (pingu)
        if self.last_ping_msg_id:
            try:
                ping_msg = await interaction.channel.fetch_message(self.last_ping_msg_id)
                await ping_msg.delete()
            except Exception:
                pass

        # 3. Usuwanie głównej wiadomości eventu
        try:
            await interaction.message.delete()
        except Exception:
            pass

        await interaction.followup.send(f"✅ Event został pomyślnie usunięty, a rola została zdjęta u {cleaned_members} osób.")


class EditEventModal(discord.ui.Modal, title="Edytuj Event"):
    def __init__(self, target_message: discord.Message, current_view: EventSignUpView):
        super().__init__()
        self.target_message = target_message
        self.current_view = current_view
        
        embed = target_message.embeds[0] if target_message.embeds else None
        
        title_val = embed.title.replace("🎉 NOWY EVENT: ", "").strip() if embed and embed.title else ""
        kiedy_val = ""
        koszt_val = "Darmowa"
        opis_val = ""

        if embed:
            for field in embed.fields:
                if field.name == "📅 Kiedy":
                    kiedy_val = field.value.split("\n⏳")[0]
                elif field.name == "💰 Koszt":
                    koszt_val = field.value
                elif field.name == "📝 Opis i szczegóły":
                    opis_val = field.value

        self.nazwa_gry = discord.ui.TextInput(label="Nazwa gry / wydarzenia", default=title_val, required=True)
        self.data_godzina = discord.ui.TextInput(label="Data i godzina (np. 25.10.2026 20:00)", default=kiedy_val, placeholder="DD.MM.YYYY HH:MM lub sama godzina 20:00", required=True)
        self.koszt = discord.ui.TextInput(label="Koszt gry", default=koszt_val, required=True)
        self.opis = discord.ui.TextInput(label="Dodatkowy opis / zasady", style=discord.TextStyle.paragraph, default=opis_val, required=False)

        self.add_item(self.nazwa_gry)
        self.add_item(self.data_godzina)
        self.add_item(self.koszt)
        self.add_item(self.opis)

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.target_message.embeds[0]
        embed.title = f"🎉 NOWY EVENT: {self.nazwa_gry.value}"
        
        parsed_dt = parse_event_datetime(self.data_godzina.value)
        target_ts = int(parsed_dt.timestamp()) if parsed_dt else None
        
        kiedy_text = self.data_godzina.value
        if target_ts:
            kiedy_text += f"\n⏳ **Start:** <t:{target_ts}:R> (<t:{target_ts}:t>)"

        new_fields = []
        new_fields.append({"name": "📅 Kiedy", "value": kiedy_text, "inline": True})
        new_fields.append({"name": "💰 Koszt", "value": self.koszt.value, "inline": True})
        if self.opis.value:
            new_fields.append({"name": "📝 Opis i szczegóły", "value": self.opis.value, "inline": False})
        
        event_role = interaction.guild.get_role(ROLE_EVENT_ID)
        new_fields.append({
            "name": "🔔 Powiadomienia",
            "value": f"Zapisz się przyciskiem poniżej, aby otrzymać rolę {event_role.mention if event_role else ''} i powiadomienie!",
            "inline": False
        })

        embed.clear_fields()
        for f in new_fields:
            embed.add_field(name=f["name"], value=f["value"], inline=f["inline"])

        view = EventSignUpView(
            author_id=interaction.user.id,
            target_timestamp=target_ts,
            last_ping_msg_id=self.current_view.last_ping_msg_id
        )

        await self.target_message.edit(embed=embed, view=view)
        await interaction.response.send_message("✅ Zaktualizowano dane eventu!", ephemeral=True)


class OpenEventModalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="📝 Otwórz formularz eventu", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not can_manage_events(interaction.user):
            return await interaction.response.send_message("❌ Brak uprawnień do tworzenia eventów.", ephemeral=True)
        await interaction.response.send_modal(CreateEventModal())


class CreateEventModal(discord.ui.Modal, title="Stwórz Nowy Event"):
    nazwa_gry = discord.ui.TextInput(
        label="Nazwa gry / wydarzenia",
        placeholder="np. Mafia / Karaoke / CS:GO 1v1",
        required=True
    )
    data_godzina = discord.ui.TextInput(
        label="Data i godzina startu",
        placeholder="np. 25.10.2026 20:00 (lub sama godzina: 20:00)",
        required=True
    )
    koszt = discord.ui.TextInput(
        label="Koszt gry",
        placeholder="np. Darmowa / Wymagana własna gra",
        default="Darmowa",
        required=True
    )
    opis = discord.ui.TextInput(
        label="Dodatkowy opis / zasady",
        style=discord.TextStyle.paragraph,
        placeholder="Szczegóły wydarzenia, zasady, linki itp.",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(EVENT_CHANNEL_ID)
        event_role = interaction.guild.get_role(ROLE_EVENT_ID)
        
        if not channel:
            return await interaction.response.send_message("❌ Kanał eventowy nie istnieje!", ephemeral=True)

        parsed_dt = parse_event_datetime(self.data_godzina.value)
        target_timestamp = int(parsed_dt.timestamp()) if parsed_dt else None
        delay_seconds = (parsed_dt - datetime.now(timezone.utc)).total_seconds() if parsed_dt else 0

        embed = discord.Embed(
            title=f"🎉 NOWY EVENT: {self.nazwa_gry.value}",
            description="Zapraszamy wszystkich chętnych do wspólnej zabawy!",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        kiedy_val = self.data_godzina.value
        if target_timestamp:
            kiedy_val += f"\n⏳ **Start:** <t:{target_timestamp}:R> (<t:{target_timestamp}:t>)"

        embed.add_field(name="📅 Kiedy", value=kiedy_val, inline=True)
        embed.add_field(name="💰 Koszt", value=self.koszt.value, inline=True)
        if self.opis.value:
            embed.add_field(name="📝 Opis i szczegóły", value=self.opis.value, inline=False)
        
        embed.add_field(
            name="🔔 Powiadomienia",
            value=f"Zapisz się przyciskiem poniżej, aby otrzymać rolę {event_role.mention if event_role else ''} i powiadomienie!",
            inline=False
        )
        embed.set_author(name=f"Organizator: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
        embed.set_footer(text="KameleonEvent • Zapisz się przyciskiem poniżej!")

        ping_text = event_role.mention if event_role else "@here"
        
        view = EventSignUpView(author_id=interaction.user.id, target_timestamp=target_timestamp)
        event_msg = await channel.send(content=f"🚀 **Wpadajcie na event!** {ping_text}", embed=embed, view=view)
        await interaction.response.send_message("✅ Ogłoszenie o evencie zostało opublikowane!", ephemeral=True)

        if delay_seconds > 0:
            async def auto_ping_task():
                await asyncio.sleep(delay_seconds)
                try:
                    await channel.send(
                        f"🚨 **EVENT WŁAŚNIE SIĘ ZACZYNA!** {ping_text}\n"
                        f"Wbijajcie na event: **{self.nazwa_gry.value}**! 🎮",
                        reference=event_msg
                    )
                except Exception as e:
                    print(f"[BŁĄD AUTO-PING]: {e}")

            asyncio.create_task(auto_ping_task())


# --- KLASY INTERFEJSU WIZYTÓWEK / OGŁOSZEŃ ---

class EditAdvancedPostModal(discord.ui.Modal, title="Edycja Wizytówki"):
    def __init__(self, target_message: discord.Message):
        super().__init__()
        self.target_message = target_message

        embed = self.target_message.embeds[0] if self.target_message.embeds else None
        current_desc = ""

        if embed:
            for field in embed.fields:
                if field.name == "💬 O mnie":
                    current_desc = field.value
                    break

        self.new_content = discord.ui.TextInput(
            label="Napisz coś o sobie",
            style=discord.TextStyle.paragraph,
            default=current_desc,
            placeholder="Opisz swoje zainteresowania, w co grasz, kogo chcesz poznać...",
            max_length=1000,
            required=True
        )
        self.add_item(self.new_content)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = self.target_message.embeds[0]
            embed.timestamp = datetime.now(timezone.utc)
            new_desc_value = self.new_content.value if self.new_content.value else "*Brak opisu.*"
            
            description_updated = False
            for i, field in enumerate(embed.fields):
                if field.name == "💬 O mnie":
                    embed.set_field_at(i, name="💬 O mnie", value=new_desc_value, inline=False)
                    description_updated = True
                    break
            
            if not description_updated:
                embed.add_field(name="💬 O mnie", value=new_desc_value, inline=False)

            await self.target_message.edit(embed=embed)
            await interaction.response.send_message("✅ Wizytówka zaktualizowana!", ephemeral=True)
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

    @discord.ui.button(label="✏️ Edytuj opis", style=discord.ButtonStyle.secondary)
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

    bot.add_view(EventSignUpView())

    try:
        synced = await bot.tree.sync()
        print(f"✅ Zsynchronizowano {len(synced)} komend(y) Slash w menu Discorda!")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend Slash: {e}")

    if not check_timeouts.is_running(): check_timeouts.start()
    if not update_member_status.is_running(): update_member_status.start()
    if not bump_timer_check.is_running(): bump_timer_check.start()
    if not cycle_info_channel.is_running(): cycle_info_channel.start()


# --- KOMENDY EVENTOWE TEKSTOWE (!) I SLASH (/) ---

@bot.tree.command(name="stworz_event", description="Tworzy formularz do tworzenia wydarzenia/eventu.")
async def stworz_event_slash(interaction: discord.Interaction):
    if not can_manage_events(interaction.user):
        return await interaction.response.send_message("❌ Nie masz uprawnień do tworzenia eventów.", ephemeral=True)

    if interaction.channel_id != EVENT_CHANNEL_ID:
        event_channel = interaction.guild.get_channel(EVENT_CHANNEL_ID)
        channel_mention = event_channel.mention if event_channel else "kanału eventowego"
        return await interaction.response.send_message(f"⚠️ Tej komendy możesz używać wyłącznie na kanale {channel_mention}!", ephemeral=True)

    await interaction.response.send_message("Oto formularz wydarzenia (kliknij poniższy przycisk):", view=OpenEventModalView(), ephemeral=True)


@bot.command(name="stworz_event", aliases=["event"])
async def stworz_event_cmd(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    if not can_manage_events(ctx.author):
        return await ctx.author.send("❌ Nie masz uprawnień do tworzenia eventów.")

    if ctx.channel.id != EVENT_CHANNEL_ID:
        event_channel = ctx.guild.get_channel(EVENT_CHANNEL_ID)
        channel_mention = event_channel.mention if event_channel else "kanału eventowego"
        return await ctx.author.send(f"⚠️ Komendy `!stworz_event` możesz używać wyłącznie na kanale {channel_mention}!")

    await ctx.send("Oto formularz wydarzenia (kliknij poniższy przycisk):", view=OpenEventModalView(), delete_after=60)


@bot.tree.command(name="zakoncz_event", description="Usuwa rolę eventową uczestnikom po zakończeniu wydarzenia.")
async def zakoncz_event_slash(interaction: discord.Interaction):
    if not can_manage_events(interaction.user):
        return await interaction.response.send_message("❌ Brak uprawnień do komendy `/zakoncz_event`.", ephemeral=True)

    role = interaction.guild.get_role(ROLE_EVENT_ID)
    if not role:
        return await interaction.response.send_message("❌ Nie znaleziono roli eventowej.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)

    count = 0
    for member in role.members:
        try:
            await member.remove_roles(role)
            count += 1
        except Exception:
            pass
    
    await interaction.followup.send(f"✅ Event zakończony! Pomyślnie usunięto rolę **{role.name}** u **{count}** użytkowników.")


@bot.command(name="zakoncz_event")
async def zakoncz_event_cmd(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    if not can_manage_events(ctx.author):
        return await ctx.author.send("❌ Brak uprawnień do komendy `!zakoncz_event`.")

    role = ctx.guild.get_role(ROLE_EVENT_ID)
    if not role:
        return await ctx.author.send("❌ Nie znaleziono roli eventowej.")

    status_msg = await ctx.author.send("⏳ Czyszczenie ról uczestników eventu... Proszę czekać.")

    count = 0
    for member in role.members:
        try:
            await member.remove_roles(role)
            count += 1
        except Exception:
            pass
    
    await status_msg.edit(content=f"✅ Event zakończony! Pomyślnie usunięto rolę **{role.name}** u **{count}** użytkowników.")


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

    # --- KANAŁY OGŁOSZEŃ I WIZYTÓWEK ---
    if message.channel.id in (SZUKAM_CHANNEL, SZUKAM_ZNAJOMYCH_CHANNEL):
        content_lower = message.content.lower()
        
        has_role_ping = len(message.role_mentions) > 0
        has_hashtag = "#szukam do gry" in content_lower or "#szukamdogry" in content_lower
        is_znajomi_channel = message.channel.id == SZUKAM_ZNAJOMYCH_CHANNEL

        if is_znajomi_channel or has_role_ping or has_hashtag:
            now = time.time()
            user_id = message.author.id
            cooldown_key = (user_id, message.channel.id)
            
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

                if is_znajomi_channel:
                    await message.delete()
                    post_cooldowns[cooldown_key] = now
                    
                    ping_text = f"{target_role.mention} {author.mention}" if target_role else author.mention

                    if not clean_content:
                        clean_content = "Hej, szukam kogoś do pogadania i wspólnego spędzania czasu!"

                    embed = discord.Embed(
                        title="✨ Wizytówka profilowa",
                        color=discord.Color.teal(),
                        timestamp=datetime.now(timezone.utc)
                    )

                    embed.set_author(
                        name=f"Wizytówka: {author.display_name}",
                        icon_url=author.display_avatar.url if author.display_avatar else None
                    )
                    embed.set_thumbnail(url=author.display_avatar.url if author.display_avatar else None)

                    embed.add_field(name="💬 O mnie", value=clean_content, inline=False)

                    plec_keywords = ["mężczyzna", "kobieta", "niebinarność"]
                    wiek_keywords = ["13-15", "16-18", "19-24", "25+", "13–15", "16–18", "19–24", "13 - 15", "16 - 18", "19 - 24"]
                    status_keywords = ["singiel", "singielka", "w związku", "zajęty", "zajęta"]
                    wojewodztwo_keywords = [
                        "dolnośląskie", "kujawsko-pomorskie", "lubelskie", "lubuskie", 
                        "łódzkie", "małopolskie", "mazowieckie", "opolskie", "podkarpackie", 
                        "podlaskie", "pomorskie", "śląskie", "świętokrzyskie", 
                        "warmińsko-mazurskie", "wielkopolskie", "zachodniopomorskie"
                    ]

                    plec_role = None
                    wiek_role = None
                    status_role = None
                    wojewodztwo_role = None

                    for r in author.roles:
                        r_name = r.name.lower()
                        
                        if not plec_role and any(k in r_name for k in plec_keywords):
                            plec_role = r.mention
                        elif not wiek_role and (any(k in r_name for k in wiek_keywords) or re.search(r'\b(1[3-9]|[2-9][0-9])\b', r_name)):
                            if "lvl" not in r_name and "poziom" not in r_name and "kameleon" not in r_name:
                                wiek_role = r.mention
                        elif not status_role and any(k in r_name for k in status_keywords):
                            status_role = r.mention
                        elif not wojewodztwo_role and any(k in r_name for k in wojewodztwo_keywords):
                            wojewodztwo_role = r.mention

                    if plec_role:
                        embed.add_field(name="👤 Płeć", value=plec_role, inline=False)
                    if wiek_role:
                        embed.add_field(name="🎂 Wiek", value=wiek_role, inline=False)
                    if status_role:
                        embed.add_field(name="❤️ Status", value=status_role, inline=False)
                    if wojewodztwo_role:
                        embed.add_field(name="📍 Województwo", value=wojewodztwo_role, inline=False)

                    if target_role:
                        embed.add_field(name="📌 Oznaczona rola", value=target_role.mention, inline=False)

                    embed.set_footer(text="Chcesz coś zmienić? Kliknij ✏️ Edytuj opis poniżej!")

                    view = AdvancedPostView(author_id=author.id, voice_channel_url=None)
                    await message.channel.send(content=ping_text, embed=embed, view=view)

                else:
                    voice_state = author.voice
                    if not voice_state or not voice_state.channel:
                        await message.delete()
                        try:
                            await author.send(
                                f"❌ **Ogłoszenie nie zostało opublikowane!**\n"
                                f"Aby wysłać ogłoszenie na kanale {message.channel.mention}, musisz najpierw dołączyć do dowolnego kanału głosowego."
                            )
                        except discord.Forbidden:
                            pass
                        return

                    await message.delete()
                    post_cooldowns[cooldown_key] = now

                    if target_role:
                        ping_text = f"{target_role.mention} {author.mention}"
                        game_title = re.sub(r'<[^>]+>', '', target_role.name).strip()
                    else:
                        default_role = message.guild.get_role(ROLE_SZUKAM_DO_GRY_ID)
                        ping_text = f"{default_role.mention} {author.mention}" if default_role else author.mention
                        game_title = "Gry"

                    if not clean_content:
                        clean_content = "Hej, szukam kogoś do wspólnej gry!"

                    voice_channel_name = f"🎙️ {voice_state.channel.name}"
                    user_limit = voice_state.channel.user_limit
                    current_users = len(voice_state.channel.members)
                    
                    osoby_text = "osoba" if current_users == 1 else "osoby" if 2 <= current_users <= 4 else "osób"
                    lobby_status = f"{current_users}/{user_limit} {osoby_text}" if user_limit > 0 else f"{current_users} {osoby_text}"
                    vc_url = f"https://discord.com/channels/{message.guild.id}/{voice_state.channel.id}"

                    embed = discord.Embed(
                        title=f"🎮 Szukamy graczy do {game_title}!",
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

                    embed.set_footer(text="Kliknij przycisk poniżej, aby dołączyć do kanału!")

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
            "💚 Fajnie że jesteście!",
            "💬 Miłego pisania!",
            "🦎 Kajlajk Pozdrawia!",
            "🚀 Pamiętaj o /bump",
            "🎮 Wpadaj na #szukam",
            "📸 Zostaw screena!",
            "❤️ Zapraszaj Znajomych!",
            "🏆 Wbijaj poziomy!",
            "☕ Usiądź i pogadaj",
            "🛡️ Przeczytaj regulamin"
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
