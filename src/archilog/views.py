import click
import uuid

import archilog.models as models
import archilog.services as services
from flask import Flask, render_template , request, redirect, url_for , send_file
from flask_sqlalchemy import SQLAlchemy

import os
from werkzeug.utils import secure_filename
import csv
import io


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # Connexion à la base de données SQLite
db = SQLAlchemy(app)

class Entry(db.Model): # Modèle de données de la table "entries"
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/hello/")   
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", name=name)


@app.route("/create")
def create_entry_form():
    return render_template("create.html")



@app.route("/create_entry", methods=["POST"])
def create_entry_route():
    # Récupérer les données du formulaire
    name = request.form["name"]
    amount = float(request.form["amount"])  # Convertir le montant en float
    category = request.form["category"]
    
    # Appeler la fonction pour insérer une nouvelle entrée dans la base de données
    models.create_entry(name, amount, category)
    
    print(f"Entrée crée avec le nom '{name}' et le montant {amount}.")
    return redirect(url_for("home"))  # Redirection vers la page d'accueil



@app.route("/entries")
def list_entries():
    entries = models.get_all_entries()  # Récupérer toutes les entrées
    return render_template("entries.html", entries=entries)




@app.route("/delete")
def delete_entry_form():
    entries = models.get_all_entries()  # Récupérer toutes les entrées

    return render_template("delete.html" , entries=entries)





@app.route("/delete_entry", methods=["POST"])
def delete_entry_route():
    # Récupérer les données du formulaire par l'id d'entrée
    id = request.form["id"]
    
    # Appeler la fonction pour supprimer une entrée dans la base de données à partir de son ID
    models.delete_entry(id)
    
    print(f"Entrée avec l'id '{id}' à été supprimée.")
    return redirect(url_for("home"))  # Redirection vers la page d'accueil



@app.route("/update")
def update_entry_form():
    return render_template("update.html")


@app.route("/update_entry", methods=["POST"])
def update_entry_route():
    id = request.form["id"]
    name = request.form["name"]
    amount = float(request.form["amount"])
    category = request.form["category"] if "category" in request.form else None # Vérifier si la catégorie est fournie

    # Appeler la fonction pour mettre à jour l'entrée
    models.update_entry(id, name, amount, category)

    print(f"Entrée avec l'ID {id} mise à jour.")
    return redirect(url_for("home"))  # Redirection vers la page d'accueil


# Spécifier un chemin absolu pour l'exportation du fichier CSV
EXPORT_DIR = os.path.join(os.getcwd(), 'exports')  # Crée un dossier 'exports' dans le répertoire de travail

# Assurer que le dossier existe
os.makedirs(EXPORT_DIR, exist_ok=True)

@app.route("/export_csv")
def export_csv():
    # Nom du fichier à télécharger
    file_name = "export.csv"
    
    file_path = services.export_to_csv(file_name)  # Appel de la fonction d'exportation

    # Retourner le fichier pour téléchargement
    return send_file(file_path, as_attachment=True)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Vérifier si le fichier est un CSV
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route pour afficher le formulaire d'importation
@app.route('/import_csv', methods=['GET'])
def import_csv_form():
    return render_template('import_csv.html')

# Route pour gérer l'importation du CSV
@app.route('/import_csv', methods=['POST'])
def import_csv():
    file = request.files['csv_file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Appeler la fonction d'importation des données CSV
        models.import_csv_to_db(file_path)
        
        return redirect(url_for('home'))  # Rediriger vers la page d'accueil après importation
    return 'Fichier invalide, veuillez télécharger un fichier CSV.'



@click.group()
def cli():
    pass


@cli.command()
def init_db():
    models.init_db()


@cli.command()
@click.option("-n", "--name", prompt="Name")
@click.option("-a", "--amount", type=float, prompt="Amount")
@click.option("-c", "--category", prompt="Category")
def create(name: str, amount: float, category: str | None):
    models.create_entry(name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def get(id: uuid.UUID):
    click.echo(models.get_entry(id))


@cli.command()
@click.option("--as-csv", is_flag=True, help="Ouput a CSV string.")
def get_all(as_csv: bool):
    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        click.echo(models.get_all_entries())


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    services.import_from_csv(csv_file)


@cli.command()
@click.option("--id", type=click.UUID, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id: uuid.UUID, name: str, amount: float, category: str | None):
    models.update_entry(id, name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def delete(id: uuid.UUID):
    models.delete_entry(id)


@cli.command()
@click.argument("csv_file", type=click.Path(writable=True))
def export_csv(csv_file):
    services.export_to_csv("csv_file")   
    