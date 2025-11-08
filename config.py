import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

BOT_NAME = "R00ty"
GUILD_IDS = []
R00TY_AVATAR_URL = "https://imgur.com/a/J5sJwuS"

# --- Configuration RSS par catégorie ---
RSS_CONFIG = {
    "Cybersecurity": {
        "channel_name": "veille-cyber",
        "feeds": [
            "https://www.cert.ssi.gouv.fr/feed/",
            "https://feeds.feedburner.com/TheHackersNews",
            "https://www.zdnet.fr/feeds/rss/actualites/cybersecurite/"
        ]
    },
    "Vulnerabilites": {
        "channel_name": "veille-vulnérabilités",
        "feeds": [
            "https://vulners.com/rss",
            "https://cvefeed.io/rss.xml",
            "https://www.exploit-db.com/rss.xml"
            "https://www.zerodayinitiative.com/rss/upcoming/",
            "https://www.zerodayinitiative.com/rss/published/"
        ]
    },
    "Sys-Linux": {
        "channel_name": "sys-linux",
        "feeds": [
            "https://www.debian.org/security/dsa-long.fr.rdf",
            "https://linuxfr.org/news.atom"
        ]
    },
    "Sys-Windows": {
        "channel_name": "sys-windows",
        "feeds": [
            "https://msrc.microsoft.com/update-guide/rss",
            "https://www.bleepingcomputer.com/feed/"
        ]
    },
    "Veille-Tech": {
        "channel_name": "veille-tech",
        "feeds": [
            "https://www.it-connect.fr/tag/rss/",
            "https://www.wired.com/feed/tag/ai/latest/rss",
            "https://www.theverge.com/rss/index.xml",
        ]
    }
}