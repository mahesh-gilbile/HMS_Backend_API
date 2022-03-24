from flask import Blueprint , request, jsonify
from . import mysql
import json
from datetime import datetime , date
import time

student = Blueprint('student',__name__)

@student.route('/',methods=['GET'])
def timepass():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("CREATE DATABASE databasename")
        mysql.connection.commit()
        return jsonify("Hey")

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

#student time cha add karaicha aahe
@student.route('/scanMess/<Std_ID>',methods=['POST'])
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
        if(n == None):
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

@student.route('/mahesh',methods=['GET'])
def mahesh():
    if request.method == 'GET':
        return "Hey"

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
