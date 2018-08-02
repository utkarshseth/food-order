import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
# mail = Mail(app)

# mail_settings = {
#     "MAIL_SERVER": 'smtp.gmail.com',
#     "MAIL_PORT": 465,
#     "MAIL_USE_TLS": False,
#     "MAIL_USE_SSL": True,
#     "MAIL_USERNAME": os.environ['EMAIL_USER'],
#     "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
# }


app.config['MAIL_SERVER'] =               os.environ.get('MAIL_SERVER',          'smtp.gmail.com')
app.config['MAIL_USERNAME'] =         os.environ.get('MAIL_USERNAME',     'EMAIL_USER')
app.config['MAIL_PASSWORD'] =         os.environ.get('MAIL_PASSWORD',     'EMAIL_PASS')
app.config['MAIL_PORT'] =              int(os.environ.get('MAIL_PORT',         '465'))
app.config['MAIL_USE_TLS'] =        int(os.environ.get('MAIL_USE_TLS',  False))
app.config['MAIL_USE_SSL'] =        int(os.environ.get('MAIL_USE_SSL',  True))





# app.config.update(mail_settings)
mail = Mail(app)

from blog import routes