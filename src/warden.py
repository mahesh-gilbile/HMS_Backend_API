from flask import Blueprint , request , jsonify
from . import mysql
import json

warden = Blueprint('warden',__name__)

@warden.route('/<ID>',methods=['GET'])
def get_Warden(ID):
    if request.method == 'GET':
        curr = mysql.connection.cursor()
        curr.execute("SELECT * FROM warden_details WHERE Warden_ID = %s",(ID))
        result = curr.fetchone()
        return jsonify(result)


@warden.route('/change_pass/<ID>',methods=['POST'])
def change_pass(ID):
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        currentPassword = data.get('currentPassword')
        newPassword = data.get('newPassword')
        confirmPassword = data.get('reEnterNewPassword')
        if newPassword != confirmPassword:
            return jsonify("Please Check Your Password!") , 404
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT Password FROM warden_details WHERE Warden_ID = %s",(ID))
            curr_pass = cur.fetchone()
            curr_pass = curr_pass[0]
            if curr_pass == currentPassword:
                cur.execute("UPDATE warden_details SET Password = %s WHERE Warden_ID = %s",(newPassword , ID))
                cur.close()
                return jsonify("Password Update Successfully!")
            else:
                cur.close()
                return jsonify("Incorrect Current Password!") , 404