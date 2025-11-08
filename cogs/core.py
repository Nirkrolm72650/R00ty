import discord
from discord.ext import commands
from discord import app_commands
from config import BOT_NAME

class Core(commands.Cog):
    """Fonctionnalités de base du bot RootSphere / r00ty"""

    def __init__(self, bot: commands.bot):
        self.bot = bot

    # Commande slash / ping
    @app_commands.command(name="ping", description="Vérifi si r00ty est en ligne.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"🏓 {BOT_NAME} est bien réveillé ! Latence : `{latency} ms`",
            ephemeral=True
        )

    # Commande slash /about
    @app_commands.command(name="about", description="Infos sur RootSphere et r00ty.")
    async def about(self, interaction: discord.Interaction):
        text = (
            f"👋 Je suis **{BOT_NAME}**, la mascotte de **RootSphere**.\n"
            "Je suis en cours d'évolution pour devenir un bot multi-fonctions :\n"
            "🔹 Veille cyber & vulnérabilités (RSS, CVE, alertes)\n"
            "🔹 Admin système & réseau (outils pratiques, rappels, docs)\n"
            "🔹 Outils communautaires & modération\n"
            "🔹 Et d'autres modules à venir, pensés pour la communauté technique."
        )
        await interaction.response.send_message(text, ephemeral=False)

    # Commande texte classique !ping (optionnelle)
    @commands.command(name="ping")
    async def ping_legacy(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.reply(f"🏓 {BOT_NAME} en ligne. Latence : `{latency} ms`")

async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))