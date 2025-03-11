import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import archilog.models as models
import archilog.services as services
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

@web_ui.route("/create")
def create_entry_form():
    return render_template("create.html")

@web_ui.route("/create_entry", methods=["POST"])
def create_entry_route():
    name = request.form["name"]
    amount = float(request.form["amount"])
    category = request.form["category"]
    models.create_entry(name, amount, category)
    return redirect(url_for("web_ui.home"))

@web_ui.route("/delete")
def delete_entry_form():
    entries = models.get_all_entries()
    return render_template("delete.html", entries=entries)

@web_ui.route("/delete_entry/<uuid:user_id>", methods=["POST"])
def delete_entry_route(user_id):
    models.delete_entry(user_id)
    return redirect(url_for("web_ui.home"))

@web_ui.route("/update")
def update_entry_form():
    return render_template("update.html")

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
