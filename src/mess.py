from crypt import methods
from ntpath import join
from MySQLdb import Time
from flask import Blueprint , request , jsonify
from . import mysql
import json
from datetime import datetime , date
import time
import uuid
import string
import random

mess = Blueprint('mess',__name__)

@mess.route('/<ID>',methods=['GET'])
def get_Mess(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mess_staff WHERE MessStaff_ID = %s",(ID))
        result = cur.fetchone()
        return jsonify(result)


@mess.route('/change_pass/<ID>',methods=['POST'])
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
            cur.execute("SELECT Password FROM mess_staff WHERE MessStaff_ID = %s",(ID))
            curr_pass = cur.fetchone()
            curr_pass = curr_pass[0]
            if curr_pass == currentPassword:
                cur.execute("UPDATE mess_staff SET Password = %s WHERE MessStaff_ID = %s",(newPassword , ID))
                cur.close()
                return jsonify("Password Update Successfully!")
            else:
                cur.close()
                return jsonify("Incorrect Current Password!"), 404    

@mess.route('/mess_menu/<Std_ID>',methods=['GET'])
def mess_Menu(Std_ID):
    if request.method == 'GET':
        print(Std_ID)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `mess_menu` WHERE (Mess_ID = (SELECT Mess_ID FROM mess_info WHERE (Hostel_ID = (SELECT Hostel_ID FROM wing_details WHERE (wing_ID = (SELECT wing_id FROM room_details WHERE (room_ID = ( SELECT room_id from room_allocate WHERE (student_ID = %s)))))))))",(Std_ID))
        data = cur.fetchall()
        data1 = [dict(zip(("MM_ID","Mess_ID","Food_Menu","Food_Type","Day","Food_Description"),vv)) for vv in data] 
        return jsonify(data1) , 200

@mess.route("/specificDay_menu/<Std_ID>",methods=['GET'])
def specificDayMenu(Std_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        day = datetime.today().strftime('%A')
        cur.execute("SELECT * FROM `mess_menu` WHERE (Mess_ID = (SELECT Mess_ID FROM mess_info WHERE (Hostel_ID = (SELECT Hostel_ID FROM wing_details WHERE (wing_ID = (SELECT wing_id FROM room_details WHERE (room_ID = ( SELECT room_id from room_allocate WHERE (student_ID = %s)))))))) && Day = %s)",(Std_ID , day))
        data = cur.fetchall()
        data1 = [dict(zip(("MM_ID","Mess_ID","Food_Menu","Food_Type","Day","Food_Description"),vv)) for vv in data]
        return jsonify(data1), 200 

#13/02/2022
@mess.route("/specificType_menu/<MessStaff_ID>/<Type>",methods=['GET'])
def getSpecificType(MessStaff_ID,Type):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mess_menu WHERE Food_Type = %s AND (Mess_ID = (SELECT Mess_ID FROM mess_info WHERE MessStaff_ID = %s))",(Type , MessStaff_ID))
        d = cur.fetchall()
        data = [dict(zip(("MM_ID","Mess_ID","Food_Menu","Food_Type","Day","Food_Description"),vv)) for vv in d]
        return jsonify({"Mess_Menu" : data}) , 200

@mess.route("/singleMenu/<ID>",methods=['GET','PUT'])
def getSingleMenu(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mess_menu WHERE MM_ID = %s",[ID])
        d = cur.fetchall()
        data = [dict(zip(("MM_ID","Mess_ID","Food_Menu","Food_Type","Day","Food_Description"),vv)) for vv in d]
        return jsonify({"Mess_Menu" : data}) , 200
    if request.method == 'PUT':
        data = request.data
        data = json.loads(data)
        Food_Menu = data.get('Food_Menu')
        Food_Description = data.get('Food_Description')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE mess_menu SET `Food_Menu` = %s , `Food_Description` = %s WHERE MM_ID = %s",(Food_Menu, Food_Description, ID))
        mysql.connection.commit()
        return jsonify("Updated Successfully...!") , 200

@mess.route("/CheckDayStarted/<MessStaff_ID>",methods=['GET'])
def CheckDay(MessStaff_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `mess_history` WHERE Date = %s AND (Mess_ID = (SELECT Mess_ID FROM `mess_info` WHERE MessStaff_ID = %s))",(getTodayformattedDate() , MessStaff_ID))
        check = cur.fetchone()
        if(check == None):
            return jsonify(False)
        else:
            return jsonify(True)

@mess.route("/startDay/<MessStaff_ID>",methods=['GET'])
def StartDay(MessStaff_ID):
    if request.method == 'GET':
        day = datetime.today().strftime('%A')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `mess_history` WHERE Date = %s AND (Mess_ID = (SELECT Mess_ID FROM `mess_info` WHERE MessStaff_ID = %s))",(getTodayformattedDate() , MessStaff_ID))
        check = cur.fetchone()
        if(check == None):
            cur.execute("SELECT * FROM `mess_menu` WHERE Day = %s AND (Mess_ID = (SELECT Mess_ID FROM `mess_info` WHERE MessStaff_ID = %s))",([day] , MessStaff_ID))
            d = cur.fetchall()
            data = [dict(zip(("MM_ID","Mess_ID","Food_Menu","Food_Type","Day","Food_Description"),vv)) for vv in d]
            for d in data:
                cur.execute("INSERT INTO `mess_history`(`MS_ID`, `Mess_ID`, `Food_Menu`, `Food_Type`, `Day`, `Food_Description`, `Date`) VALUES (%s, %s, %s, %s, %s, %s, %s)",(getUniqueIDMS("MS",d.get('MM_ID')), d.get('Mess_ID'), d.get('Food_Menu'), d.get('Food_Type'), d.get('Day'), d.get('Food_Description'), getTodayformattedDate()))
                mysql.connection.commit()
            return jsonify("Start Your Day..!") , 200
        else:
            return jsonify("Day Already Started..!") , 200


#06-03-2022
#Generate QR Code As per Time
@mess.route("/GenerateQRForMess/<Mess_Staff_ID>",methods=['GET'])
def GenerateQRMess(Mess_Staff_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `mess_history` WHERE Date = %s AND (Mess_ID = (SELECT Mess_ID FROM `mess_info` WHERE MessStaff_ID = %s))",(getTodayformattedDate() , Mess_Staff_ID))
        check = cur.fetchone()
        if(check == None):
            return jsonify("Please Start Your Day") , 404
        else:
            type = CheckQRTime()
            if type == "Nothing":
                return jsonify(type) , 404
            else:
                date = getTodayformattedDate()
                time = getTime()
                cur.execute("SELECT mess_id FROM mess_info WHERE messstaff_id = %s",(Mess_Staff_ID))
                data = cur.fetchone()
                Mess_ID = data[0]
                cur.execute("SELECT QR_ID FROM qr_for_mess WHERE Date = %s AND Type = %s AND Mess_ID = %s",(date , type , Mess_ID))
                data1 = cur.fetchone()
                if data1 == None:
                    QR_ID = str(getUniqueID('QR'))
                    QR_Code1 = generateRandomPassword(20)
                    QR_Code2 = generateRandomPassword(25)
                    cur.execute("INSERT INTO `qr_for_mess`(`QR_ID`, `Mess_ID`, `MessStaff_ID`, `Time`, `Date`, `QR_Code1`, `Qr_Code2`, `Type`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(QR_ID , Mess_ID , Mess_Staff_ID , time , date , QR_Code1 , QR_Code2 , type))
                    mysql.connection.commit()
                else:
                    QR_ID = data1            
                cur.execute("SELECT * FROM `qr_for_mess` WHERE `QR_ID` = %s",[QR_ID])
                d = cur.fetchall()
                data = [dict(zip(("QR_ID","Mess_ID","MessStaff_ID","Time","Date","QR_Code1","QR_Code2","Type"),vv)) for vv in d]
                return jsonify(data)

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

###Common Function

#Get Present Time

def getTime() -> str:
    t = time.localtime()
    now = time.strftime("%H:%M:%S",t)
    return now

#Get Unique Id for Mess History
def getUniqueIDMS(string,MM_ID):
    str1 = uuid.uuid4()
    str2 = str(str1)[:8]
    return (string + MM_ID + str2)

#Get Unique Id for QR Code of Mess
def getUniqueID(string) -> str:
    str1 = uuid.uuid4()
    str2 = str(str1)[:8]
    return (string + '_'+ str2)

#Get Today's date in format
def getTodayformattedDate() -> str:
    currentDate = date.today()
    formatted = currentDate.strftime('%d/%m/%Y')
    return formatted

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
