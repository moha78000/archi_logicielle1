import csv
import dataclasses
import io

from archilog.models import create_entry, get_all_entries, Entry , engine , entries_table
from dataclasses import asdict
from sqlalchemy import select



def export_to_csv(csv_file_path=None):
    csv_file = io.StringIO() if csv_file_path is None else open(csv_file_path, "w", newline="", encoding="utf-8")

    with engine.connect() as conn:
        result = conn.execute(select(entries_table)).fetchall()
        entries = [Entry(*row) for row in result]

    csv_writer = csv.DictWriter(csv_file, fieldnames=[f.name for f in dataclasses.fields(Entry)])
    csv_writer.writeheader()

    for entry in entries:
        csv_writer.writerow(dataclasses.asdict(entry))

    if csv_file_path is None:
        csv_file.seek(0)  # Revenir au début pour Flask
        return csv_file
    else:
        csv_file.close()  # Fermer le fichier pour Click
        print(f"Exportation réussie vers {csv_file_path} !")
        

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
