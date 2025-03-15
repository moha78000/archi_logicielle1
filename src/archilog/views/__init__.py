from dataclasses import dataclass
from flask import Flask
from archilog.views.web_ui import web_ui
from archilog.views.cli import cli

@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool
    SECRET_KEY: str

config = Config(
    DATABASE_URL="sqlite:///data.db",
    DEBUG=True,
    SECRET_KEY="secret01"

)



def create_app():
    app = Flask(__name__)


    # Enregistrement des blueprints
    app.register_blueprint(web_ui)
    app.config.from_object(config)
    app.cli.add_command(cli)  # Ici on attache Click à l'application Flask
    return app
