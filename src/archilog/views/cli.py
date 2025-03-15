import click
import uuid
from archilog import models, services


@click.group()
def cli():
    """Commandes pour gérer l'application"""
    pass

@cli.command()
def init_db():
    """Initialiser la base de données"""
    models.init_db()
    click.echo("Base de données initialisée.")

@cli.command()
@click.option("-n", "--name", prompt="Nom")
@click.option("-a", "--amount", type=float, prompt="Montant")
@click.option("-c", "--category", prompt="Catégorie")
def create(name: str, amount: float, category: str | None):
    """Créer une nouvelle entrée"""
    models.create_entry(name, amount, category)
    click.echo(f"Entrée '{name}' créée avec succès.")

@cli.command()
@click.option("--id", required=True, type=click.UUID)
def get(id: uuid.UUID):
    """Obtenir une entrée par ID"""
    entry = models.get_entry(id)
    click.echo(entry if entry else "Entrée non trouvée.")

@cli.command()
@click.option("--as-csv", is_flag=True, help="Exporter en format CSV")
def get_all(as_csv: bool):
    """Afficher toutes les entrées"""
    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        click.echo(models.get_all_entries())

@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    """Importer des entrées depuis un fichier CSV"""
    services.import_from_csv(csv_file)
    click.echo("Importation terminée.")

@cli.command()
@click.option("--id", type=click.UUID, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id: uuid.UUID, name: str, amount: float, category: str | None):
    """Mettre à jour une entrée"""
    models.update_entry(id, name, amount, category)
    click.echo(f"Entrée {id} mise à jour.")

@cli.command()
@click.option("--id", required=True, type=click.UUID)
def delete(id: uuid.UUID):
    """Supprimer une entrée"""
    models.delete_entry(id)
    click.echo(f"Entrée {id} supprimée.")

@cli.command()
@click.argument("csv_file", type=click.Path(writable=True))
def export_csv(csv_file):
    """Exporter les données en CSV"""
    services.export_to_csv(csv_file)
    click.echo(f"Données exportées dans {csv_file}")

if __name__ == "__main__":
    cli()
