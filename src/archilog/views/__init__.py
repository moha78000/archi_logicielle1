from dataclasses import dataclass
from flask import Flask
from archilog import config
from archilog.views.web_ui import web_ui
from dotenv import load_dotenv
from api import api , spec


load_dotenv()


def create_app():
    app = Flask(__name__)
        

    # Enregistrement des blueprints
    app.register_blueprint(web_ui)
    app.register_blueprint(api)
    
    # Configuration de l'application
    app.config["SECRET_KEY"] = config.SECRET_KEY  

    spec.register(api)
    
        
    return app
