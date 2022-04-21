from flask import Blueprint, request , jsonify
from . import mysql
import MySQLdb
import json

auth = Blueprint('auth',__name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        id = None
        data = request.data
        data = json.loads(data)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        cur = mysql.connection.cursor()
        if role == 'Student':
            cur.execute("SELECT Student_ID FROM student_details WHERE Email = %s AND Password = %s",(username , password))
            id = cur.fetchone()
            if(id == None):
                id = None
        elif role == 'Warden':
            cur.execute("SELECT Warden_ID FROM warden_details WHERE Email = %s AND Password = %s",(username , password))
            id = cur.fetchone()
            if(id == None):
                id = None
        elif role == 'Security':
            cur.execute("SELECT SecurityGuard_ID FROM security_guard WHERE Email = %s AND Password = %s",(username , password))
            id = cur.fetchone()
            if(id == None):
                id = None
        elif role == 'Mess':
            cur.execute("SELECT MessStaff_ID FROM mess_staff WHERE Email = %s AND Password = %s",(username , password))
            id = cur.fetchone()
            if(id == None):
                id = None
        elif role == 'Secretory':
            cur.execute("SELECT Secretory_ID FROM secretory WHERE Email = %s AND Password = %s",(username , password))
            id = cur.fetchone()
            if(id == None):
                id = None
        elif role == 'Admin':
            cur.execute("SELECT admin_ID FROM admin WHERE Email = %s AND Password = %s",(username , password))
            id = cur.fetchone()
            if(id == None):
                id = None
        cur.close()
        if(id != None):
            return jsonify(role = role , id = id[0]) , 200
        else:
            return jsonify("Email Id and Password is Incorrect") , 404