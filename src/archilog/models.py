import uuid
from dataclasses import dataclass
from sqlalchemy import create_engine, Table, Column, String, Float, MetaData
from sqlalchemy import Uuid
# Configuration de la base de données SQLite
db_url = "sqlite:///data.db"
engine = create_engine(db_url, echo=True)  # echo=True pour afficher les requêtes SQL exécutées
metadata = MetaData()

# Définir la table "entries"
entries_table = Table(
    "entries",
    metadata,               
    Column("id", Uuid ,  primary_key=True, default=uuid.uuid4), # UUID stocké en string pour que SQLite puisse récupérer l'id
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category", String, nullable=True),
)


@dataclass
class Entry:
    id: uuid.UUID
    name: str
    amount: float
    category: str | None


# Créer la table dans la base de données si elle n'existe pas encore
def init_db():
    metadata.create_all(engine)
    print("Database and table created (if not already existing).")

# Insérer une nouvelle entrée dans la table "entries"
def create_entry(name: str, amount: float, category: str | None = None):
    stmt = entries_table.insert().values(name=name, amount=amount, category=category)
    with engine.begin() as conn:
        conn.execute(stmt)
    print(f"Entrée crée avec le nom '{name}' et le montant {amount}.")

# Récupérer toutes les entrées contenues dans la table "entries"
def get_all_entries():
    with engine.connect() as conn:
        result = conn.execute(entries_table.select()).fetchall()
        # Convertir chaque ligne en une instance de Entry
        entries = [Entry(id=row[0], name=row[1], amount=row[2], category=row[3]) for row in result]

    print(entries)
    return entries

def delete_entry(id : uuid.UUID) -> None: 
    """
    Fonction pour supprimer une entrée par son UUID.
    :param id: L'ID de l'entrée à supprimer, qui peut être une chaîne ou un UUID.
    """

    
    # Suppression de l'entrée par l'UUID
    stmt = entries_table.delete().where(entries_table.c.id == id)  # Assurez-vous que l'ID est une chaîne

    with engine.begin() as conn:
        conn.execute(stmt)

    print(f"L'entrée avec l'ID {id} a été supprimée.")
        

def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None = None):
    
    # Création de la requête de mise à jour
    stmt = entries_table.update().where(entries_table.c.id == id).values(name=name, amount=amount, category=category)

    # Exécution de la requête
    with engine.begin() as conn:
        conn.execute(stmt)
        print(f"L'entrée avec l'ID {id} a été mise à jour.")

def get_entry(id: uuid.UUID):
    with engine.connect() as conn:
        result = conn.execute(entries_table.select().where(entries_table.c.id == id)).fetchone()
        if result:
            # Retourner un dictionnaire avec les données de l'entrée
            return {
                "id": result.id,
                "name": result.name,
                "amount": result.amount,
                "category": result.category
            }
        else:
            return None  # Si l'entrée n'est pas trouvée, retourner None
# Exemple d'utilisation de la fonction principale
if __name__ == "__main__":
    # Initialisation de la base de données
    init_db()


    # Récupérer toutes les entrées
    print("\n Toutes les entrées dans la database:")
    get_all_entries()
