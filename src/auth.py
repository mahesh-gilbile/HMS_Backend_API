from flask import Blueprint, request , jsonify
from . import mysql
import MySQLdb
import json

auth = Blueprint('auth',__name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return jsonify("Hey")
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


@auth.route('/getEmail',methods=['GET'])
def getEmail():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT semail FROM stdregister")
        d = cur.fetchall()
        registerEmail = [dict(zip(("e"),vv)) for vv in d]
        cur.execute("SELECT email FROM student_details")
        d1 = cur.fetchall()
        StdEmail = [dict(zip(("e"),vv)) for vv in d1]
        return jsonify({"RegisterEmail" : registerEmail , "StdEmail" : StdEmail})

@auth.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        print(data)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `stdregister`(`SFN`, `SMN`, `SLN`, `SGender`, `SAge`, `SCitizen`, `SEmail`, `SMobileNumber`, `SDOB`, `SAddress`, `SCategory`, `SCourse`, `SBranch`, `SCourseDuration`, `SYear`, `GFN`, `GMN`, `GLN`, `GRelation`, `GAge`, `GGender`, `GOccupation`, `GEmail`, `GMobileNumber`, `GDOB`, `GAddress`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data.get('StdFN') , data.get('StdMN') , data.get('StdLN') ,data.get('StdGender') , data.get('StdAge') , data.get('StdCitizen') ,data.get('StdEmail') ,data.get('StdMobileNumber') ,data.get('StdDOB') ,data.get('StdAddress') ,data.get('StdCategory') , data.get('StdCourse') ,data.get('StdBranch') ,data.get('StdCourseDuration') ,data.get('StdYear') , data.get('GuardianFN') , data.get('GuardianMN') , data.get('GuardianLN') , data.get('GuardianRelation') , data.get('GuardianAge') , data.get('GuardianGender') , data.get('GuardianOccupation') , data.get('GuardianEmail') , data.get('GuardianMobileNumber') , data.get('GuardianDOB') , data.get('GuardianAddress')))
        mysql.connection.commit()
        return jsonify("Student Register Successfully...!") , 200
