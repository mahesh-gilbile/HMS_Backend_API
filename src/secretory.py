import re
from flask import Blueprint , request , jsonify
import json
from . import mysql

secretory = Blueprint('secretory',__name__)

@secretory.route('/<ID>',methods=['GET'])
def get_Secretory(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM secretory WHERE secretory_ID = %s",[ID])
        result = cur.fetchone()
        return jsonify(result)

@secretory.route('/change_pass/<ID>',methods=['POST'])
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
            cur.execute("SELECT Password FROM secretory WHERE secretory_ID = %s",(ID))
            curr_pass = cur.fetchone()
            curr_pass = curr_pass[0]
            if curr_pass == currentPassword:
                cur.execute("UPDATE secretory SET Password = %s WHERE secretory_ID = %s",(newPassword , ID))
                mysql.connection.commit()
                cur.close()
                return jsonify("Password Update Successfully!")
            else:
                cur.close()
                return jsonify("Incorrect Current Password!") , 404

@secretory.route('/leaves/<ID>',methods=['POST','GET'])
def leaves(ID):
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        fromDate = data.get('from')
        toDate = data.get('to')
        days = data.get('days')
        reason = data.get('reason')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `leaves`(`Staff_Type`, `From_Date`, `To_Date`, `Day`, `Reason`, `Status`,`Staff_ID`) VALUES ('Secretory',%s,%s,%s,%s,'Pending',%s)",(fromDate,toDate,days,reason,ID))
        mysql.connection.commit()
        return jsonify("Leaves Apply SuccessFully...!")
    elif request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `leaves` WHERE Staff_ID = %s AND Staff_Type = 'Secretory'",(ID))
        d = cur.fetchall()
        data = [dict(zip(("ID","StaffType","FromDate","ToDate","Day","Reason","Status","DescisionTakenByType","StaffID","DecisionTakenByID","DescisionTakenByName"),vv)) for vv in d]
        return jsonify(data)
