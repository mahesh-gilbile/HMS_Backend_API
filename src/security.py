from datetime import date
from multiprocessing import connection
import random
import string
import time
import uuid
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
                mysql.connection.commit()
                return jsonify("Password Update Successfully!")
            else:
                curr.close()
                return jsonify("Incorrect Current Password") , 404

@security.route('/leaves/<ID>',methods=['POST','GET'])
def leaves(ID):
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        fromDate = data.get('from')
        toDate = data.get('to')
        days = data.get('days')
        reason = data.get('reason')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `leaves`(`Staff_Type`, `From_Date`, `To_Date`, `Day`, `Reason`, `Status`,`Staff_ID`) VALUES ('Security',%s,%s,%s,%s,'Pending',%s)",(fromDate,toDate,days,reason,ID))
        mysql.connection.commit()
        return jsonify("Leaves Apply SuccessFully...!")
    elif request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `leaves` WHERE Staff_ID = %s AND Staff_Type = 'Security'",(ID))
        d = cur.fetchall()
        data = [dict(zip(("ID","StaffType","FromDate","ToDate","Day","Reason","Status","DescisionTakenByType","StaffID","DecisionTakenByID","DescisionTakenByName"),vv)) for vv in d]
        return jsonify(data)

@security.route('/getHostelName/<ID>',methods=['GET'])
def getHostelNameBySecurityID(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Gate_Name FROM gate_info WHERE Gate_ID = (SELECT Gate_ID FROM security_guard WHERE securityguard_ID = %s)",(ID))
        GateName = cur.fetchone()
        cur.execute("SELECT hostel_Name FROM hostel_details WHERE Hostel_ID = (SELECT Hostel_ID FROM gate_info WHERE Gate_ID = (SELECT Gate_ID FROM security_guard WHERE securityguard_ID = %s))",(ID))
        HostelName = cur.fetchone()
        return jsonify({"GateName" : GateName[0] , "HostelName" : HostelName[0]})

@security.route('/GenerateQRForGate/<Security_ID>',methods=['GET'])
def GenerateQRGate(Security_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Gate_ID FROM security_guard WHERE Securityguard_ID=%s",(Security_ID))
        data = cur.fetchone()
        Gate_ID = data[0]
        date = getTodayformattedDate()
        time = getTime()
        QR_ID = str(getUniqueID('QR'))
        QR_Code1 = generateRandomPassword(20)
        QR_Code2 = generateRandomPassword(25)
        cur.execute("INSERT INTO `qr_for_gate`(`QR_ID`, `Gate_ID`, `SecurityGuard_ID`, `Time`, `Date`, `QR_Code1`, `QR_Code2`) VALUES (%s,%s,%s,%s,%s,%s,%s)",(QR_ID,Gate_ID,Security_ID,time,date,QR_Code1,QR_Code2))
        mysql.connection.commit()
        cur.execute("SELECT * FROM qr_for_gate WHERE QR_ID = %s",[QR_ID])
        d = cur.fetchall()
        qr_data = [dict(zip(("QR_ID","Gate_ID","SecurityGuard_ID","Time","Date","QR_Code1","QR_Code2"),vv)) for vv in d]
        return jsonify(qr_data[0])
    
@security.route('/getTodayQRHistory/<ID>',methods=['GET'])
def getTodayQRHistory(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        Date = getTodayformattedDate()
        cur.execute("SELECT sg.First_Name , sg.Middle_Name , sg.Last_Name , qr.QR_ID , qr.Time FROM qr_for_gate as qr , security_guard as sg WHERE (SELECT gate_id FROM security_guard WHERE securityguard_id = %s) AND qr.SecurityGuard_ID = sg.SecurityGuard_ID AND qr.Date = %s",(ID,Date))
        d = cur.fetchall()
        data = [dict(zip(("FirstName","MiddleName","LastName","QR_ID","Time"),vv)) for vv in d]
        return jsonify(data)

@security.route('/getQRIDInfo/<ID>',methods=['GET'])
def getQRIDInfo(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT ge.Time , ge.Status , sd.First_Name , sd.Middle_Name , sd.Last_Name FROM gate_entry as ge , student_details as sd WHERE ge.QR_ID = %s AND ge.student_id = sd.student_id",[ID])
        d = cur.fetchall()
        data = [dict(zip(("Time","Status","FirstName","MiddleName","LastName"),vv)) for vv in d]
        return jsonify(data)



###Common Function

#Get Present Time

def getTime() -> str:
    t = time.localtime()
    now = time.strftime("%H:%M:%S",t)
    return now

#Get Today's date in format
def getTodayformattedDate() -> str:
    currentDate = date.today()
    formatted = currentDate.strftime('%d/%m/%Y')
    return formatted

#Get Unique Id for QR Code of Mess
def getUniqueID(string) -> str:
    str1 = uuid.uuid4()
    str2 = str(str1)[:8]
    return (string + '_'+ str2)

#Generate Random Password for QR
def generateRandomPassword(length) -> str:
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    random.shuffle(characters)
    password = []
    for i in range(length):
        password.append(random.choice(characters))
    random.shuffle(password)
    data = "".join(password)
    return data
