import csv
import dataclasses
import io

from archilog.models import create_entry, get_all_entries, Entry , engine , entries_table
from dataclasses import asdict
from sqlalchemy import select



def export_to_csv(csv_file: io.StringIO) -> None:
    with engine.connect() as conn:
        result = conn.execute(select(entries_table)).fetchall()  # Récupérer les entrées
        entries = [Entry(*row) for row in result]  # Convertir les tuples en objets Entry

    with open("export.csv", "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=[f.name for f in dataclasses.fields(Entry)])
        csv_writer.writeheader()
        for entry in entries:
            csv_writer.writerow(asdict(entry))  # Maintenant, entry est bien une instance de dataclass

    print("Exportation réussie !")

def import_from_csv(csv_file: io.StringIO) -> None:
    # L'ordre des colonnes attendues
    fieldnames = ["name", "amount", "category"]
    csv_reader = csv.DictReader(csv_file, fieldnames=fieldnames)
    
    next(csv_reader)
    
    for row in csv_reader:
        create_entry(
            name=row["name"],
            amount=float(row["amount"]),
            category=row["category"],
        )
