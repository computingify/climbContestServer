# climb

## Installation
clone the deploy file:
<code>
wget https://raw.githubusercontent.com/computingify/climbContestServer/master/deployement/deploy_app.sh
</code>

enable executable
<code>
chmod +x /home/pi/deployement/deploy_app.sh
</code>

install
<code>
/home/pi/deployement/deploy_app.sh
</code>

### Certificates injection
In case of using headless machine, we need to made the first google sheet connection from a machine with embedded browser to obtain the token.pickle.
So copy all certificates from another machine to rapsi one:
From my Mac machine:
<code>
scp security/* token.pickle pi@<PI ADDRESS>:~/climbcontestserver/
</code>
be sure to have the *.pem files inside security folder

There Are 2 type of certificates:
- 1 for Android application https protocol
- 1 to connect to google sheet

## Update
From an host machine
<code>
chmod +x /home/pi/deployement/deploy_RPi.sh
./home/pi/deployement/deploy_RPi.sh
</code>

## Advance
### Start python virtual environnement
source venv/bin/activate

### Instalation
just install requirements.txt:
<code>
pip install -r requirements.txt
</code>

### Launch server side:
<code>
flask --app climb_contest/__init__.py --debug run
</code>

### Manually modify database
Use sqllitebrowser tool: https://sqlitebrowser.org
if the database is on ssh remote FS, follow this tuto: https://www.petergirnus.com/blog/how-to-use-sshfs-on-macosyes

# Here we are
To made it work follow this instruction to enable google sheet access:
https://developers.google.com/sheets/api/quickstart/go?hl=fr

Then you need to create a googlesheet and update the SPREADSHEET_ID inside google_sheets.py if you want to change the sheet.
Becareful to get the correct information from googlesheet fresh created:
The SPREADSHEET_ID you're using is set to 'contest'. However, the SPREADSHEET_ID should be the actual ID of your Google Spreadsheet, not the name.
Find the correct Spreadsheet ID:
Open your Google Sheets document.
In the URL, you will find something like this:
https://docs.google.com/spreadsheets/d/1aBcD_XYZ1234aBcD_XYZ5678/edit#gid=0
The part after /d/ and before /edit is your Spreadsheet ID:
1aBcD_XYZ1234aBcD_XYZ5678
Update your SPREADSHEET_ID:
SPREADSHEET_ID = '1aBcD_XYZ1234aBcD_XYZ5678'  # Replace with your actual Spreadsheet ID

After that you shoud be able to send the correct information to googlesheet by simulate API request using postman

# HTTPS

for developpement create a self signed certificat:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

Flask itself can serve HTTPS, but it's not suitable for production (use a WSGI server like gunicorn or uWSGI for production). For simplicity, here's how you can use Flask's built-in SSL support.
Shall do for the production:
Use gunicorn with HTTPS:
gunicorn --certfile cert.pem --keyfile key.pem -w 4 -b 0.0.0.0:5007 routes:app

# DEBUG

sudo systemctl restart climb_contest_server_app.service
sudo journalctl -fu climb_contest_server_app.service

# Use to deploy on hosted server
Store the token into base64 to use it on deployment server:
base64 -i token.pickle | pbcopy

# Googlesheet access
## 1st possibility
To be able to use the google sheet, the only way I find is to copy the Etienne's google sheet in ADN-Dev one. By the way, I can access to it in write mode.

## 2nd possibility (the best one)
Add adrien.jouve@adn-dev.fr as writer in shared options.
If it doesn't work, open writer mode to someone have the link.

# Unit Test

Only for unit test you need to install pytest to the virtual env
```
pip install pytest
```

To run unit test:
In CLI go to the project root
```
pytest -sv
```
Pytest will discover all the tests automatically and execute it.
-v for the test verbose
-s to show source code print call in command line interface

To run unit test only on a part of test
```
pytest tests/test_routes.py::test_check_climber -sv
```

## Lancer l'application Flask en local

Pour lancer ton application Flask localement, assure-toi d'être dans le dossier racine du projet et d'utiliser le bon module d'entrée.

Si ton fichier principal est `climb_contest/__init__.py` et que tu utilises une factory `create_app`, lance :

```
export FLASK_APP=climb_contest
export FLASK_ENV=development
flask run --debug
```

Ou en une seule ligne :
```
FLASK_APP=climb_contest FLASK_ENV=development flask run --debug
```

**Remarques :**
- Ne mets pas `:__init__.py` dans le nom du module.
- Le nom du module doit correspondre au dossier contenant le fichier `__init__.py` (ici `climb_contest`).
- Si tu veux utiliser un port spécifique :  
  `flask run --debug --port 5007`

## Utilisation de la table BlocScore pour la gestion des points

### 1. Mettre à jour la valeur d'un bloc lorsqu'un grimpeur réussit

À chaque réussite, il faut :
- Compter le nombre de grimpeurs ayant réussi ce bloc pour la catégorie donnée.
- Mettre à jour la valeur du bloc dans la table `BlocScore` (valeur = 1000 / nombre de grimpeurs).

Exemple en Python :

```python
from climb_contest.models import BlocScore, Success, Climber, db

def update_bloc_score(bloc_id, category):
    # Compte le nombre de grimpeurs ayant réussi ce bloc dans la catégorie
    count = (
        db.session.query(Success)
        .join(Climber, Success.climber_id == Climber.id)
        .filter(Success.bloc_id == bloc_id, Climber.category == category)
        .count()
    )
    if count == 0:
        value = 1000
    else:
        value = int(1000 / count)

    # Met à jour ou crée la valeur dans BlocScore
    bloc_score = BlocScore.query.filter_by(bloc_id=bloc_id, category=category).first()
    if not bloc_score:
        bloc_score = BlocScore(bloc_id=bloc_id, category=category, value=value)
        db.session.add(bloc_score)
    else:
        bloc_score.value = value
    db.session.commit()
    return value
```

### 2. Afficher la valeur d'un bloc

Pour afficher la valeur d'un bloc pour une catégorie :

```python
bloc_score = BlocScore.query.filter_by(bloc_id=bloc_id, category=category).first()
if bloc_score:
    print(f"Bloc {bloc_id} pour la catégorie {category} vaut {bloc_score.value} points")
else:
    print("Aucune valeur enregistrée pour ce bloc et cette catégorie")
```

### 3. Faire un classement par catégorie

Pour chaque grimpeur d'une catégorie, additionne les valeurs des blocs qu'il a réussis :

```python
from sqlalchemy import func

def classement_par_categorie(category):
    # Liste tous les grimpeurs de la catégorie
    climbers = Climber.query.filter_by(category=category).all()
    classement = []
    for climber in climbers:
        # Liste des succès du grimpeur
        successes = Success.query.filter_by(climber_id=climber.id).all()
        score_total = 0
        for success in successes:
            bloc_score = BlocScore.query.filter_by(bloc_id=success.bloc_id, category=category).first()
            if bloc_score:
                score_total += bloc_score.value
        classement.append((climber.name, score_total))
    # Trie par score décroissant
    classement.sort(key=lambda x: x[1], reverse=True)
    return classement

# Exemple d'affichage
for name, score in classement_par_categorie("U16 H"):
    print(f"{name}: {score} points")
```

---

**Résumé :**
- Mets à jour la valeur du bloc à chaque réussite avec `update_bloc_score`.
- Affiche la valeur d'un bloc avec une requête sur `BlocScore`.
- Calcule le classement par catégorie en additionnant les valeurs des blocs réussis pour chaque grimpeur.