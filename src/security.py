from multiprocessing import connection
from flask import Blueprint , request , jsonify
# from typer import confirm
from . import mysql
import json

security = Blueprint('security',__name__)

@security.route('/<ID>',methods=['GET'])
def get_Security(ID):
    if request.method == 'GET':
        curr = mysql.connection.cursor()
        curr.execute("SELECT * FROM security_guard WHERE SecurityGuard_ID = %s",(ID))
        result = curr.fetchone()
        return jsonify(result)

@security.route('/change_pass/<ID>',methods=['POST'])
def change_pass(ID):
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        currentPassword = data.get('currentPassword')
        newPassword = data.get('newPassword')
        confirmPassword = data.get('reEnterNewPassword')
        if newPassword != confirmPassword:
            return jsonify("Please Check your Password!") , 404
        else:
            curr = mysql.connection.cursor()
            curr.execute("SELECT Password FROM security_guard WHERE SecurityGuard_ID = %s",(ID))
            curr_pass = curr.fetchone()
            curr_pass = curr_pass[0]
            if curr_pass == currentPassword:
                curr.execute("UPDATE security_guard SET Password = %s WHERE SecurityGuard_ID = %s",(newPassword,ID))
                return jsonify("Password Update Successfully!")
            else:
                curr.close()
                return jsonify("Incorrect Current Password") , 404
