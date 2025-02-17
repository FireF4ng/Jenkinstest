import logging

logging.basicConfig(
    filename="DevSec/logs/security.log",  # 🔥 Chemin du fichier log
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("security")

# 🔹 Intercepter les erreurs 429 et les enregistrer
from flask_limiter import Limiter
import os

limiter = Limiter(
    key_func=lambda: "global",
    storage_uri="memory://"
)

os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["NO_COLOR"] = "1"
