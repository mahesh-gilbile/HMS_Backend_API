
from pickletools import read_uint1
from flask import Blueprint , request , jsonify
import json
import uuid
from . import mysql
from datetime import datetime , date , timedelta
import time

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

@secretory.route('getStdList',methods=['GET'])
def getStdList():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Student_ID , First_Name , Middle_Name , Last_Name , Email , Mobile_Number FROM student_details")
        d = cur.fetchall()
        data = [dict(zip(("StudentID" , "FirstName" , "MiddleName" , "LastName" , "Email" , "MobileNumber"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('StdFees/<ID>',methods=['GET'])
def stdFees(ID):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT count(me.QrScanID) , me.type , mf.Amount , count(me.QrScanID)*Amount as totalAmount FROM `mess_entry` as me , mess_fees as mf WHERE me.student_id = %s and me.Type = mf.Food_Type group by me.type;",(ID))
        d = cur.fetchall()
        messFees = [dict(zip(("Count" , "Type" , "Amount" , "TotalAmount"),vv)) for vv in d]
        cur.execute("SELECT * FROM hostel_fees WHERE student_id = %s",(ID))
        d1 = cur.fetchall()
        hostelFees = [dict(zip(("ID" , "StudentID" , "Amount" , "Year" , "JoiningDate"),vv)) for vv in d1]
        cur.execute("SELECT p.Payment_ID , p.Student_ID , p.Date , p.Time , p.Amount , p.Payment_Method , s.First_Name , s.Middle_Name , s.Last_Name FROM payment as p , secretory as s WHERE student_id = %s AND s.Secretory_ID = p.DoneBySecretoryID;",(ID))
        d2 = cur.fetchall()
        paidFees = [dict(zip(("PaymentID" , "StudentID" , "Date" , "Time" , "Amount" , "PaymentMethod" , "SecretoryFN", "SecretoryMN", "SecretoryLN"),vv)) for vv in d2]
        cur.execute("SELECT ra.Room_ID , wd.Wing_Name , hd.Hostel_Name , sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Email , sd.Mobile_Number FROM `room_allocate` as ra , room_details as rd , wing_details as wd , hostel_details as hd , student_details as sd WHERE ra.Student_ID = %s AND ra.Room_ID = rd.Room_ID AND rd.Wing_ID = wd.Wing_ID AND wd.Hostel_ID = hd.Hostel_ID AND ra.Student_ID = sd.Student_ID;",(ID))
        d3 = cur.fetchall()
        StdInfo = [dict(zip(("RoomID" , "WingName" , "HostelName" , "FirstName" , "MiddleName" , "LastName" , "Email" ,  "MobileNumber"),vv)) for vv in d3]
        return jsonify({"MessFees" : messFees , "HostelFees" : hostelFees , "FeesPaid" : paidFees , "StudentInfo" : StdInfo})

@secretory.route('payFees/<SecID>',methods=['POST'])
def payfees(SecID):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        data = request.data
        data = json.loads(data)
        StdID = data.get('StudentID')
        Amount = data.get('Amount')
        PaymentMethod = data.get('PaymentMethod') 
        cur.execute("INSERT INTO `payment`(`Student_ID`, `Date`, `Time`, `Amount`, `Payment_Method`, `DoneBySecretoryID`) VALUES (%s,%s,%s,%s,%s,%s)",(StdID , getTodayformattedDate() , getTime() , Amount , PaymentMethod , SecID))
        mysql.connection.commit()
        return jsonify("Payment Done Successfully...!") , 200

def getTodayformattedDate() -> str:
    currentDate = date.today()
    formatted = currentDate.strftime('%d/%m/%Y')
    return formatted

def getTime() -> str:
    t = time.localtime()
    now = time.strftime("%H:%M:%S",t)
    return now

@secretory.route('getRegistredStudent',methods=['GET'])
def getRgisteredStd():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT ID , SFN , SMN , SLN , SEmail , SmobileNumber  FROM stdregister")
        d = cur.fetchall()
        data = [dict(zip(("ID","SFN","SMN","SLN","SEmail","SMobileNumber",),vv)) for vv in d]
        return jsonify(data)

@secretory.route('getRegistredStudent/<ID>',methods=['GET'])
def getRgisteredStdInfo(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stdregister Where ID = %s",(ID))
        d = cur.fetchall()
        data = [dict(zip(("ID","SFN","SMN","SLN","SGender","SAge"	,"SCitizen"	,"SEmail","SMobileNumber","SDOB","SAddress","SCategory","SCourse","SBranch","SCourseDuration","SYear","GFN","GMN","GLN","GRelation","GAge","GGender","GOccupation","GEmail","GMobileNumber","GDOB","GAddress"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('approve',methods=['POST','GET'])
def approveStd():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        data = request.data
        data = json.loads(data)
        status = data.get('Status')
        stdID = data.get('StdID')
        if(status == 'True'):
            cur.execute("SELECT * FROM stdregister WHERE id = %s",(stdID))
            regData = cur.fetchone()
            stdNewID = str(getUniqueID("Std"))
            cur.execute("INSERT INTO `student_details`(`Student_ID`, `First_Name`, `Middle_Name`, `Last_Name`, `Gender`, `Age`, `Citizen`, `Email`, `Mobile_Number`, `DOB`, `Address`, `Password`, `Category`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'1234',%s)",(stdNewID , regData[1] , regData[2] , regData[3] , regData[4] , regData[5] , regData[6] , regData[7] , regData[8] , regData[9] , regData[10]  , regData[11]))
            mysql.connection.commit() 
            cur.execute("INSERT INTO `student_education_details`(`Student_ID`, `Course`, `Branch`, `Course_Duration`, `Year`) VALUES (%s,%s,%s,%s,%s)",(stdNewID , regData[12] , regData[13] , regData[14] , regData[15]))
            mysql.connection.commit()           
            cur.execute("INSERT INTO `guardian_details`(`Student_ID`, `First_Name`, `Middle_Name`, `Last_Name`, `Relation`, `Gender`, `Age`, `Occupation`, `Email`, `Mobile_Number`, `DOB`, `Address`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(stdNewID , regData[16] , regData[17] , regData[18] , regData[19] , regData[21] , regData[20] , regData[22] , regData[23] , regData[24] , regData[25]  , regData[26]))
            mysql.connection.commit()
            todayDate = getTodayformattedDate() 
            cur.execute("INSERT INTO `hostel_fees`(`Student_ID`, `Amount`, `Year`, `Joining_Date`,`Ending_Date`) VALUES (%s,%s,%s,%s,%s)",(stdNewID , data.get('Amount') , data.get('Year') , data.get('JoinDate') , data.get('EndDate')))
            mysql.connection.commit()
            cur.execute("DELETE FROM `stdregister` WHERE id = %s",(stdID))
            mysql.connection.commit()
            return jsonify("Admission Done") , 200
    if request.method == 'GET':
        data = str(getUniqueID("Std"))
        return jsonify(data)

@secretory.route('getRoomList',methods=['GET'])
def getRoomList():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT rd.Room_ID , rd.No_of_Beds , rd.Description , wd.Wing_Name , wd.Wing_ID , hd.Hostel_Name , hd.Hostel_ID FROM `room_details` as rd , wing_details as wd , hostel_details as hd WHERE rd.Wing_ID = wd.Wing_ID AND wd.Hostel_ID = hd.Hostel_ID;")
        d = cur.fetchall()
        data = [dict(zip(("RoomID" , "NoOfBeds" , "RoomDescription" , "WingName" , "WingID" , "HostelName" , "HostelID"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('getHostelList',methods=['GET'])
def getHostelList():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Hostel_ID , Hostel_Name FROM hostel_details")
        d = cur.fetchall()
        data = [dict(zip(("HostelID" , "HostelName"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('getWingList',methods=['GET'])
def getWingList():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT HOstel_ID , Wing_ID , wing_Name FROM wing_details")
        d = cur.fetchall()
        data = [dict(zip(("HostelID" , "WingID" , "WingName"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('addRoom',methods=['POST'])
def addRoom():
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        print(data)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `room_details`(`Wing_ID`, `No_of_Beds`, `Description`) VALUES (%s,%s,%s)",(data.get('WingID') , data.get('NoOfBeds') , data.get('Description')))
        mysql.connection.commit()
        return jsonify("Room Added Successfully")

@secretory.route('roomDetailsForAlt/<ID>',methods=['GET'])
def roomDetailsForALt(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT rd.Room_ID , rd.No_of_Beds , rd.Description , wd.Wing_Name , wd.Wing_ID , hd.Hostel_Name , hd.Hostel_ID FROM `room_details` as rd , wing_details as wd , hostel_details as hd WHERE rd.Wing_ID = wd.Wing_ID AND wd.Hostel_ID = hd.Hostel_ID AND rd.Room_ID = %s;",(ID))
        d = cur.fetchall()
        data = [dict(zip(("RoomID","NoOfBeds","Description","WingName","WingID","HostelName","HostelID"),vv)) for vv in d]
        cur.execute("SELECT ra.RA_ID , ra.Room_ID , ra.Student_ID , sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Email , sd.Mobile_Number FROM `room_allocate` as ra , student_details as sd WHERE ra.Room_ID = %s AND ra.Student_ID = sd.Student_ID;",(ID))
        d1 = cur.fetchall()
        data1 = [dict(zip(("ID","RoomID","StudentID","StudentFN","StudentMN","StudentLN","StudentEmail","StudentMobileNumber"),vv)) for vv in d1]
        return jsonify({"RoomDetails":data , "RoomAllotmentDetails":data1})

#Extra Functions
def getUniqueID(string) -> str:
    str1 = uuid.uuid4()
    str2 = str(str1)[:12]
    return (string + str2)

def getTodayformattedDate() -> str:
    currentDate = date.today()
    formatted = currentDate.strftime('%d/%m/%Y')
    return formatted

