import click
import uuid
import archilog.models as models
import archilog.services as services
from flask import Flask, render_template , request, redirect, url_for, Response , flash
from tabulate import tabulate



import os
from werkzeug.utils import secure_filename
import io


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # Connexion à la base de données SQLite


@app.route("/")
def home():
    return render_template("home.html")



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


@app.route("/entry", methods=["GET"])
def get_entry():
    # Récupérer l'ID de la requête (c'est-à-dire l'ID entré dans le formulaire)
    id = request.args.get("id")
    if id:
        try:
            # Convertir l'ID en UUID
            entry_id = uuid.UUID(id)
            entry = models.get_entry(entry_id)  # Récupérer l'entrée dans la base de données
            
            if entry:
                return render_template("entry.html", entry=entry)  # Afficher l'entrée correspondante
            else:
                flash("Entrée non trouvée.")  # Si l'entrée n'est pas trouvée
                return redirect(url_for('home'))  # Rediriger vers la page d'accueil
        except ValueError:
            flash("ID invalide.")  # Si l'ID n'est pas valide
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))  # Rediriger vers la page d'accueil







@app.route("/delete")
def delete_entry_form():
    entries = models.get_all_entries()  # Récupérer toutes les entrées
    print(tabulate(entries, headers="keys"))

    return render_template("delete.html" , entries=entries)





@app.route("/delete_entry/<uuid:user_id>" , methods=["POST"])  
def delete_entry_route(user_id):
   # Appeler la fonction pour supprimer une entrée dans la base de données à partir de son ID
    models.delete_entry(user_id)
    
    print(f"Entrée avec l'id '{user_id}' à été supprimée.")
    return redirect(url_for("home"))  # Redirection vers la page d'accueil



@app.route("/update")
def update_entry_form():
    return render_template("update.html")


@app.route("/update_entry", methods=["POST"])
def update_entry_route():
    
    id = uuid.UUID(request.form["id"])  # Si id est un UUID valide
    name = request.form["name"]
    amount = float(request.form["amount"])
    category = request.form["category"] if "category" in request.form else None # Vérifier si la catégorie est fournie

    # Appeler la fonction pour mettre à jour l'entrée
    models.update_entry(id, name, amount, category)

    print(f"Entrée avec l'ID {id} mise à jour.")
    return redirect(url_for("home"))  # Redirection vers la page d'accueil


@app.route("/export_csv")
def export_csv():
    csv_file = services.export_to_csv()  # Appeler la fonction d'exportation des données en CSV
    
    return Response(csv_file.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=export.csv"}
                    ) # Retourner le fichier CSV en tant que réponse  




# Route pour afficher le formulaire d'importation
@app.route('/import_csv', methods=['GET'])
def import_csv_form():
    return render_template('import_csv.html')



# Définir le dossier où les fichiers seront téléchargés
UPLOAD_FOLDER = 'uploads'  # Remplace 'uploads' par le chemin complet si nécessaire
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}  # Autoriser uniquement les fichiers .csv

# Assure-toi que le dossier existe (si ce n'est pas déjà fait)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return filename.endswith('.csv')  # Vérifie si le fichier se termine par '.csv'    

# Route pour gérer l'importation du CSV
@app.route('/import_csv', methods=['POST'])
def import_csv():
    file = request.files['csv_file']  # Récupère le fichier téléchargé
    
    if file and allowed_file(file.filename):  # Vérifie si le fichier a une extension valide
        filename = secure_filename(file.filename)  # Sécuriser le nom du fichier pour éviter les attaques
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Dossier où on sauvegarde le fichier
        file.save(file_path)  # Sauvegarder le fichier dans le dossier

        # Ouvrir le fichier et l'envoyer à la fonction d'importation
        with open(file_path, 'r', encoding='utf-8') as f:
            # Créer un objet StringIO à partir du fichier
            csv_file = io.StringIO(f.read())
            services.import_from_csv(csv_file)  # Appeler la fonction d'importation


        
        return redirect(url_for('home'))  # Rediriger vers la page d'accueil après l'importation
    
    flash('Fichier invalide, veuillez télécharger un fichier CSV.')  # Message d'erreur
    return redirect(url_for('import_csv_form'))  # Rediriger vers la page de téléchargement du fichier



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
    services.export_to_csv(csv_file)   
    