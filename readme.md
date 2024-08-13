Step 1 : Install flask and virtualenv
pip install flask
pip install flask-mysqldb
py -2 -m pip install virtualenv

Step 2 : Create a virtual environment named flask_env
py -3 -m venv flask_env

Step 3 : Activate the environment
python -m venv .\flask_env\Scripts\activate

Step 4 : Setup flask app
setx FLASK_APP "app.py"

Step 5 : Run Flask
flask run --reload --debugger

Step 6 : Open localhost website

http://127.0.0.1:5000/search

http://127.0.0.1:5000/borrow

http://127.0.0.1:5000/checkin

http://127.0.0.1:5000/fine

http://127.0.0.1:5000/insertborrower

http://127.0.0.1:5000/insertbooks
 





