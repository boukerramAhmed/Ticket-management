
# Projet backend (FastAPI)

Ce document décrit la structure du projet backend, comment l'installer, lancer les tests et visualiser l'API.

## Structure du projet (aperçu)

Racine: `backend/`

- `app/` : code source principal de l'application FastAPI
	- `api/` : routeurs et points d'entrée API
		- `main.py` : assemble les routeurs 
		- `routes/` : modules de routes 
	- `config/` : configuration et paramètres 
	- `core/` : éléments centraux (DB, dépendances, utilitaires)
		- `database/` : moteur SQLAlchemy / sessions
	- `crud/` : opérations CRUD
	- `models/` : modèles ORM 
	- `schema/` : schémas Pydantic (request/response)
	- `services/` : logique métier

- `tests/` : tests unitaires et d'intégration
	- `conftest.py` : fixtures (DB en mémoire, client test)
	- `api/` : tests pour les routes API

- `requirements.txt` : dépendances Python
- `pytest.ini` : configuration des tests
- `docker-compose.yaml`, `Dockerfile`, `Taskfile.yml` : orchestration et commandes utiles




## Installation locale

#### Avec un environnement local

Prérequis : Python 3.11+ (le projet a été testé avec Python 3.13 dans l'environnement CI), `pip`, `virtualenv` recommandé.

1. Créez un environnement virtuel et activez-le :

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Variables d'environnement

```bash
export SQLALCHEMY_DATABASE_URL="sqlite+aiosqlite:///:memory:"
```
## Lancer l'application

Pour lancer l'API en local avec rechargement automatique :

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
## Lancer les tests

```shell
```

L'API sera alors disponible sur `http://localhost:8000`.


### Avec docker (<mark>Recommandé</mark>)

1. Docker

```bash
# lancer l'api
docker compose up -d
# visualizer les logs
docker compose logs -f ticket-api
``` 
2. avec Taskfile

```shell
# install Taskfile 
curl -1sLf 'https://dl.cloudsmith.io/public/task/task/setup.deb.sh' | sudo -E bash
apt install task


$ task
18:19 $ task
task: Available tasks for this project:
* black:           Vérifie le formatage du code avec black
* build:           build l'image du backend
* down:            Arrête tous les services Docker Compose
* flake8:          Vérifie le style du code avec flake8 et formate avec black
* load-data:       chargement des données
* logs:            Affiche les logs des services Docker
* restart:         Redémarre le conteneur ticket-api
* status:          Affiche le statut des services Docker
* test:            Lance les tests unitaires
* up:              Démarre tous les services Docker Compose

```

```shell
task up
task test
task flask8
```
#### Lancer les tests

Deux approches : local (direct) ou via les tâches Docker fournies.

Local (avec l'environnement virtuel activé) :

```bash
# lancer tous les tests
python -m pytest tests/ -v -xvs
```

Via Taskfile / Docker (comme utilisé dans CI):

```bash
# la repo contient un Taskfile.yml ; la tâche 'test' exécute les tests via docker compose
task test

# ou directement via docker-compose si vous préférez
docker compose up -d
docker compose exec  fastapi python -m pytest tests/ -v
```

## Visualiser l'API / documentation

FastAPI expose automatiquement la documentation interactive :

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

