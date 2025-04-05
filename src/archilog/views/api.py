from flask import Blueprint , jsonify , Response
from flask_httpauth import HTTPTokenAuth
from spectree import SpecTree , SecurityScheme
from pydantic import BaseModel, Field, constr
import archilog.models as models
from archilog.services import export_to_csv
from uuid import UUID





api = Blueprint("api", __name__, url_prefix="/api")
auth = HTTPTokenAuth(scheme='Bearer')
spec = SpecTree(
"flask",
security_schemes=[
    SecurityScheme(
        name="bearer_token",
        data={"type": "http", "scheme": "bearer"}
    )
],
security=[{"bearer_token": []}]
)


tokens = {
"secret-token-1": "john",
"secret-token-2": "susan"
}


@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    return None





# Exemple de route de test pour vérifier l'authentification
@api.route("/test", methods=["GET"])
@auth.login_required
def test_auth():
    return jsonify({"message": f"Hello {auth.current_user()}!"}), 200



class CreateEntry(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Le nom de l'entrée")
    amount: float = Field(gt=0, description="Le montant de l'entrée")
    category: str = Field(min_length=2, max_length=50, description="La catégorie de l'entrée")


@api.route("/user", methods=["POST"])
@auth.login_required
@spec.validate(tags=["user"])   
def create_user(json: CreateEntry):
    models.create_entry(json.name, json.amount, json.category)
    # Ici, json contient un objet de type CreateEntry
    return jsonify({"message": f"User {json.name} created with amount {json.amount}"}), 201


class UpdateEntry(BaseModel):
    id: UUID  = Field(description="ID de l'entrée à mettre à jour")
    name: str = Field(min_length=2, max_length=100, description="Nouveau nom de l'entrée")  
    amount: float = Field(gt=0, description="Nouveau montant de l'entrée")
    category: str = Field(min_length=2, max_length=50, description="Nouvelle catégorie de l'entrée")


@api.route("/user/<id>", methods=["PUT"])
@auth.login_required
@spec.validate(tags=["user"])
def update_user(id: UUID, json: UpdateEntry):
    models.update_entry(json.id ,json.name, json.amount, json.category)
    # Ici, json contient un objet de type UpdateEntry
    return jsonify({"message": f"User {id} updated"}), 200



class DeleteEntry(BaseModel):
    id: UUID = Field(description="ID de l'entrée à supprimer")

@api.route("/user/<id>", methods=["DELETE"])
@auth.login_required
@spec.validate(tags=["user"])
def delete_user(id: UUID , json: DeleteEntry):
    models.delete_entry(json.id)
    # Ici, json contient l'ID de l'utilisateur à supprimer
    return jsonify({"message": f"User {id} deleted"}), 204    



@api.route("/user", methods=["GET"])
@auth.login_required
@spec.validate(tags=["user"])
def get_entries():
    # Récupérer toutes les entrées depuis la base de données
    entries = models.get_all_entries()
    
    # Convertir les résultats en un format JSON pour la réponse
    entries_data = [{
        "id": entry.id,
        "name": entry.name,
        "amount": entry.amount,
        "category": entry.category
    } for entry in entries]
    
    # Retourner les entrées en format JSON
    return jsonify(entries_data), 200


@api.route("/products/export", methods=["GET"])
@spec.validate(tags=["api"])
@auth.login_required
def export_csv_api():
    csv_data = export_to_csv()
    return Response(csv_data.getvalue(), content_type="text/csv")



@api.route('/')
@auth.login_required
def index():
    return "Hello, {}!".format(auth.current_user())


