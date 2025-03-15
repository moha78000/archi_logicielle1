import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import archilog.models as models
import archilog.services as services

import os
import io
from werkzeug.utils import secure_filename
from archilog.views.forms import CreateForm , DeleteForm , UpdateForm

web_ui = Blueprint("web_ui", __name__, url_prefix="/")

@web_ui.route("/")
def home():
    return render_template("home.html")

@web_ui.route("/entries")
def list_entries():
    entries = models.get_all_entries()
    return render_template("entries.html", entries=entries)


@web_ui.route("/entry", methods=["GET"])
def get_entry():
    # Récupérer l'ID de la requête (depuis le formulaire)   
    entry_id = request.args.get("id")

    if entry_id:
        try:
            # Convertir l'ID en UUID
            entry_uuid = uuid.UUID(entry_id)
            entry = models.get_entry(entry_uuid)  # Récupérer l'entrée dans la base de données
            
            if entry:
                return render_template("entry.html", entry=entry)  # Afficher l'entrée trouvée
            else:
                flash("Entrée non trouvée.", "error")  # Si l'entrée n'est pas trouvée
        except ValueError:
            flash("ID invalide. Veuillez entrer un UUID valide.", "error")  # ID invalide
    else:
        flash("Veuillez entrer un ID.", "error")

    return redirect(url_for("web_ui.home"))  # Redirection vers la page d'accueil



@web_ui.route("/create", methods=["GET", "POST"])
def create_entry_form():
    form = CreateForm()

    if form.validate_on_submit():  # Vérifier si le formulaire a été soumis avec des données valides
        name = form.name.data
        amount = form.amount.data
        category = form.category.data

        # Message de succès
        flash(f"Entrée créée: {name} ({amount}€) dans {category}", "success")
        
        # Rediriger vers la page d'accueil ou une autre page
        return redirect(url_for("web_ui.home"))

    return render_template("create.html", form=form)

@web_ui.route("/create_entry", methods=["POST"])
def create_entry_route():
    name = request.form["name"]
    amount = float(request.form["amount"])
    category = request.form["category"]
    models.create_entry(name, amount, category)
    return redirect(url_for("web_ui.home"))

@web_ui.route("/delete", methods=["GET", "POST"])
def delete_entry_form():
    form = DeleteForm()  # WTForms
    
    entries = models.get_all_entries()  # Récupérer les entrées depuis la DB

    if form.validate_on_submit():
        user_id = form.user_id.data
        user_id = uuid.UUID(user_id)
        models.delete_entry(user_id)
        flash("Entrée supprimée avec succès.", "success")
        return redirect(url_for("web_ui.delete_entry_form"))

    return render_template("delete.html", form=form, entries=entries)


@web_ui.route("/delete_entry/<user_id>", methods=["POST"])
def delete_entry_route(user_id):
    models.delete_entry(user_id)
    return redirect(url_for("web_ui.home"))


@web_ui.route("/update")
def update_entry_form():
    form = UpdateForm()
    entries = models.get_all_entries()
    if form.validate_on_submit():
        try:
            entry_id = form.id.data
            name = form.name.data
            amount = form.amount.data
            category = form.category.data

            models.update_entry(entry_id, name, amount, category)
            flash("Entrée mise à jour avec succès!", "success")
            return redirect(url_for('web_ui.home'))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "error")

    return render_template("update.html", form=form, entries=entries)

@web_ui.route("/update_entry", methods=["POST"])
def update_entry_route():
    id = uuid.UUID(request.form["id"])
    name = request.form["name"]
    amount = float(request.form["amount"])
    category = request.form.get("category")

    models.update_entry(id, name, amount, category)
    return redirect(url_for("web_ui.home"))

@web_ui.route("/export_csv")
def export_csv():
    csv_file = services.export_to_csv()
    return Response(
        csv_file.getvalue(), 
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=export.csv"}
    )

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return filename.endswith(".csv")

@web_ui.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    if request.method == "GET":
        return render_template("import_csv.html")

    file = request.files["csv_file"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            csv_file = io.StringIO(f.read())
            services.import_from_csv(csv_file)
        
        return redirect(url_for("web_ui.home"))

    flash("Fichier invalide, veuillez télécharger un fichier CSV.")
    return redirect(url_for("web_ui.import_csv"))
