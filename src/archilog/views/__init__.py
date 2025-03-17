from dataclasses import dataclass
from flask import Flask
from archilog import config
from archilog.views.web_ui import web_ui
from archilog.views.cli import cli
from dotenv import load_dotenv



load_dotenv()


def create_app():
    app = Flask(__name__)
    

    # Enregistrement des blueprints
    app.register_blueprint(web_ui)
     # Configuration de l'application
    app.config["SECRET_KEY"] = config.SECRET_KEY  
    app.cli.add_command(cli)  # Ici on attache Click à l'application Flask
    
    return app
