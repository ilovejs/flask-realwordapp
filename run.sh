export CONDUIT_SECRET='11223344'
export FLASK_APP=autoapp.py
export FLASK_DEBUG=1

# pip install -r requirements/dev.txt
flask db init
flask db migrate
flask db upgrade
