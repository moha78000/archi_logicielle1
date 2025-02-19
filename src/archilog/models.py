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
    Column("id", Uuid ,  primary_key=True, default=uuid.uuid4),
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
        result = conn.execute(stmt)
    print(f"Entry '{name}' created with amount {amount}.")

# Récupérer toutes les entrées de la table "entries"
def get_all_entries():
    with engine.connect() as conn:
        result = conn.execute(entries_table.select()).fetchall()
        for row in result:
            print(f"ID: {row['id']}, Name: {row['name']}, Amount: {row['amount']}, Category: {row['category']}")

def delete(id : uuid.UUID ):
    stmt = entries_table.update().where(entries_table.c.id == id )
    print("Suppresion de l'id réussie" )      

# Exemple d'utilisation de la fonction principale
if __name__ == "__main__":
    # Initialisation de la base de données
    init_db()


    # Récupérer toutes les entrées
    print("\n Toutes les entrées dans la database:")
    get_all_entries()
