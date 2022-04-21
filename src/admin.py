from flask import Blueprint , request , jsonify
from . import mysql
import json
import uuid

admin = Blueprint('admin',__name__)

@admin.route('/<ID>',methods=['GET'])
def get_Admin(ID):
    if request.method == 'GET':
        curr = mysql.connection.cursor()
        curr.execute("SELECT * FROM admin WHERE Admin_ID = %s",(ID))
        result = curr.fetchone()
        return jsonify(result)

@admin.route('/change_pass/<ID>',methods=['POST'])
def change_Password(ID):
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
            cur.execute("SELECT Password FROM admin WHERE Admin_ID = %s",(ID))
            curr_pass = cur.fetchone()
            curr_pass = curr_pass[0]
            if curr_pass == currentPassword:
                cur.execute("UPDATE admin SET Password = %s WHERE Admin_ID = %s",(newPassword , ID))
                mysql.connection.commit()
                cur.close()
                return jsonify("Password Update Successfully!")
            else:
                cur.close()
                return jsonify("Incorrect Current Password!"), 404    


@admin.route('/LeaveDecision/<ID>',methods=['GET','POST'])
def LeaveDecision(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT l.ID , l.Staff_Type , l.From_Date , l.To_Date , l.Day , l.Reason , l.Status , l.Decision_takenby_type , l.Staff_ID , l.Decison_takenby_ID , l.Decision_takenby_Name , s.First_Name , s.Middle_Name , s.Last_Name FROM leaves as l , secretory as s WHERE l.Staff_Type = 'Secretory' AND l.Staff_ID = s.Secretory_ID")
        d1 = cur.fetchall()
        data1 = [dict(zip(("ID","StaffType","FromDate","ToDate","Day","Reason","Status","DecisionTakenByType","StaffID","DecisionTakenByID","DecisionTakenByName" ,"First_Name","Middle_Name","Last_Name"),vv)) for vv in d1]
        cur.execute("SELECT l.ID , l.Staff_Type , l.From_Date , l.To_Date , l.Day , l.Reason , l.Status , l.Decision_takenby_type , l.Staff_ID , l.Decison_takenby_ID , l.Decision_takenby_Name , w.First_Name , w.Middle_Name , w.Last_Name FROM leaves as l , warden_details as w WHERE l.Staff_Type = 'Warden' AND l.Staff_ID = w.Warden_ID")
        d2 = cur.fetchall()
        data2 = [dict(zip(("ID","StaffType","FromDate","ToDate","Day","Reason","Status","DecisionTakenByType","StaffID","DecisionTakenByID","DecisionTakenByName" ,"First_Name","Middle_Name","Last_Name"),vv)) for vv in d2]
        data = data1 + data2
        return jsonify(data)
    elif request.method == 'POST':
        data = request.data
        data = json.loads(data)
        l_ID = data.get('ID')
        Status = data.get('Status')
        DecisionTakenByType = data.get('DecisionTakenByType')
        cur = mysql.connection.cursor()
        cur.execute("SELECT CONCAT(First_Name ,' ' , Middle_Name ,' ' , Last_Name) as Full_Name FROM admin WHERE Admin_ID = %s",(ID))
        name = cur.fetchone()
        cur.execute("UPDATE leaves SET Status = %s , Decision_takenby_type = %s , Decison_takenby_ID = %s , Decision_takenby_Name = %s WHERE ID = %s",(Status , DecisionTakenByType , ID , name , l_ID))
        mysql.connection.commit()
        return jsonify("Status Updated Successfully....!")

@admin.route('/aboutSecretory',methods=['GET','POST','PUT'])
def aboutSecretory():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM secretory")
        d = cur.fetchall()
        data = [dict(zip(("SecretoryID","FirstName","MiddleName","LastName","Age","Gender","Gmail","MobileNo","DOB","Address"),vv)) for vv in d]
        return jsonify(data)
    elif request.method == 'POST':
        data = request.data
        data = json.loads(data)
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        age = data.get('age')
        gender = data.get('gender')
        email = data.get('email')
        mobileno = data.get('mobileNo')
        dob = data.get('dob')
        add = data.get('add')
        password = '1234'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `secretory`(`First_Name`, `Middle_Name`, `Last_Name`, `Age`, `Gender`, `Email`, `Mobile_Number`, `DOB`, `Address`, `Password`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(fn,mn,ln,age,gender,email,mobileno,dob,add,password))
        mysql.connection.commit()
        return jsonify("Secretory Information Added Successfully....!") , 200
    elif request.method == 'PUT':
        data = request.data
        data = json.loads(data)
        sid = data.get('id')
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        gender = data.get('gender')
        mobileno = data.get('mobileNo')
        add = data.get('add')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `secretory` SET `First_Name`= %s,`Middle_Name`= %s,`Last_Name`= %s,`Gender`= %s,`Mobile_Number`= %s,`Address`= %s WHERE secretory_id = %s",(fn, mn, ln, gender, mobileno, add, sid))
        mysql.connection.commit()
        return jsonify("Secretory Information Updated Successfully....!") , 200


@admin.route('/aboutWarden',methods=['GET','POST','PUT'])
def aboutWarden():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM warden_details")
        d = cur.fetchall()
        data = [dict(zip(("WardenID","FirstName","MiddleName","LastName","Age","Gender","Gmail","MobileNo","DOB","Address"),vv)) for vv in d]
        return jsonify(data)
    elif request.method == 'POST':
        data = request.data
        data = json.loads(data)
        warden_ID = getUniqueID("WD")
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        age = data.get('age')
        gender = data.get('gender')
        email = data.get('email')
        mobileno = data.get('mobileNo')
        dob = data.get('dob')
        add = data.get('add')
        password = '1234'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `warden_details`(`warden_ID`,`First_Name`, `Middle_Name`, `Last_Name`, `Age`, `Gender`, `Email`, `Mobile_Number`, `DOB`, `Address`, `Password`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(warden_ID,fn,mn,ln,age,gender,email,mobileno,dob,add,password))
        mysql.connection.commit()
        return jsonify("Warden Informtion Added Successfully....!") , 200
    elif request.method == 'PUT':
        data = request.data
        data = json.loads(data)
        sid = data.get('id')
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        gender = data.get('gender')
        mobileno = data.get('mobileNo')
        add = data.get('add')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `warden_details` SET `First_Name`= %s,`Middle_Name`= %s,`Last_Name`= %s,`Gender`= %s,`Mobile_Number`= %s,`Address`= %s WHERE warden_id = %s",(fn, mn, ln, gender, mobileno, add, sid))
        mysql.connection.commit()
        return jsonify("Warden Information Updated Successfully....!") , 200



@admin.route('/aboutMess',methods=['GET','POST','PUT'])
def aboutMess():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mess_staff")
        d = cur.fetchall()
        data = [dict(zip(("MessStaffID","FirstName","MiddleName","LastName","Age","Gender","Gmail","MobileNo","DOB","Address"),vv)) for vv in d]
        return jsonify(data)
    elif request.method == 'POST':
        data = request.data
        data = json.loads(data)
        ID = getUniqueID("MS")
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        age = data.get('age')
        gender = data.get('gender')
        email = data.get('email')
        mobileno = data.get('mobileNo')
        dob = data.get('dob')
        add = data.get('add')
        password = '1234'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `mess_staff`(`MessStaff_ID`,`First_Name`, `Middle_Name`, `Last_Name`, `Age`, `Gender`, `Email`, `Mobile_Number`, `DOB`, `Address`, `Password`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(ID,fn,mn,ln,age,gender,email,mobileno,dob,add,password))
        mysql.connection.commit()
        return jsonify("Mess Staff Informtion Added Successfully....!") , 200
    elif request.method == 'PUT':
        data = request.data
        data = json.loads(data)
        sid = data.get('id')
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        gender = data.get('gender')
        mobileno = data.get('mobileNo')
        add = data.get('add')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `mess_staff` SET `First_Name`= %s,`Middle_Name`= %s,`Last_Name`= %s,`Gender`= %s,`Mobile_Number`= %s,`Address`= %s WHERE MessStaff_id = %s",(fn, mn, ln, gender, mobileno, add, sid))
        mysql.connection.commit()
        return jsonify("Mess Staff Information Updated Successfully....!") , 200


@admin.route('/aboutSecurity',methods=['GET','POST','PUT'])
def aboutSecurity():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM security_guard")
        d = cur.fetchall()
        data = [dict(zip(("SecurityGuardID","FirstName","MiddleName","LastName","Age","Gender","Gmail","MobileNo","DOB","Address"),vv)) for vv in d]
        return jsonify(data)
    elif request.method == 'POST':
        data = request.data
        data = json.loads(data)
        ID = getUniqueID("SG")
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        age = data.get('age')
        gender = data.get('gender')
        email = data.get('email')
        mobileno = data.get('mobileNo')
        dob = data.get('dob')
        add = data.get('add')
        password = '1234'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `security_guard`(`SecurityGuard_ID`,`First_Name`, `Middle_Name`, `Last_Name`, `Age`, `Gender`, `Email`, `Mobile_Number`, `DOB`, `Address`, `Password`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(ID,fn,mn,ln,age,gender,email,mobileno,dob,add,password))
        mysql.connection.commit()
        return jsonify("Security Guard Information Added Successfully....!") , 200
    elif request.method == 'PUT':
        data = request.data
        data = json.loads(data)
        sid = data.get('id')
        fn = data.get('fn')
        mn = data.get('mn')
        ln = data.get('ln')
        gender = data.get('gender')
        mobileno = data.get('mobileNo')
        add = data.get('add')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `security_guard` SET `First_Name`= %s,`Middle_Name`= %s,`Last_Name`= %s,`Gender`= %s,`Mobile_Number`= %s,`Address`= %s WHERE SecurityGuard_ID = %s",(fn, mn, ln, gender, mobileno, add, sid))
        mysql.connection.commit()
        return jsonify("Security Guard Information Updated Successfully....!") , 200

@admin.route('/getEmails/<role>',methods=['GET'])
def getEmails(role):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        if role == 'Warden':
            cur.execute("SELECT email FROM warden_details")
            email = cur.fetchall()
        elif role == 'Security':
            cur.execute("SELECT email FROM security_guard")
            email = cur.fetchall()
        elif role == 'Mess':
            cur.execute("SELECT email FROM mess_staff")
            email = cur.fetchall()
        elif role == 'Secretory':
            cur.execute("SELECT email FROM secretory")
            email = cur.fetchall()
        data = [dict(zip(("e"),vv)) for vv in email]
        return jsonify(data)

#Unique ID
def getUniqueID(string) -> str:
    str1 = uuid.uuid4()
    str2 = str(str1)[:8]
    return (string + '_'+ str2)