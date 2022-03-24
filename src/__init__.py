from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['MYSQL_HOST'] = 'sql6.freesqldatabase.com'
    app.config['MYSQL_USER'] = 'sql6480839'
    app.config['MYSQL_PASSWORD'] = 'y1uW3rfc1M'
    app.config['MYSQL_DB'] = 'sql6480839'


    mysql = MySQL(app)

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .auth import auth
    from .student import student
    from .mess import mess
    from .security import security
    from .warden import warden

    app.register_blueprint(auth , url_prefix='/auth')
    app.register_blueprint(student , url_prefix='/student')
    app.register_blueprint(mess , url_prefix='/mess')
    app.register_blueprint(security , url_prefix="/security")
    app.register_blueprint(warden , url_prefix='/warden')

    return app

 
