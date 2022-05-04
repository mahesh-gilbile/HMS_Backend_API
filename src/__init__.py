from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'hms'
    
    
    mysql = MySQL(app)

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .auth import auth
    from .student import student
    from .mess import mess
    from .security import security
    from .warden import warden
    from .secretory import secretory
    from .admin import admin
    app.route("/",methods=['GET'])
    def hey():
        return "Hey"

    app.register_blueprint(auth , url_prefix='/auth')
    app.register_blueprint(student , url_prefix='/student')
    app.register_blueprint(mess , url_prefix='/mess')
    app.register_blueprint(security , url_prefix="/security")
    app.register_blueprint(warden , url_prefix='/warden')
    app.register_blueprint(secretory , url_prefix='/secretory')
    app.register_blueprint(admin , url_prefix='/admin')

    return app

 
