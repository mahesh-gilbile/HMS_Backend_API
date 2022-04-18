from crypt import methods
from logging.config import valid_ident
import uuid
from flask import Blueprint , request, jsonify
from . import mysql
import json
from datetime import datetime , date , timedelta
import time

student = Blueprint('student',__name__)

@student.route('/<ID>',methods=['GET'])
def get_Student(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student_details as sd , student_education_details as sed WHERE sd.Student_ID = %s AND sed.Student_ID = sd.Student_ID",(ID))
        result = cur.fetchone()
    return jsonify(data = result)

@student.route('/change_pass/<ID>',methods=['POST'])
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
            cur = mysql.connection.cursor()
            cur.execute("SELECT Password FROM student_details WHERE student_ID = %s",(ID))
            curr_pass = cur.fetchone()
            curr_pass = curr_pass[0]
            if curr_pass == currentPassword:
                cur.execute("UPDATE student_details SET Password = %s WHERE student_ID = %s",(newPassword,ID))
                cur.close()
                return jsonify("Password Update Successfully!")            
            else:
                cur.close()
                return jsonify("Incorrect Current Password!") , 404 

@student.route('/guardian_details/<ID>',methods=['GET'])
def guardian_Details(ID):
    if request.method == 'GET': 
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM guardian_details WHERE Student_ID = %s",(ID))
        data = cur.fetchone()
        return jsonify(data) , 200
    
@student.route('/getRoomDetails/<Std_ID>',methods=['GET'])
def getRoomDetails(Std_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Room_ID FROM room_allocate WHERE Student_ID = %s",(Std_ID))
        Room_ID = cur.fetchone()
        cur.execute("SELECT Wing_Name FROM wing_details WHERE (Wing_ID = (SELECT Wing_ID FROM room_details WHERE Room_ID = %s))",(Room_ID))
        Wing_Name = cur.fetchone()
        cur.execute("SELECT sd.Student_ID , sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Email , sd.Mobile_Number FROM student_details AS sd , room_allocate AS ra WHERE ra.Room_ID = %s AND ra.Student_ID != %s AND sd.Student_ID = ra.Student_ID",(Room_ID , Std_ID))
        data = cur.fetchall()
        Room_Mate_Details = [dict(zip(("Student_ID","First_Name","Middle_Name","Last_Name","Email","Mobile_Number"),vv)) for vv in data]
        return jsonify({"Room_ID" : Room_ID[0] , "Wing_Name" : Wing_Name[0] , "Room_Mate_Details" : Room_Mate_Details}) , 200

@student.route('/scanForMess/<Std_ID>',methods=['POST'])
def scanQRMess(Std_ID):
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        Date = data.get('Date')
        Type = data.get('Type')
        Password1 = data.get('Password1')
        Password2 = data.get('Password2')
        cur = mysql.connection.cursor()
        cur.execute("SELECT QR_ID , MessStaff_ID FROM qr_for_mess WHERE (Date = %s AND QR_Code1 = %s AND QR_Code2 = %s AND Type = %s)",[Date , Password1 , Password2 , Type])
        n = cur.fetchone()
        type = CheckQRTime()
        if(n == None or type == 'Nothing'):
            return jsonify("Not Valid QR Code") , 404
        else:
            cur.execute("SELECT * FROM mess_entry WHERE (Student_ID = %s AND Date = %s AND Type = %s)",[Std_ID , Date , Type])
            messEntryData = cur.fetchone()
            if(messEntryData == None):
                QR_ID = n[0]
                MessStaff_ID = n[1]
                Date1 = getTodayformattedDate()
                Time1 = getTime()
                cur.execute("INSERT INTO `mess_entry`(`QR_ID`,`Student_ID`,`Time`,`Date`,`Type`) VALUES(%s, %s, %s, %s, %s)",(QR_ID , Std_ID , Time1 , Date1, Type))
                mysql.connection.commit()
                cur.execute("SELECT First_Name , Last_Name FROM mess_staff WHERE MessStaff_ID = %s",(MessStaff_ID))
                data1 = cur.fetchone()
                fn = data1[0]
                ln = data1[1]
                return jsonify({"MessStaffName": fn + ln , "Date" : Date1 , "Time" : Time1 , "Type" : Type}) , 200
            else:
                QR_ID = messEntryData[1]
                Time1 = messEntryData[3]
                Date1 = messEntryData[4]
                Type = messEntryData[5]
                cur.execute("SELECT First_Name , Last_Name FROM mess_staff WHERE (MessStaff_ID = (SELECT MessStaff_ID FROM qr_for_mess WHERE QR_ID = %s))",[QR_ID])
                data1 = cur.fetchone()
                fn = data1[0]
                ln = data1[1]
                return jsonify({"MessStaffName": fn + " " +  ln , "Date" : Date1 , "Time" : Time1 , "Type" : Type}) , 200



def CheckQRTime() -> str:
    t = time.localtime()
    hour = int(time.strftime("%H", t))
    if(hour >= 9 and hour < 11):
        value = 'Breakfast'
    elif(hour >= 13 and hour < 16):
        value = 'Lunch'
    elif(hour >= 20 and hour < 23):
        value = 'Dinner'
    else:
        value = "Nothing"
    return value

@student.route('/scanForGate/<Std_ID>',methods=['POST','GET'])
def ScanForGate(Std_ID):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        data = request.data
        data = json.loads(data)
        Password1 = data.get('Password1')
        Password2 = data.get('Password2')
        date = data.get('Date')
        Time = data.get('Time')
        d = datetime.today() - timedelta(hours=0, minutes=60)
        nowTime = d.strftime('%H:%M:%S')
        #QR Code is valid for one hour check
        if(nowTime > Time):
            cur.execute("SELECT QR_ID FROM qr_for_gate WHERE Time = %s AND Date = %s AND QR_Code1 = %s AND QR_Code2 = %s",(Time,date,Password1,Password2))
            n = cur.fetchone()
            #Qr Code is exist or not
            nowDate = getTodayformattedDate()
            if(n == None or nowDate != date):
                return jsonify("QR Code is Wrong...!") , 404
            else:
                QR_ID = n[0]
                cur.execute("SELECT hostel_id FROM wing_details WHERE wing_id = (SELECT wing_id FROM room_details WHERE room_id = (SELECT room_id FROM room_allocate WHERE student_id = %s))",(Std_ID))
                data = cur.fetchone()
                hostelIDFromStudentID = data[0]
                cur.execute("SELECT Hostel_id FROM gate_info WHERE gate_id = (SELECT gate_id FROM qr_for_gate WHERE qr_id = %s)",[QR_ID])
                data1 = cur.fetchone()
                hostelIDFromQRID = data1[0]
                #Check if student are from same hostel when scaning QR
                if(hostelIDFromQRID == hostelIDFromStudentID):
                    cur.execute("SELECT MAX(QR_Scan_ID) FROM `gate_entry` WHERE student_id = %s",(Std_ID))
                    data2 = cur.fetchone()
                    #check last status of student
                    if(data2[0] == None):
                        date = getTodayformattedDate()
                        Time = getTimewithNanoSec()
                        cur.execute("INSERT INTO `gate_entry`(`QR_ID`, `Student_ID`, `Time`, `Date`, `Status`) VALUES (%s,%s,%s,%s,'IN')",(QR_ID,Std_ID,Time,date))
                        mysql.connection.commit()
                        cur.execute("SELECT * FROM gate_entry WHERE Student_ID = %s AND Time = %s AND Date = %s AND QR_ID = %s",(Std_ID , Time , date , QR_ID))
                        d = cur.fetchall()
                        QR_Info = [dict(zip(("QrScanID","QRID","StudentID","Time","Date","Status"),vv)) for vv in d]
                        cur.execute("SELECT First_Name , Middle_Name , Last_Name FROM security_guard WHERE SecurityGuard_ID = (SELECT SecurityGuard_ID FROM qr_for_gate WHERE qr_id = %s)",[QR_ID])
                        d2 = cur.fetchall()
                        SecurityGuard_Name = [dict(zip(("FirstName","MiddleName","LastName"),vv)) for vv in d2]
                        return jsonify({"QR_Info" : QR_Info[0] , "SecurityGuardName" : SecurityGuard_Name[0]}) , 200
                    else:
                        lastQRScanID = data2[0]
                        cur.execute("SELECT Status FROM gate_entry WHERE QR_Scan_ID = %s",[lastQRScanID])
                        data3 = cur.fetchone()
                        lastStatus = data3[0]
                        date = getTodayformattedDate()
                        Time = getTimewithNanoSec()
                        #Adding Status according to last status
                        if(lastStatus == 'IN'):
                            cur.execute("INSERT INTO `gate_entry`(`QR_ID`, `Student_ID`, `Time`, `Date`, `Status`) VALUES (%s,%s,%s,%s,'OUT')",(QR_ID,Std_ID,Time,date))
                            mysql.connection.commit()
                        elif(lastStatus == 'OUT'):
                            cur.execute("INSERT INTO `gate_entry`(`QR_ID`, `Student_ID`, `Time`, `Date`, `Status`) VALUES (%s,%s,%s,%s,'IN')",(QR_ID,Std_ID,Time,date))
                            mysql.connection.commit()
                        cur.execute("SELECT * FROM gate_entry WHERE Student_ID = %s AND Time = %s AND Date = %s AND QR_ID = %s",(Std_ID , Time , date , QR_ID))
                        d = cur.fetchall()
                        QR_Info = [dict(zip(("QrScanID","QRID","StudentID","Time","Date","Status"),vv)) for vv in d]
                        cur.execute("SELECT First_Name , Middle_Name , Last_Name FROM security_guard WHERE SecurityGuard_ID = (SELECT SecurityGuard_ID FROM qr_for_gate WHERE qr_id = %s)",[QR_ID])
                        d2 = cur.fetchall()
                        SecurityGuard_Name = [dict(zip(("FirstName","MiddleName","LastName"),vv)) for vv in d2]
                        return jsonify({"QR_Info" : QR_Info[0] , "SecurityGuardName" : SecurityGuard_Name[0]}) , 200
                else:
                    cur.execute("SELECT hostel_Name FROM hostel_details WHERE hostel_id=%s",(hostelIDFromQRID))
                    data = cur.fetchone()
                    HostelName = data[0]
                    errorMessage = "Your not From " + HostelName
                    return jsonify(errorMessage) , 404
        else:
            return jsonify("QR Code is Expired....!") , 404
    elif request.method == 'GET':
        time = getTimewithNanoSec()
        return jsonify(time)

@student.route('/getMessHistory/<ID>',methods=['GET'])
def getMessHistory(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT me.Date , me.Type , mh.Food_Menu , mh.MS_ID FROM mess_entry as me , mess_history as mh , qr_for_mess as qr WHERE me.Student_ID = 3 AND me.QR_ID = qr.QR_ID AND qr.Mess_ID = mh.Mess_ID AND me.Date = mh.Date AND me.Type = mh.Food_Type")
        d = cur.fetchall()
        data = [dict(zip(("Date","Type","FoodMenu","MSID"),vv)) for vv in d]
        return jsonify(data)

@student.route('/getGateHistory/<ID>',methods=['GET'])
def getGateHistory(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM gate_entry WHERE student_id = %s",(ID))
        d = cur.fetchall()
        data = [dict(zip(("QRSacnID","QRID","StudentID","Time","Date","Status"),vv)) for vv in d]
        return jsonify(data)


###Common Function

#Get Today's date in format
def getTodayformattedDate() -> str:
    currentDate = date.today()
    formatted = currentDate.strftime('%d/%m/%Y')
    return formatted

def getTime() -> str:
    t = time.localtime()
    now = time.strftime("%H:%M:%S",t)
    return now

def getTimewithNanoSec() -> str:
    now = datetime.now()
    time = now.strftime("%H:%M:%S:%f")
    return time

#Gate_Entry ID
def getUniqueID(string) -> str:
    str1 = uuid.uuid4()
    str2 = str(str1)[:8]
    return (string + '_'+ str2)

