import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response , abort
import archilog.models as models
import archilog.services as services
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
import os
import io
from werkzeug.utils import secure_filename



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

class CreateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=100)])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    category = StringField("Category", validators=[Optional(), Length(min=2, max=50)])
    submit = SubmitField("Valider") 

@web_ui.route("/create", methods=["GET", "POST"])
def create_entry_form():
    form = CreateForm()

    if form.validate_on_submit():  # Vérifier si le formulaire a été soumis avec des données valides
        name = form.name.data
        amount = form.amount.data
        category = form.category.data
        models.create_entry(name, amount, category)
        # Message de succès
        flash(f"Entrée créée: {name} ({amount}€) dans {category}", "success")

        
        
        # Rediriger vers la page d'accueil ou une autre page
        return redirect(url_for("web_ui.home"))

    return render_template("create.html", form=form)



class DeleteForm(FlaskForm):
    user_id = StringField("ID de l'entrée à supprimer", validators=[DataRequired()])
    submit = SubmitField("Supprimer")

@web_ui.route("/delete", methods=["GET", "POST"])
def delete_entry_form():
    form = DeleteForm()  # WTForms
    

    if form.validate_on_submit():
        user_id = form.user_id.data
        user_id = uuid.UUID(user_id)
        models.delete_entry(user_id)
        flash("Entrée supprimée avec succès.", "success")
        return redirect(url_for("web_ui.home"))

    return render_template("delete.html", form=form, entries= models.get_all_entries())



class UpdateForm(FlaskForm):
    id = StringField("ID", validators=[DataRequired()])
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=100)])
    amount = DecimalField("Montant", validators=[
        DataRequired(),
        NumberRange(min=0, message="Le montant doit être positif")
    ])
    category = StringField("Catégorie", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Mettre à jour")    

@web_ui.route("/update" , methods=["POST" , "GET"] )
def update_entry_form():
    form = UpdateForm()
    if form.validate_on_submit():
        
        try:
            entry_id = uuid.UUID(form.id.data)
            name = form.name.data
            amount = form.amount.data
            category = form.category.data

            models.update_entry(entry_id, name, amount, category)
            flash("Entrée mise à jour avec succès!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "error")

    return render_template("update.html", form=form, entries = models.get_all_entries())


@web_ui.route("/export_csv")
def export_csv():
    csv_file = services.export_to_csv()
    return Response(
        csv_file.getvalue(), 
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=export.csv"}
    )




@web_ui.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    if request.method == "GET":
        return render_template("import_csv.html")  # Affiche le formulaire d'import

    file = request.files.get("csv_file")
    
    if file and file.filename.endswith(".csv"):
        services.import_from_csv(file)
        flash("Fichier CSV importé avec succès!")
        return redirect(url_for("web_ui.home"))  # Redirige après succès

    flash("Le fichier doit être au format CSV.")
    return render_template("import_csv.html")  # Reste sur la page en cas d'erreur


@web_ui.get("/users/create")
def users_create_form():
    abort(500)
    return render_template("users_create_form.html")    

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect(url_for("web_ui.home"))