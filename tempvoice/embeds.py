import discord

def create_control_panel_embed(owner_mention: str) -> discord.Embed:
    embed = discord.Embed(
        title="⚙️ Panel Zarządzania Kanałem",
        description=(
            f"Użyj poniższych przycisków, aby zarządzać swoim kanałem.\n\n"
            f"👑 **Właściciel:** {owner_mention}\n\n"
            "**Ustawienia podstawowe:**\n"
            "📝 — Zmień nazwę kanału\n"
            "👥 — Ustaw limit osób na kanale\n\n"
            "**Dostęp i Moderacja:**\n"
            "🔒 — Zablokuj kanał dla wszystkich\n"
            "🔓 — Odblokuj kanał\n"
            "👢 — Wyrzuć wybranego użytkownika\n"
            "🚪 — Odbanuj wybranego użytkownika\n"
            "👑 — Przekaż koroną właściciela"
        ),
        color=discord.Color.from_rgb(46, 204, 113)  # Kameleonowa zieleń
    )
    embed.set_footer(text="Kameleon Guard • Zarządzanie kanałem tymczasowym")
    return embed
