# cogs/rss.py

import discord
from discord.ext import commands, tasks
import feedparser
import json
import os
import asyncio
import logging
import re
from datetime import datetime
from config import RSS_CONFIG, R00TY_AVATAR_URL

logger = logging.getLogger("r00ty")
DATA_FILE = "data/rss_feeds.json"


class RSSCog(commands.Cog):
    """Cog de veille RSS enrichie avec images, résumé et couleurs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure_data_file()
        self.posted_links = self._load_posted_links()
        self.fetch_rss.start()  # démarre la tâche périodique

    def cog_unload(self):
        """Annule la tâche si le cog est déchargé."""
        self.fetch_rss.cancel()

    # -------------------------------
    # Gestion du fichier JSON
    # -------------------------------
    def _ensure_data_file(self):
        """Crée le fichier de stockage si absent."""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"posted_links": []}, f, indent=4)

    def _load_posted_links(self):
        """Charge les liens déjà postés (anti doublon)."""
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("posted_links", [])
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("⚠️ Fichier JSON vide ou invalide, recréation...")
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"posted_links": []}, f, indent=4)
            return []

    def _save_posted_links(self):
        """Sauvegarde les liens déjà postés."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"posted_links": self.posted_links}, f, indent=4)

    # -------------------------------
    # Utilitaires
    # -------------------------------
    def extract_cvss(self, entry):
        """Cherche un score CVSS dans le titre ou le résumé."""
        text = f"{entry.title} {getattr(entry, 'summary', '')}"
        match = re.search(r"CVSS[:\s]*([0-9]\.?[0-9]?)", text)
        if not match:
            return "N/A", "Inconnu", discord.Color.dark_grey()

        score = float(match.group(1))
        if score >= 9:
            return score, "Critique 🔴", discord.Color.red()
        elif score >= 7:
            return score, "Élevée 🟠", discord.Color.orange()
        elif score >= 4:
            return score, "Moyenne 🟡", discord.Color.yellow()
        else:
            return score, "Faible 🟢", discord.Color.green()

    def short_summary(self, entry):
        """Crée un résumé court sans HTML."""
        summary = getattr(entry, "summary", None)
        if not summary:
            return "Pas de résumé disponible pour cet article."
        summary = re.sub(r"<[^>]+>", "", summary)  # supprime le HTML
        return summary[:250] + ("..." if len(summary) > 250 else "")

    def get_image_url(self, entry):
        """Récupère l’image de l’article si elle existe, sinon avatar de r00ty."""
        image_url = None

        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0].get("url")
        elif "links" in entry:
            for l in entry.links:
                if l.get("type", "").startswith("image"):
                    image_url = l.get("href")
                    break

        if not image_url:
            image_url = R00TY_AVATAR_URL

        return image_url

    # -------------------------------
    # Création d’un embed stylé
    # -------------------------------
    def create_embed(self, category, entry, feed_title):
        """Crée un embed Discord complet et contextuel."""
        title = entry.title
        link = entry.link
        published = getattr(entry, "published", "Date inconnue")
        summary = self.short_summary(entry)
        image_url = self.get_image_url(entry)

        # === Cyber ===
        if category == "Cybersecurity":
            embed = discord.Embed(
                title="🌐 Un nouvel article est sorti !",
                description=f"**[{title}]({link})**\n\n{summary}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Veille Cyber • {feed_title} • {published}")
            embed.set_author(name="R00ty", icon_url=R00TY_AVATAR_URL)
            embed.set_thumbnail(url=image_url)

        # === Vulnérabilités ===
        elif category == "Vulnerabilites":
            cvss_score, criticity, color = self.extract_cvss(entry)
            embed = discord.Embed(
                title="🚨 Une nouvelle vulnérabilité a été détectée !",
                description=f"**[{title}]({link})**\n\n💣 **Score CVSS :** {cvss_score}\n💥 **Criticité :** {criticity}\n\n{summary}",
                color=color,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Veille Vulnérabilités • {feed_title} • {published}")
            embed.set_author(name="R00ty", icon_url=R00TY_AVATAR_URL)
            embed.set_thumbnail(url=image_url)

        # === Linux ===
        elif category == "Sys-Linux":
            embed = discord.Embed(
                title="🐧 Nouvel article Linux disponible !",
                description=f"**[{title}]({link})**\n\n{summary}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Veille Linux • {feed_title} • {published}")
            embed.set_author(name="R00ty", icon_url=R00TY_AVATAR_URL)
            embed.set_thumbnail(url=image_url)

        # === Windows ===
        elif category == "Sys-Windows":
            embed = discord.Embed(
                title="🪟 Nouvel article Windows disponible !",
                description=f"**[{title}]({link})**\n\n{summary}",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Veille Windows • {feed_title} • {published}")
            embed.set_author(name="R00ty", icon_url=R00TY_AVATAR_URL)
            embed.set_thumbnail(url=image_url)

        else:
            embed = discord.Embed(
                title=title,
                url=link,
                description=summary,
                color=discord.Color.dark_grey()
            )
            embed.set_author(name="R00ty", icon_url=R00TY_AVATAR_URL)
            embed.set_thumbnail(url=image_url)

        return embed

    # -------------------------------
    # Boucle périodique RSS
    # -------------------------------
    @tasks.loop(minutes=10.0)
    async def fetch_rss(self):
        """Vérifie et publie les nouveaux articles RSS dans les bons salons."""
        await self.bot.wait_until_ready()
        logger.info("🔍 Vérification des flux RSS...")

        for category, info in RSS_CONFIG.items():
            channel = discord.utils.get(self.bot.get_all_channels(), name=info["channel_name"])
            if not channel:
                logger.warning(f"⚠️ Salon introuvable : {info['channel_name']}")
                continue

            for feed_url in info["feeds"]:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:
                        link = entry.link
                        if link not in self.posted_links:
                            embed = self.create_embed(category, entry, feed.feed.get("title", "Flux inconnu"))
                            await channel.send(embed=embed)
                            self.posted_links.append(link)
                            self._save_posted_links()
                            await asyncio.sleep(1.5)
                except Exception as e:
                    logger.error(f"Erreur dans {feed_url}: {e}")

        logger.info("✅ Vérification RSS terminée.")

    @fetch_rss.before_loop
    async def before_fetch_rss(self):
        """Attend que le bot soit prêt avant de démarrer la tâche."""
        await self.bot.wait_until_ready()
        logger.info("🕒 Démarrage de la tâche périodique RSS stylisée...")

    # -------------------------------
    # Commande manuelle
    # -------------------------------
    @commands.command(name="rssnow")
    async def rssnow(self, ctx):
        """Force la vérification immédiate des flux RSS."""
        await ctx.reply("🔄 Vérification manuelle des flux RSS en cours...")
        await self.fetch_rss()
        await ctx.reply("✅ Vérification terminée.")


# -------------------------------
# Enregistrement du Cog
# -------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(RSSCog(bot))
