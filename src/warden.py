from flask import Blueprint , request , jsonify
from . import mysql
import json

warden = Blueprint('warden',__name__)

@warden.route('/<ID>',methods=['GET'])
def get_Warden(ID):
    if request.method == 'GET':
        curr = mysql.connection.cursor()
        curr.execute("SELECT * FROM warden_details WHERE Warden_ID = %s",[ID])
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
                mysql.connection.commit()
                cur.close()
                return jsonify("Password Update Successfully!")
            else:
                cur.close()
                return jsonify("Incorrect Current Password!") , 404

@warden.route('/getHostelDetails/<Warden_ID>',methods=['GET'])
def getHostelDetails(Warden_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hostel_details WHERE warden_id = %s",[Warden_ID])
        data = cur.fetchone()
        HostelID = data[0]
        HostelName = data[1]
        HostelDescription = data[2]
        cur.execute("SELECT wing_id , wing_name FROM wing_details WHERE Hostel_ID = %s",(HostelID))
        data = cur.fetchall()
        Wing = [dict(zip(("Wing_ID","Wing_Name"),vv)) for vv in data]
        return jsonify({"HostelID" : HostelID , "HostelName" : HostelName , "HostelDescription" : HostelDescription , "WingDetails" : Wing})
    
@warden.route('/getWingDetails/<Wing_ID>',methods=['GET'])
def getWingDetails(Wing_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT wing_name , hostel_id FROM wing_details WHERE wing_id = %s",(Wing_ID))
        data = cur.fetchone()
        HostelID = data[1]
        WingName = data[0]
        cur.execute("SELECT hostel_name FROM hostel_details WHERE hostel_id = %s",(HostelID))
        data = cur.fetchone()
        HostelName = data[0]
        cur.execute("SELECT * FROM room_details WHERE wing_id = %s",(Wing_ID))
        data = cur.fetchall()
        RoomDetails = [dict(zip(("Room_ID" , "Wing_ID" , "No_of_Beds" , "Description"),vv)) for vv in data]    
        return jsonify({"RoomDetails":RoomDetails , "WingName" : WingName , "HostelName" : HostelName })

@warden.route('/getRoomDetails/<Room_ID>',methods=['GET'])
def getRoomDetails(Room_ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Wing_Name , hostel_id FROM wing_details WHERE (Wing_ID = (SELECT Wing_ID FROM room_details WHERE Room_ID = %s))",(Room_ID))
        data = cur.fetchone()
        HostelID = data[1]
        WingName = data[0]
        cur.execute("SELECT hostel_name FROM hostel_details WHERE hostel_id = %s",(HostelID))
        data = cur.fetchone()
        HostelName = data[0]
        cur.execute("SELECT sd.Student_ID , sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Email , sd.Mobile_Number FROM student_details AS sd , room_allocate AS ra WHERE ra.Room_ID = %s  AND sd.Student_ID = ra.Student_ID",(Room_ID))
        data = cur.fetchall()
        Room_Mate_Details = [dict(zip(("Student_ID","First_Name","Middle_Name","Last_Name","Email","Mobile_Number"),vv)) for vv in data]
        return jsonify({"RoomID" : Room_ID[0] , "WingName" : WingName , "HostelName" : HostelName , "RoomMembers" : Room_Mate_Details}) , 200

@warden.route('/leaves/<ID>',methods=['POST','GET'])
def leaves(ID):
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        fromDate = data.get('from')
        toDate = data.get('to')
        days = data.get('days')
        reason = data.get('reason')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `leaves`(`Staff_Type`, `From_Date`, `To_Date`, `Day`, `Reason`, `Status`,`Staff_ID`) VALUES ('Warden',%s,%s,%s,%s,'Pending',%s)",(fromDate,toDate,days,reason,ID))
        mysql.connection.commit()
        return jsonify("Leaves Apply SuccessFully...!")
    elif request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `leaves` WHERE Staff_ID = %s AND Staff_Type = 'Warden'",(ID))
        d = cur.fetchall()
        data = [dict(zip(("ID","StaffType","FromDate","ToDate","Day","Reason","Status","DescisionTakenByType","StaffID","DecisionTakenByID","DescisionTakenByName"),vv)) for vv in d]
        return jsonify(data)

@warden.route('/LeaveDecision/<ID>',methods=['GET','POST'])
def LeaveDecision(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("Select * from (SELECT securityguard_id , First_Name , Middle_Name , Last_name FROM security_guard WHERE gate_id = (SELECT gate_id FROM `gate_info` WHERE hostel_id = (SELECT hostel_ID FROM `hostel_details` WHERE warden_id = %s))) as security_table , leaves as le WHERE le.Staff_Type = 'Security' AND le.Staff_ID = security_table.securityguard_id",[ID])
        d1 = cur.fetchall()
        data1 = [dict(zip(("SecurityGuard_ID","First_Name","Middle_Name","Last_Name","ID","StaffType","FromDate","ToDate","Day","Reason","Status","DecisionTakenByType","StaffID","DecisionTakenByID","DecisionTakenByName"),vv)) for vv in d1]
        cur.execute("SELECT * FROM (SELECT mess_staff.messStaff_ID , mess_staff.First_name , mess_staff.Middle_name ,mess_staff.Last_name FROM mess_staff WHERE messStaff_ID = (SELECT MessStaff_ID FROM mess_info WHERE Hostel_ID = (SELECT hostel_id FROM hostel_details WHERE warden_id = %s))) as msi , leaves as le WHERE le.Staff_Type = 'Mess' AND le.Staff_ID = msi.messStaff_ID",[ID])
        d2 = cur.fetchall()
        data2 = [dict(zip(("MessStaff_ID","First_Name","Middle_Name","Last_Name","ID","StaffType","FromDate","ToDate","Day","Reason","Status","DecisionTakenByType","StaffID","DecisionTakenByID","DecisionTakenByName"),vv)) for vv in d2]
        data = data1 + data2
        return jsonify(data)
    elif request.method == 'POST':
        data = request.data
        data = json.loads(data)
        l_ID = data.get('ID')
        Status = data.get('Status')
        DecisionTakenByType = data.get('DecisionTakenByType')
        cur = mysql.connection.cursor()
        cur.execute("SELECT CONCAT(First_Name ,' ' , Middle_Name ,' ' , Last_Name) as Full_Name FROM warden_details WHERE Warden_ID = %s",(ID))
        name = cur.fetchone()
        cur.execute("UPDATE leaves SET Status = %s , Decision_takenby_type = %s , Decison_takenby_ID = %s , Decision_takenby_Name = %s WHERE ID = %s",(Status , DecisionTakenByType , ID , name , l_ID))
        mysql.connection.commit()
        return jsonify("Status Updated Successfully....!")
