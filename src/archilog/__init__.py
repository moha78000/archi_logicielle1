from dataclasses import dataclass
from flask import Flask
from archilog.views import api, web_ui

@dataclass
class Config:
    DATABASE_URL: str
    DEBUG: bool

config = Config(
DATABASE_URL="sqlite:///data.db",
DEBUG=True
)



def create_app():
    app = Flask(__name__)


    # Enregistrement des blueprints
    app.register_blueprint(api)
    app.register_blueprint(web_ui)

    return app
