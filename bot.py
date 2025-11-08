import discord
from discord.ext import commands
import logging
from config import DISCORD_TOKEN, BOT_NAME, GUILD_IDS
from utils.logger import setup_logger

# --- Initialisation du logger ---
setup_logger()
logger = logging.getLogger("r00ty")

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # pour gérer les membres, rôles, etc.
intents.presences = False

# -- Bot instance ---
class RootSphereBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
        )
    
    async def setup_hook(self):
        # Chargement des cogs au démarrage
        await self.load_extension("cogs.core")
        await self.load_extension("cogs.rss")

        # Sync des commandes slash
        if GUILD_IDS:
            for guild_id in GUILD_IDS:
                guild = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
            print("[SYNC] Commandes slash synchronisées sur les serveurs spécifiés.")
        else:
            await self.tree.sync()
            print("[SYNC] Commandes slash globales synchronisées (peut prendre un peu de temps à apparaître).")

    async def on_ready(self):
        print(f"[START] Connecté en tant que {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="les flux cyber sur RootSphere 🌐"
            )
        )

# --- Lancement ---
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Le token Discord n'est pas défini dans le fichier .env (DISOCRD_TOKEN).")

    bot = RootSphereBot()
    bot.run(DISCORD_TOKEN)