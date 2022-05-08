import random
from pickletools import read_uint1
from flask import Blueprint , request , jsonify
import json
import uuid
from . import mysql
from datetime import datetime , date , timedelta
import time
import numpy as np

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
        cur.execute("SELECT count(me.QrScanID) , me.type , mf.Amount , count(me.QrScanID)*Amount as totalAmount FROM `mess_entry` as me , mess_fees as mf WHERE me.student_id = %s and me.Type = mf.Food_Type group by me.type;",[ID])
        d = cur.fetchall()
        messFees = [dict(zip(("Count" , "Type" , "Amount" , "TotalAmount"),vv)) for vv in d]
        cur.execute("SELECT * FROM hostel_fees WHERE student_id = %s",[ID])
        d1 = cur.fetchall()
        hostelFees = [dict(zip(("ID" , "StudentID" , "Amount" , "Year" , "JoiningDate"),vv)) for vv in d1]
        cur.execute("SELECT p.Payment_ID , p.Student_ID , p.Date , p.Time , p.Amount , p.Payment_Method , s.First_Name , s.Middle_Name , s.Last_Name FROM payment as p , secretory as s WHERE student_id = %s AND s.Secretory_ID = p.DoneBySecretoryID;",[ID])
        d2 = cur.fetchall()
        paidFees = [dict(zip(("PaymentID" , "StudentID" , "Date" , "Time" , "Amount" , "PaymentMethod" , "SecretoryFN", "SecretoryMN", "SecretoryLN"),vv)) for vv in d2]
        cur.execute("SELECT ra.Room_ID , wd.Wing_Name , hd.Hostel_Name , sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Email , sd.Mobile_Number FROM `room_allocate` as ra , room_details as rd , wing_details as wd , hostel_details as hd , student_details as sd WHERE ra.Student_ID = %s AND ra.Room_ID = rd.Room_ID AND rd.Wing_ID = wd.Wing_ID AND wd.Hostel_ID = hd.Hostel_ID AND ra.Student_ID = sd.Student_ID;",[ID])
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
        for i in range (0 , len(data)):
            roomID = data[i].get("RoomID")
            noofbeds = data[i].get("NoOfBeds")
            cur.execute("SELECT count(*) FROM `room_allocate` WHERE Room_ID = %s",[roomID])
            fillbeds = cur.fetchone()
            data[i].update({"FillBeds" : fillbeds[0]})
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
        cur.execute("INSERT INTO `room_details`( `Room_ID` , `Wing_ID`, `No_of_Beds`, `Description`) VALUES (%s,%s,%s,%s)",(data.get('RoomID') , data.get('WingID') , data.get('NoOfBeds') , data.get('Description')))
        mysql.connection.commit()
        return jsonify("Room Added Successfully")

@secretory.route('roomDetailsForAlt/<ID>',methods=['GET'])
def roomDetailsForALt(ID):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT rd.Room_ID , rd.No_of_Beds , rd.Description , wd.Wing_Name , wd.Wing_ID , hd.Hostel_Name , hd.Hostel_ID FROM `room_details` as rd , wing_details as wd , hostel_details as hd WHERE rd.Wing_ID = wd.Wing_ID AND wd.Hostel_ID = hd.Hostel_ID AND rd.Room_ID = %s;",[ID])
        d = cur.fetchall()
        data = [dict(zip(("RoomID","NoOfBeds","Description","WingName","WingID","HostelName","HostelID"),vv)) for vv in d]
        cur.execute("SELECT ra.RA_ID , ra.Room_ID , ra.Student_ID , sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Email , sd.Mobile_Number FROM `room_allocate` as ra , student_details as sd WHERE ra.Room_ID = %s AND ra.Student_ID = sd.Student_ID;",[ID])
        d1 = cur.fetchall()
        data1 = [dict(zip(("ID","RoomID","StudentID","StudentFN","StudentMN","StudentLN","StudentEmail","StudentMobileNumber"),vv)) for vv in d1]
        return jsonify({"RoomDetails":data , "RoomAllotmentDetails":data1})

@secretory.route('getNotAltStd',methods=['GET'])
def getNotAltStd():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT Student_ID , First_Name , Middle_Name , Last_Name , Email , Mobile_Number FROM `student_details` WHERE Student_ID  NOT IN (SELECT Student_ID FROM room_allocate)")
        d = cur.fetchall()
        data = [dict(zip(("StudentID","FN","MN","LN","Email","MobileNumber"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('deleteRA/<ID>',methods=['DELETE'])
def deleteRA(ID):
    if request.method == 'DELETE':
        cur = mysql.connection.cursor();
        cur.execute("DELETE FROM `room_allocate` WHERE RA_ID = %s",[ID])
        mysql.connection.commit()
        return jsonify("Data Updated Successfully") , 200

@secretory.route('updateRA',methods=['PUT'])
def updateRA():
    if request.method == 'PUT':
        data = request.data
        data = json.loads(data)
        print(data)
        ra = data.get('ID')
        stdID = data.get('StudentID')
        cur = mysql.connection.cursor();
        cur.execute("UPDATE `room_allocate` SET `Student_ID`=%s WHERE RA_ID = %s",(stdID,ra))
        mysql.connection.commit()
        return jsonify("Data Updated Successfully") , 200

@secretory.route('getRoomID',methods=['GET'])
def getRoomID():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("Select room_ID from room_details")
        d = cur.fetchall()
        data = [dict(zip(("RoomID"),vv)) for vv in d]
        return jsonify(data)

@secretory.route('addRA',methods=['POST'])
def addRA():
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        roomID = data.get('RoomID')
        stdID = data.get('StudentID')
        cur = mysql.connection.cursor();
        cur.execute("INSERT INTO `room_allocate`(`Room_ID`, `Student_ID`) VALUES (%s,%s)",(roomID,stdID))
        mysql.connection.commit()
        return jsonify("Data Updated Successfully") , 200

@secretory.route('allocateAll',methods=['GET'])
def allocateAll():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        altData = []
        class Data:
            cur.execute("Select wing_ID , gender from wing_details")
            d = cur.fetchall()
            Hostels = [list(x) for x in d]
            cur.execute("SELECT Room_ID , Wing_ID FROM `room_details`")
            d1 = cur.fetchall()
            rooms = [list(x) for x in d1]
            array = ['FE' , 'SE' , 'TE' , 'BE' , 'HI' , 'F']
            Rooms = []
            for i in range(0 , len(rooms)):
                data = []
                roomID = rooms[i][0]
                data.append(roomID)
                data.append(rooms[i][1])
                secure_random = random.SystemRandom()   
                item = secure_random.choice(array)
                data.append(item)
                cur.execute("SELECT `No_of_Beds` FROM `room_details` WHERE Room_ID = %s",[roomID])
                nob = cur.fetchone()
                cur.execute("SELECT count(*) FROM `room_allocate` WHERE Room_ID = %s",[roomID])
                alreadyalt = cur.fetchone()
                remain = nob[0] - alreadyalt[0]
                data.append(remain)
                data.append(0)
                Rooms.append(data)
            cur.execute("SELECT Student_ID , Gender , Category , '0' FROM `student_details` WHERE Student_ID  NOT IN (SELECT Student_ID FROM room_allocate)")
            d3 = cur.fetchall()
            Students = [list(x) for x in d3]
            
            def __init__(self):
                self._hostels = []; self._rooms = []; self._students = []
                for i in range(0 , len(self.Hostels)):
                    self._hostels.append(Hostel(self.Hostels[i][0], self.Hostels[i][1]))
                    
                for i in range(0 , len(self.Rooms)):
                    self._rooms.append(Room(self.Rooms[i][0], self.Rooms[i][1], self.Rooms[i][2], self.Rooms[i][3], self.Rooms[i][4]))
                    
                for i in range(0, len(self.Students)):
                    self._students.append(Student(self.Students[i][0], self.Students[i][1], self.Students[i][2], self.Students[i][3]))

                self._A_Rom = 0
                for i in range(0, len(self._students)):
                    self._A_Rom = i + 1

            def get_hostels(self): return self._hostels
            def get_rooms(self): return self._rooms
            def get_students(self): return self._students
            def get_A_Rom(self): return self._A_Rom

        class Allocate():
            def __init__(self):
                self._data = data
                self._allocate = []
                self._ARom = 0        
                
                rooms = self._data.get_rooms()
                for i in range(0, len(rooms)):
                    students = self._data.get_students()
                    for j in range(0, len(students)):
                        allot = Allocation(self._ARom, rooms[i], students[j])
                        
                        while(rooms[i].get_Rset() < rooms[i].get_Capacity()):
                            # rand = rnd.randrange(0, len(students))
                            if (students[j].get_S_avail() == 0):
                                if ((rooms[i].get_Hid() == '1' or rooms[i].get_Hid() == '2' or rooms[i].get_Hid() == '3') and students[j].get_Gen() == 'MALE'):
                                    if (rooms[i].get_Cat() == students[j].get_Cat()):
                                        self._ARom += 1
                                        allot.set_room(rooms[i].get_Rid())
                                        allot.set_Acap(rooms[i].get_Rset())
                                        rooms[i].set_Rset(rooms[i].get_Rset() + 1)
                                        allot.set_student(students[j].get_Sid())
                                        students[j].set_S_avail(1)
                                        self._allocate.append(allot)
                                    else:
                                        break
                                elif ((rooms[i].get_Hid() == '4' or rooms[i].get_Hid() == '5' or rooms[i].get_Hid() == '6') and students[j].get_Gen() == 'FEMALE'):
                                    if (rooms[i].get_Cat() == students[j].get_Cat()):
                                        self._ARom += 1
                                        allot.set_room(rooms[i].get_Rid())
                                        allot.set_Acap(rooms[i].get_Rset())
                                        rooms[i].set_Rset(rooms[i].get_Rset() + 1)
                                        allot.set_student(students[j].get_Sid())
                                        students[j].set_S_avail(1)
                                        self._allocate.append(allot)
                                    else:
                                        break
                                else:
                                    break
                            else:
                                break
                for i in range(0, len(self._allocate)):
                    # print(str(i+1)+")",self._allocate[i].get_room(), self._allocate[i].get_student(), self._allocate[i].get_R().get_Cat(), self._allocate[i].get_S().get_Cat())
                    roomID = self._allocate[i].get_room()
                    stdID = self._allocate[i].get_student()
                    cur.execute("INSERT INTO `room_allocate`(`Room_ID`, `Student_ID`) VALUES (%s,%s)",(roomID , stdID))
                    mysql.connection.commit()
                    cur.execute("SELECT sd.First_Name , sd.Middle_Name , sd.Last_Name , sd.Category , sd.Gender , sd.Email , sd.Mobile_Number , rd.Room_ID , wd.Wing_Name , hd.Hostel_Name FROM `room_details` as rd , student_details as sd , wing_details as wd , hostel_details as hd WHERE sd.Student_ID = %s AND rd.Room_ID = %s AND rd.Wing_ID = wd.Wing_ID AND wd.Hostel_ID = hd.Hostel_ID;",(stdID , roomID))
                    d = cur.fetchall()
                    data1 = [dict(zip(("FN" , "MN" , "LN" , "Category" , "Gender" , "Email" , "MobileNumber" , "RoomID" , "WingName" , "HostelName"),vv)) for vv in d]
                    altData.append(data1[0])

        class Allocation:
            def __init__(self, Aid, R, S):
                self._Aid = Aid
                self._R = R
                self._S = S
                self._room = None
                self._student = None
                self._Acap = None
            def get_Aid(self): return self._Aid
            def get_R(self): return self._R
            def get_S(self): return self._S
            def get_room(self): return self._room
            def get_student(self): return self._student
            def get_Acap(self): return self._Acap
            def set_room(self, room): self._room = room
            def set_student(self, student): self._student = student
            def set_Acap(self, Acap):
                Acap += 1
                self._Acap = Acap



        class Hostel:
            def __init__(self, Hid, Dorm):
                self._Hid = Hid
                self._Dorm = Dorm
            def get_Hid(self): return self._Hid
            def get_Dorm(self): return self._Dorm


        class Room:
            def __init__(self, Rid, Hid, Cat, Capacity, Std_Allocated):
                self._Rid = Rid
                self._Hid = Hid
                self._Cat = Cat
                self._Capacity = Capacity
                self._Std_Allocated = Std_Allocated
                self._allot = 0

            def get_Rid(self): return self._Rid
            def get_Hid(self): return self._Hid
            def get_Cat(self): return self._Cat
            def get_Capacity(self): return self._Capacity
            def get_Std_Allocated(self): return self._Std_Allocated
            def get_Rset(self): return self._allot
            def set_Rset(self, Rset): self._allot = Rset
            def set_Rsetend(self) : self._allot = 0
            

        class Student:
            def __init__(self, Sid, Gen, Cat, std_allocated):
                self._Sid = Sid
                self._Gen = Gen
                self._Cat = Cat
                self._std_allocated = std_allocated
                self.S_avail = 0
                
            def get_Sid(self): return self._Sid
            def get_Gen(self): return self._Gen
            def get_Cat(self): return self._Cat
            def get_std_allocated(self): return self._std_allocated
            def get_S_avail(self): return self.S_avail
            def set_S_avail(self, avail): self.S_avail = avail
        
        data = Data()
        allocate = Allocate()
        return jsonify(altData)

#Extra Functions
def getUniqueID(string) -> str:
    str1 = uuid.uuid4()
    str2 = str(str1)[:12]
    return (string + str2)

def getTodayformattedDate() -> str:
    currentDate = date.today()
    formatted = currentDate.strftime('%d/%m/%Y')
    return formatted

