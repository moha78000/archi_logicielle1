import os 
from dataclasses import dataclass
from dotenv import load_dotenv
import logging 


load_dotenv()


# Configurer le logging
logging.basicConfig(
    level=logging.INFO,  # On affiche au minimum les messages INFO
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("activity.log"),  # Enregistre dans un fichier
        logging.StreamHandler()  # Affiche dans la console
    ]
)


@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool
    SECRET_KEY: str

config = Config(    
    DATABASE_URL=os.getenv("ARCHILOG_DATABASE_URL", ""),
    DEBUG=os.getenv("ARCHILOG_DEBUG", "False") == "True",
    SECRET_KEY=os.getenv("SECRET_KEY", "fallback_secret")  # Ajout de SECRET_KEY
)

