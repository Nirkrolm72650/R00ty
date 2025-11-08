# utils/logger.py

import logging
import os
from datetime import datetime

def setup_logger():
    # Créer le dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)

    log_filename = datetime.now().strftime("logs/rootsphere_%Y-%m-%d.log")

    # Format des logs
    log_format = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configuration globale du logger
    logging.basicConfig(
        level=logging.INFO,               # Niveau de logs (DEBUG, INFO, WARNING, ERROR)
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler()       # Console
        ]
    )

    # Log d’initialisation
    logging.getLogger(__name__).info("✅ Logger initialisé.")
