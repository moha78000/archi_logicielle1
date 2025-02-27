# archilog

A simple project for educational purpose.

```bash
$ pdm run archilog
Usage: archilog [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create
  delete
  get
  get-all
  import-csv
  init-db
  update
```

Course & examples : [https://kathode.neocities.org](https://kathode.neocities.org)

# Archi-Logicielle1 - Gestion des Entrées

## Description
Archi-Logicielle1 est une application Flask qui permet de gérer une base de données d'entrées. Ces entrées peuvent être des objets divers (voitures, téléphones, etc.) et sont stockées dans une base de données SQLite. L'application permet de créer, afficher, mettre à jour et supprimer des entrées via une interface web simple.

## Fonctionnalités
- **Créer une nouvelle entrée** : Ajouter une entrée avec un nom, un montant et une catégorie.
- **Voir toutes les entrées** : Afficher une liste des entrées existantes avec leurs détails.
- **Mettre à jour une entrée** : Modifier une entrée existante avec de nouvelles informations.
- **Supprimer une entrée** : Supprimer une entrée par son ID.
- **Importer un fichier CSV** : Importer des données depuis un fichier CSV dans la base de données.
- **Exporter un fichier CSV** : Exporter des données depuis la base de données vers un fichier généré.

