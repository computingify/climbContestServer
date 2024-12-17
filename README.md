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
flask --app main.py --debug run
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
gunicorn --certfile cert.pem --keyfile key.pem -w 4 -b 0.0.0.0:5007 main:app

# DEBUG

sudo systemctl restart climb_contest_server_app.service
sudo journalctl -fu climb_contest_server_app.service

# Use to deploy on hosted server
Store the token into base64 to use it on deployment server:
base64 -i token.pickle | pbcopy