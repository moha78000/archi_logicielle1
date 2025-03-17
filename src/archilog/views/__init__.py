from dataclasses import dataclass
from flask import Flask
from archilog.views.web_ui import web_ui
from archilog.views.cli import cli
from dotenv import load_dotenv
import os

@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool

config = Config(
    DATABASE_URL=os.getenv("ARCHILOG_DATABASE_URL", ""),
    DEBUG=os.getenv("ARCHILOG_DEBUG", "False") == "True"

    

)



def create_app():
    app = Flask(__name__)
    
    load_dotenv()

    # Enregistrement des blueprints
    app.register_blueprint(web_ui)
     # Configuration de l'application
    app.config["SECRET_KEY"] = config.getenv("SECRET_KEY", "fallback_secret")
    app.cli.add_command(cli)  # Ici on attache Click à l'application Flask
    
    return app
