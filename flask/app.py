#! /usr/bin/python3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import config
import re
import os
#for the pymysql look at the faculty url, on that the two ways to access the CS database will be shown


#Configuration for pymysql
db = config.dblocal

app = Flask(__name__)
app.secret_key = os.urandom(24)    # SESSION FIX
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')
       
@app.route('/student', methods = ['GET','POST'])
def displayStudents():
        if session["permissions"] != "ADMIN":
             return
        
        if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from student;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            print(data)
            #return f"Done!! Query Result is {data}"
            return render_template('student/student.html', data=data)
        if request.method == 'POST':
            data = request.form["ID"]
            action = request.form["action"]

            if action == "delete":
                print(data)
                cursor = db.cursor()
                sql = "delete from student where stu_id = %s"
                cursor.execute(sql, [data])
                sql = "select * from student"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('student/student.html',data= data)
            elif action == "view":
                cursor = db.cursor()
                sql = "select s.ID, s.name, t.course_id, t.sec_id, t.semester, t.year, t.grade FROM student s join takes t on s.ID = t.ID WHERE s.ID = %s"
                cursor.execute(sql, [data])
                data = cursor.fetchall()
                cursor.close()    
                #return render_template('studentschedule.html',data=data)
                student_id = request.form["ID"]
                return redirect(url_for("studentSchedule", id=student_id))

# Displays the student's schedule
@app.route('/studentschedule/<id>', methods=['GET', 'POST'])
def studentSchedule(id):

    cursor = db.cursor()
    sql_years = """
        SELECT DISTINCT t.year
        FROM takes t
        WHERE t.ID = %s
        ORDER BY t.year DESC
    """
    cursor.execute(sql_years, [id])
    years = [row[0] for row in cursor.fetchall()]
    cursor.close()

    selected_year = None
    if request.method == "POST":
        selected_year = request.form.get("year")

        cursor = db.cursor()
        sql = """
            SELECT s.ID, s.name, t.course_id, t.sec_id, t.semester, t.year, t.grade
            FROM student s
            JOIN takes t ON s.ID = t.ID
            WHERE s.ID = %s AND t.year = %s
        """
        cursor.execute(sql, [id, selected_year])
        schedule = cursor.fetchall()
        cursor.close()
    else:
        cursor = db.cursor()
        sql = """
            SELECT s.ID, s.name, t.course_id, t.sec_id, t.semester, t.year, t.grade
            FROM student s
            JOIN takes t ON s.ID = t.ID
            WHERE s.ID = %s
        """
        cursor.execute(sql, [id])
        schedule = cursor.fetchall()
        cursor.close()

    return render_template(
        "student/studentschedule.html",
        schedule=schedule,
        years=years,
        selected_year=selected_year,
        student_id=id
    )

@app.route('/studentsearch', methods = ['GET','POST'])
def studentSearch():        
        if request.method == 'GET':
            return render_template('studentsearch.html')
        if request.method == 'POST':
            myName = request.form['name']
            myId = request.form['id']
            print(myName, myId)    
            if myId != "":
                print("Goin for ID")
                cursor = db.cursor()
                sql = "SELECT * from student where id LIKE %s"
                cursor.execute(sql,[f"{myId}%"])
                data = cursor.fetchall()
                cursor.close()
                return redirect(url_for("displayResult", id = myId))    
            elif myName != "":
                print("Goin for Name")
                cursor = db.cursor()
                sql = "SELECT * from student where name LIKE %s"
                cursor.execute(sql, [f"{myName}%"])
                data = cursor.fetchall()
                cursor.close()     
                return redirect(url_for("displayResult", id = myName))       
            else:
                 return render_template('studentsearch.html')
            
        
@app.route('/searchresult/<id>', methods = ['GET','POST'])
def displayResult(id):
        if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from student WHERE name like %s OR ID LIKE %s;"
            cursor.execute(sql,[f"{id}%", f"{id}%"])         
            data = cursor.fetchall()
            cursor.close()
            print(data)
            #return f"Done!! Query Result is {data}"
            return render_template('searchresult.html', data=data)
        if request.method == 'POST':
            data = request.form["ID"]
            action = request.form["action"]

            if action == "delete":
                print(data)
                cursor = db.cursor()
                sql = "delete from student where id = %s"
                cursor.execute(sql, [data])
                sql = "select * from student"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('student.html',data= data)
            elif action == "view":
                cursor = db.cursor()
                sql = "select s.ID, s.name, t.course_id, t.sec_id, t.semester, t.year, t.grade FROM student s join takes t on s.ID = t.ID WHERE s.ID = %s"
                cursor.execute(sql, [data])
                data = cursor.fetchall()
                cursor.close()    
                #return render_template('studentschedule.html',data=data)
                student_id = request.form["ID"]
                return redirect(url_for("studentSchedule", id=student_id))

@app.route('/newstudent',  methods = ['GET','POST'])
def newStudent():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
        cursor = db.cursor()
        sql = "SELECT dept_name as dept_name from department;"
        cursor.execute(sql)
        data = cursor.fetchall()        
        cursor.close()
        edited = []
        print(data)
        for i in data:
            edited.append(i[0])
        return render_template('student/newstudent.html', data = edited)
    if request.method == 'POST':
        myName = request.form['name']
        myId = request.form['id']
        myDept = request.form['dept']
        isTransfer = bool(request.form.get("is_active"))
        myCredits = request.form['credits']
        if not isTransfer:
            myCredits = 0
        cursor = db.cursor()
        sql = "Insert into student values(%s, %s, %s, %s)"
        cursor.execute(sql,[myId, myName, myDept, myCredits])
        data = cursor.fetchall()
        #cursor.execute("CALL pp(%s, %s, %s, %s);",[myId, myName, myDept, mySalary])
        #reload page with all favulty members        
        cursor = db.cursor()
        sql = "SELECT dept_name as dept_name from department;"
        cursor.execute(sql)
        data = cursor.fetchall()        
        cursor.close()
        edited = []
        print(data)
        for i in data:
            edited.append(i[0])
        return redirect(url_for("displayStudents"))
    
@app.route("/studentedit/<stu_id>", methods = ["GET", "POST"])
def editStudent(stu_id):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = "SELECT dept_name as dept_name from department;"
        cursor.execute(sql)
        data = cursor.fetchall()        
        edited = []
        for i in data:
            edited.append(i[0])

        sql = "SELECT * FROM student WHERE stu_ID = %s"
        cursor.execute(sql, [stu_id])
        data = cursor.fetchone()
        if data:
            return render_template('student/studentedit.html', student_id=stu_id, depts=edited, name=data[1], dept_name=data[2], credits=data[3])
    if request.method == "POST":
        student_name = request.form["name"]
        department = request.form["dept"]
        tot_creds = request.form["credits"]
        print(stu_id)
        cursor = db.cursor()
        sql = """
                update student
                set
                    name = %s,
                    dept_name = %s,
                    tot_cred = %s
                WHERE stu_ID = %s
                """
        cursor.execute(sql, [student_name, department, tot_creds, stu_id])

        print("Rows affected:", cursor.rowcount)

        db.commit()
        cursor.close()
        return redirect(url_for("displayStudents"))

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ SECTION /////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\//////////////////////////////////////////////////////////////////////////////

@app.route("/section", methods = ["GET", "POST"])
def displaySection():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from section;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            print(data)
            #return f"Done!! Query Result is {data}"
            return render_template('section/section.html', data=data)
    if request.method == 'POST':
            
            action = request.form["action"]

            if action == "delete":
                data = json.loads(request.form["row"])
                print(data)
                cursor = db.cursor()
                sql = """
                    delete from section
                    where course_id = %s AND sec_id = %s AND semester = %s AND year = %s
                    """
                cursor.execute(sql, [data[0], data[1], data[2], data[3]])
                sql = "select * from section"
                cursor.execute(sql)
                db.commit()
                data = cursor.fetchall()
                cursor.close()    
                return render_template('section/section.html',data= data)

@app.route('/newsection',  methods = ['GET','POST'])
def newSection():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
        cursor = db.cursor()
        sql = "SELECT course_id from course;"
        cursor.execute(sql)
        data = cursor.fetchall()

        sql = """SELECT * FROM classroom"""   
        cursor.execute(sql)
        rooms = cursor.fetchall()
        
        sql = """SELECT * FROM time_slot"""
        cursor.execute(sql)
        timeSlots = cursor.fetchall()

        cursor.close()
        edited = []
        print(data)
        for i in data:
            edited.append(i[0])
        classrooms = []
        for i in rooms:
            classrooms.append(i)
        semester = ["Summer", "Fall", "Spring"]
        return render_template('section/newsection.html', course = edited, classrooms=classrooms, semester=semester, timeslots=timeSlots)
    if request.method == 'POST':
        myCourse = request.form['course']
        myId = request.form['sec_id']
        mySem = request.form['sem']
        myYear = request.form['year']
        myRoom = request.form["room"]
        mySlot = request.form["slot"]
        cursor = db.cursor()
        sql = "Insert into section values(%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql,[myCourse, myId, mySem, myYear, myRoom, mySlot])
        data = cursor.fetchall()  
        db.commit() 
        cursor.close()
        return redirect(url_for("displaySection"))

@app.route("/editsection/<course_id>/<sec_id>/<sem>/<int:year>", methods=['GET','POST'])
def editSection(course_id, sec_id, sem, year):
    cursor = db.cursor()

    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
        cursor = db.cursor()
        sql = "SELECT course_id from course;"
        cursor.execute(sql)
        data = cursor.fetchall()

        sql = """SELECT * FROM classroom"""   
        cursor.execute(sql)
        rooms = cursor.fetchall()
        
        sql = """SELECT * FROM time_slot"""
        cursor.execute(sql)
        timeSlots = cursor.fetchall()

        edited = []
        print(data)
        for i in data:
            edited.append(i[0])
        classrooms = []
        for i in rooms:
            classrooms.append(i)
        semester = ["Summer", "Fall", "Spring"]

        # Fetch the current section row to pre-fill the form
        cursor.execute("""
            SELECT * FROM section
            WHERE course_id=%s AND sec_id=%s AND semester=%s AND year=%s
        """, [course_id, sec_id, sem, year])
        section = cursor.fetchone()  # section = (course_id, sec_id, semester, year, roomID, time_slot_id)

        cursor.close()

        semesters = ["Summer", "Fall", "Spring"]
        return render_template(
            'section/editsection.html',
            classrooms=classrooms,
            timeslots=timeSlots,
            section=section
        )

    if request.method == 'POST':
        myRoom = request.form['room']
        mySlot = request.form['slot']

        cursor.execute("""
            SELECT * FROM section
            WHERE course_id=%s AND sec_id=%s AND semester=%s AND year=%s
        """, [course_id, sec_id, sem, year])
        section = cursor.fetchone()  # section = (course_id, sec_id, semester, year, roomID, time_slot_id)
        
        # Update the section instead of insert
        cursor.execute("""
            UPDATE section
            SET roomID=%s, time_slot_id=%s
            WHERE course_id=%s AND sec_id=%s AND semester=%s AND year=%s
        """, [myRoom, mySlot, section[0], section[1], section[2], section[3]])

        db.commit()
        cursor.close()
        return redirect(url_for("displaySection"))

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ CLASSROOM \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@app.route("/classroom", methods = ["GET", "POST"])
def displayClassrooms():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from classroom;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            
            #return f"Done!! Query Result is {data}"
            return render_template('classroom/classroom.html', data=data)
    if request.method == 'POST':
            
            action = request.form["action"]

            if action == "delete":
                data = request.form["ID"]
                print(data)
                cursor = db.cursor()
                sql = """
                    delete from classroom
                    where roomID = %s
                    """
                cursor.execute(sql, [data[0]])
                sql = "select * from classroom"
                cursor.execute(sql)
                db.commit()
                data = cursor.fetchall()
                cursor.close()    
                return render_template('classroom/classroom.html',data=data)

@app.route('/newclassroom', methods = ["GET", "POST"])
def newClassroom():
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from buildings"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('classroom/newclassroom.html', buildings=edited)
    
    if request.method == "POST":
        myBuilding = request.form["building"]
        myRoomNo = request.form["roomNo"]
        myCap = request.form["capacity"]
        cursor = db.cursor()
        sql = """ 
                SELECT roomID
                FROM classroom
                ORDER BY roomID DESC
                LIMIT 1;
            """
        cursor.execute(sql)
        roomID = cursor.fetchone()[0]
        roomID += 1
        sql = """
                insert into classroom(roomID, building, room_number, capacity)
                values (%s, %s, %s, %s)
              """
        cursor.execute(sql, [roomID, myBuilding, myRoomNo, myCap])
        db.commit()
        cursor.close()
        return redirect(url_for("displayClassrooms"))

@app.route('/editclassroom/<room_id>', methods = ["GET", "POST"])
def editClassroom(room_id):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from classroom where roomID = %s"""
        cursor.execute(sql, [room_id])
        data = cursor.fetchone()
        
        sql = """select * from buildings"""
        cursor.execute(sql)
        rooms = cursor.fetchall()
        cursor.close()
        edited = []
        for i in rooms:
            edited.append(i[0])

        cursor.close()
        return render_template("/classroom/editclassroom.html", buildings=edited, roomID=room_id, building=data[1], roomNo=data[2], capacity=data[3])
    if request.method == "POST":
        myBuilding = request.form["building"]
        myRoomNo = request.form["roomNo"]
        myCap = request.form["capacity"]
        cursor = db.cursor()
        sql = """
                update classroom
                SET building = %s, room_number = %s, capacity = %s
                WHERE roomID = %s
              """
        cursor.execute(sql, [myBuilding, myRoomNo, myCap, room_id])
        db.commit()
        cursor.close()
        return redirect(url_for("displayClassrooms"))
    
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ COURSES ////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////////////

@app.route("/course", methods = ["GET", "POST"])
def displayCourses():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from course;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            
            #return f"Done!! Query Result is {data}"
            return render_template('course/course.html', data=data)
    if request.method == 'POST':  
            action = request.form["action"]
            if action == "delete":
                data = request.form["ID"]
                print(data)
                cursor = db.cursor()
                sql = """
                    delete from course
                    where course_id = %s
                    """
                cursor.execute(sql, [data])
                db.commit()
                sql = "select * from course"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('course/course.html',data=data)

@app.route('/newcourse', methods = ["GET", "POST"])
def newCourse():
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from department"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('course/newcourse.html', data=edited)
    
    if request.method == "POST":
        myCourse = request.form["courseID"]
        myTitle = request.form["title"]
        myDept = request.form["dept"]
        myCreds = request.form["credits"]
        cursor = db.cursor()
        sql = """
                insert into course(course_id, title, dept_name, credits)
                values (%s, %s, %s, %s)
              """
        cursor.execute(sql, [myCourse, myTitle, myDept, myCreds])
        db.commit()
        cursor.close()
        return redirect(url_for("displayCourses"))

@app.route('/editcourse/<course_id>', methods = ["GET", "POST"])
def editCourse(course_id):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from course WHERE course_id = %s"""
        cursor.execute(sql, [course_id])
        course = cursor.fetchone()
        sql = """select * from department"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('course/editcourse.html', courseID=course_id, data=edited, title=course[1], dept_name=course[2], credits=course[3])
    if request.method == "POST":
        myTitle = request.form["title"]
        myDept = request.form["dept"]
        myCreds = request.form["credits"]
        cursor = db.cursor()
        sql = """
                update course
                SET title = %s, dept_name = %s, credits = %s
                WHERE course_id = %s
              """
        cursor.execute(sql, [myTitle, myDept, myCreds, course_id])
        db.commit()
        cursor.close()
        return redirect(url_for("displayCourses"))
    
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ Department ////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////////////

@app.route("/department", methods = ["GET", "POST"])
def displayDepartments():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from department;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            
            #return f"Done!! Query Result is {data}"
            return render_template('department/department.html', data=data)
    if request.method == 'POST':  
            action = request.form["action"]
            if action == "delete":
                data = request.form["ID"]
                print(data)
                cursor = db.cursor()
                sql = """
                    delete from department
                    where dept_name = %s
                    """
                cursor.execute(sql, [data])
                db.commit()
                sql = "select * from department"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('department/department.html',data=data)

@app.route('/newdepartment', methods = ["GET", "POST"])
def newDepartment():
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from buildings"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('department/newdepartment.html', data=edited)
    
    if request.method == "POST":
        myDept = request.form["deptName"]
        myBuilding = request.form["building"]
        myBudget = request.form["budget"]
        cursor = db.cursor()
        sql = """
                insert into department(dept_name, building, budget)
                values (%s, %s, %s)
              """
        cursor.execute(sql, [myDept, myBuilding, myBudget])
        db.commit()
        cursor.close()
        return redirect(url_for("displayDepartments"))

@app.route('/editdepartment/<dept_name>', methods = ["GET", "POST"])
def editDepartment(dept_name):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from department WHERE dept_name = %s"""
        cursor.execute(sql, [dept_name])
        dept = cursor.fetchone()
        sql = """select * from buildings"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        print(edited)
        print(dept)
        return render_template('department/editdepartment.html', deptName=dept[0], building=dept[1], budget=dept[2], data=edited)
    if request.method == "POST":
        myDept = request.form["deptName"]
        myBuilding = request.form["building"]
        myBudget = request.form["budget"]
        cursor = db.cursor()
        sql = """
                update department
                SET building = %s, budget = %s
                WHERE dept_name = %s
              """
        cursor.execute(sql, [myBuilding, myBudget, myDept])
        db.commit()
        cursor.close()
        return redirect(url_for("displayDepartments"))


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ Instructor ////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////////////

@app.route("/instructor", methods = ["GET", "POST"])
def displayInstructors():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from instructor;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            
            #return f"Done!! Query Result is {data}"
            return render_template('instructor/instructor.html', data=data)
    if request.method == 'POST':  
            action = request.form["action"]
            if action == "delete":
                data = request.form["ID"]
                print(data)
                cursor = db.cursor()
                sql = """
                    delete from instructor
                    where ID = %s
                    """
                cursor.execute(sql, [data])
                db.commit()
                sql = "select * from instructor"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('instructor/instructor.html',data=data)

@app.route('/newinstructor', methods = ["GET", "POST"])
def newInstructor():
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from department"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('instructor/newinstructor.html', data=edited)
    
    if request.method == "POST":
        myID = request.form["ID"]
        myName = request.form["name"]
        myDept = request.form["dept"]
        mySalary = request.form["salary"]
        cursor = db.cursor()
        sql = """
                insert into instructor(ID, name, dept_name, salary)
                values (%s, %s, %s, %s)
              """
        cursor.execute(sql, [myID, myName, myDept, mySalary])
        db.commit()
        cursor.close()
        return redirect(url_for("displayInstructors"))

@app.route('/editinstructor/<i_ID>', methods = ["GET", "POST"])
def editInstructor(i_ID):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from instructor WHERE ID = %s"""
        cursor.execute(sql, [i_ID])
        instru = cursor.fetchone()
        sql = """select * from department"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('instructor/editinstructor.html', ID=instru[0], name=instru[1], dept_name=instru[2], salary=instru[3], data=edited)
    if request.method == "POST":
        myID = request.form["ID"]
        myName = request.form["name"]
        myDept = request.form["dept"]
        mySalary = request.form["salary"]
        cursor = db.cursor()
        sql = """
                update instructor
                SET name = %s, dept_name = %s, salary = %s
                WHERE ID = %s
              """
        cursor.execute(sql, [myName, myDept, mySalary, myID])
        db.commit()
        cursor.close()
        return redirect(url_for("displayInstructors"))
    

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ Timeslot ////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////////////

@app.route("/timeslot", methods = ["GET", "POST"])
def displayTimeslots():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from time_slot"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            
            #return f"Done!! Query Result is {data}"
            return render_template('timeslot/timeslot.html', data=data)
    if request.method == 'POST':  
            action = request.form["action"]
            if action == "delete":
                myID = request.form["ID"]
                myDay = request.form["day"]
                cursor = db.cursor()
                sql = """
                    delete from time_slot
                    where time_slot_id = %s and day = %s
                    """
                cursor.execute(sql, [myID, myDay])
                db.commit()
                sql = "select * from time_slot"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('timeslot/timeslot.html',data=data)

@app.route('/newtimeslot', methods = ["GET", "POST"])
def newTimeslot():
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        return render_template('timeslot/newtimeslot.html')
    
    if request.method == "POST":
        myID = request.form["ID"]
        myDay = request.form["day"]
        myStart = request.form["start"]
        myEnd = request.form["end"]
        cursor = db.cursor()
        sql = """
                insert into time_slot(time_slot_id, day, start_time, end_time)
                values (%s, %s, %s, %s)
              """
        cursor.execute(sql, [myID, myDay, myStart, myEnd])
        db.commit()
        cursor.close()
        return redirect(url_for("displayTimeslots"))

@app.route('/edittimeslot/<t_id>/<i_day>', methods = ["GET", "POST"])
def editTimeslot(t_id, i_day):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from time_slot WHERE time_slot_id = %s and day = %s"""
        cursor.execute(sql, [t_id, i_day])
        data = cursor.fetchone()
        cursor.close()
        return render_template('timeslot/edittimeslot.html', ID=t_id, day=i_day, start=data[2], end=data[3])
    if request.method == "POST":
        myID = request.form["ID"]
        myDay = request.form["day"]
        myStart = request.form["start"]
        myEnd = request.form["end"]
        cursor = db.cursor()
        sql = """
                update time_slot
                SET start_time = %s, end_time = %s
                WHERE time_slot_id = %s and day = %s
              """
        cursor.execute(sql, [myStart, myEnd, myID, myDay])
        db.commit()
        cursor.close()
        return redirect(url_for("displayTimeslots"))

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\///////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ASSIGN ////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////////////

@app.route("/teachertoclass", methods = ["GET", "POST"])
def displayTeaches():
    if session["permissions"] != "ADMIN":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from teaches"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            
            #return f"Done!! Query Result is {data}"
            return render_template('assignteacher/teachertoclass.html', data=data)
    if request.method == 'POST':  
            action = request.form["action"]
            if action == "delete":
                myID = request.form["ID"]
                myCourse = request.form["class"]
                mySection = request.form["section"]
                mySemester = request.form["semester"]
                myYear = request.form["year"]
                cursor = db.cursor()
                sql = """
                    delete from teaches
                    where ID = %s and course_id = %s and sec_id = %s and semester = %s and year = %s
                    """
                cursor.execute(sql, [myID, myCourse, mySection, mySemester, myYear])
                db.commit()
                sql = "select * from teaches"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()    
                return render_template('assignteacher/teachertoclass.html',data=data)
                

@app.route('/assign', methods = ["GET", "POST"])
def assignInstructor():
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from instructor"""
        cursor.execute(sql)
        instructors = cursor.fetchall()
        sql = """select * from section"""
        cursor.execute(sql)
        sections = cursor.fetchall()
        cursor.close()
        return render_template('assignteacher/assign.html', instructors=instructors, sections=sections)
    
    if request.method == "POST":
        myTeach = request.form["teach"]
        myCourse = request.form["course_id"]
        mySection = request.form["sec_id"]
        mySemester = request.form["semester"]
        myYear = request.form["year"]

        cursor = db.cursor()
        sql = """
                insert into teaches(ID, course_id, sec_id, semester, year)
                values (%s, %s, %s, %s, %s)
              """
        cursor.execute(sql, [myTeach, myCourse, mySection, mySemester, myYear])
        db.commit()
        cursor.close()
        return redirect(url_for("displayTeaches"))
    
@app.route('/changeinstructor/<i_id>/<course_id>/<sec_id>/<semester>/<year>', methods = ["GET", "POST"])
def changeInstructor(i_id, course_id, sec_id, semester, year):
    if session["permissions"] != "ADMIN":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from instructor"""
        cursor.execute(sql)
        instructors = cursor.fetchall()
        sql = """select * from section"""
        cursor.execute(sql)
        sections = cursor.fetchall()
        cursor.close()
        return render_template('assignteacher/changeinstructor.html', instructor=i_id, course=course_id, section=sec_id, semester=semester, year=year, instructors=instructors)
    
    if request.method == "POST":
        myTeach = request.form["teach"]

        cursor = db.cursor()
        sql = """
                update teaches
                set ID = %s
                where course_id = %s and sec_id = %s and semester = %s and year = %s and ID = %s
              """
        cursor.execute(sql, [myTeach, course_id, sec_id, semester, year, i_id])
        db.commit()
        cursor.close()
        return redirect(url_for("displayTeaches"))

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ADVISOR STUFF /////////////////////////////////////
@app.route('/assignadvisor', methods = ["GET", "POST"])
def assignAdvisor():
    if session["permissions"] != "INSTRUCTOR":
        return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from student where stu_ID in (select s_ID from advisor where i_ID = %s)"""
        cursor.execute(sql, [session["instructor_id"]])
        data = cursor.fetchall()
        cursor.close()
        return render_template('advisor/assignadvisor.html', data=data)
    
    if request.method == "POST":
        action = request.form["action"]
        if action == "delete":
            myID = request.form["ID"]
            cursor = db.cursor()
            sql = """
                delete from advisor
                where s_id = %s and i_id = %s
                """
            cursor.execute(sql, [myID, session["instructor_id"]])
            db.commit()
            sql = """select * from student where stu_ID in (select s_ID from advisor where i_ID = %s)"""
            cursor.execute(sql, [session["instructor_id"]])
            data = cursor.fetchall()
            cursor.close()    
            return render_template('advisor/assignadvisor.html', data=data)

@app.route('/assignstudenttoadvisor', methods = ["GET", "POST"])
def assignStudentToAdvisor():
    if session["permissions"] != "INSTRUCTOR":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select stu_ID, name from student where stu_ID not in (select s_ID from advisor)"""
        cursor.execute(sql)
        students = cursor.fetchall()
        cursor.close()
        return render_template('advisor/assignstudenttoadvisor.html', students=students)
    
    if request.method == "POST":
        myStudent = request.form["student"]

        cursor = db.cursor()
        sql = """
                insert into advisor(s_ID, i_ID)
                values (%s, %s)
              """
        cursor.execute(sql, [myStudent, session["instructor_id"]])
        db.commit()
        cursor.close()
        return redirect(url_for("assignAdvisor"))

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ GRADE STUFF ////////////////////////////////////////
@app.route('/grades',  methods = ['GET','POST'])
def gradePage():
    if session["permissions"] != "INSTRUCTOR":
        return
    if request.method == 'GET':
        #Function with pymysql
        cursor = db.cursor()
        sql = """ 
                select student.name, takes.stu_ID, takes.course_id, takes.sec_id, takes.semester, takes.year, takes.grade
                from student, takes 
                where (course_id, sec_id, semester, year) in (
                    select course_id, sec_id, semester, year 
                    from teaches 
                    where ID = %s
                ) && student.name in (select name from student where stu_ID = takes.stu_ID)
            """
        cursor.execute(sql, [session["instructor_id"]]) 
        data = cursor.fetchall()
        cursor.close()
        return render_template('grades/grades.html', data=data)
    return render_template('grades/grades.html')

@app.route('/updategrade/<stu_ID>/<course_id>/<sec_id>/<semester>/<year>/<grade>', methods = ["GET", "POST"])
def editGrade(stu_ID, course_id, sec_id, semester, year, grade):
    if session["permissions"] != "INSTRUCTOR":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """ 
                select * from takes where stu_ID = %s AND course_id = %s AND sec_id = %s AND semester = %s AND year = %s AND grade = %s
            """
        cursor.execute(sql, [stu_ID, course_id, sec_id, semester, year, grade])
        takes = cursor.fetchone()
        return render_template('grades/updategrade.html', takes=takes)
    if request.method == "POST":
        cursor = db.cursor()
        newGrade = request.form["grade"]
        print([newGrade, stu_ID, course_id, sec_id, semester, year])

        sql = """ 
                update takes 
                set grade = %s
                where stu_ID = %s AND course_id = %s AND sec_id = %s AND semester = %s AND year = %s
            """
        cursor.execute(sql, [newGrade, stu_ID, course_id, sec_id, semester, year])
        db.commit()
        cursor.close()
        return redirect(url_for("gradePage"))
        

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ PREREQ ///////////////////////////////////////////////
@app.route("/prereq", methods = ["GET", "POST"])
def prereqPage():
    if session["permissions"] != "INSTRUCTOR":
             return
    if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from prereq;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            print(data)
            #return f"Done!! Query Result is {data}"
            return render_template('prereq/prereq.html', data=data)
    if request.method == 'POST':
            action = request.form["action"]
            if action == "delete":
                course_id = request.form["course_id"]
                prereq_id = request.form["prereq_id"]
                cursor = db.cursor()
                sql = """
                    delete from prereq
                    where course_id = %s AND prereq_id = %s
                    """
                cursor.execute(sql, [course_id, prereq_id])
                sql = "select * from prereq"
                cursor.execute(sql)
                db.commit()
                data = cursor.fetchall()
                cursor.close()    
                return render_template('prereq/prereq.html',data= data)

@app.route('/editprereq/<course_id>/<prereq_id>', methods = ["GET", "POST"])
def editPrereq(course_id, prereq_id):
    if session["permissions"] != "INSTRUCTOR":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select * from prereq WHERE course_id = %s AND prereq_id = %s"""
        cursor.execute(sql, [course_id, prereq_id])
        course = cursor.fetchone()
        sql = """select course_id from course"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('prereq/editprereq.html', courseID=course_id, prereqID=prereq_id, data=edited)
    if request.method == "POST":
        newCourseID = request.form["course_id"]
        newPrereqID = request.form["prereq_id"]
        cursor = db.cursor()
        print([newCourseID, newPrereqID, course_id, prereq_id])
        sql = """
                update prereq
                set prereq_id = %s
                WHERE course_id = %s AND prereq_id = %s
              """
        cursor.execute(sql, [newPrereqID, course_id, prereq_id])
        db.commit()
        cursor.close()
        return redirect(url_for("prereqPage"))

@app.route('/newPrereq', methods = ["GET", "POST"])
def newPrereq():
    if session["permissions"] != "INSTRUCTOR":
             return
    if request.method == "GET":
        cursor = db.cursor()
        sql = """select course_id from course"""
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        edited = []
        for i in data:
            edited.append(i[0])
        return render_template('prereq/newprereq.html', data=edited)
    
    if request.method == "POST":
        myCourse = request.form["course_id"]
        myPrereq = request.form["prereq_id"]
        cursor = db.cursor()
        sql = """
                insert into prereq(course_id, prereq_id)
                values (%s, %s)
              """
        cursor.execute(sql, [myCourse, myPrereq])
        db.commit()
        cursor.close()
        return redirect(url_for("prereqPage"))

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ LOGIN AND REGISTER PAGES ////////////////////////////////
@app.route('/login',  methods = ['GET','POST'])
def loginPage():
    msg = ''
    if request.method == "POST":
        myUser = request.form["username"]
        myPassword = request.form["password"]

        cursor = db.cursor()
        sql = """select * from accounts where username = %s"""
        cursor.execute(sql, [myUser])
        account = cursor.fetchone()

        if account:
            if check_password_hash(account[4], myPassword):
                msg = "Logged in!"
                session["logged-in"] = True
                session["id"] = account[0]
                session["student_id"] = account[1]
                session["instructor_id"] = account[2]
                session["username"] = account[3]
                session["email"] = account[5]
                session["permissions"] = account[6]
                return redirect(url_for('profilePage'))
            else:
                msg = "Invalid username or password"
        else:
            msg = "Invalid username or password"

    return render_template('login.html', msg=msg)

@app.route('/register', methods = ['GET','POST'])
def registerPage():
    accOptions = ["STUDENT", "INSTRUCTOR", "ADMIN"]
    msg = ''
    cursor = db.cursor()
    if request.method == "POST":
        myID = request.form["id"]
        myUser = request.form["username"]
        myPassword = request.form["password"]
        myPerm = request.form["option"]
        myEmail = request.form["email"]

        sql = """select * from accounts where username = %s"""
        cursor.execute(sql, [myUser])
        account = cursor.fetchall()
        # Checks if account exists and if the email or password are invalid
        if account:
            msg = "User already exists!"
            return render_template('register.html', options=accOptions, msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', myEmail):
            msg = 'Invalid email address!'
            return render_template('register.html', options=accOptions, msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', myUser):
            msg = 'Username must contain only characters and numbers!'
            return render_template('register.html', options=accOptions, msg=msg)
        elif not myUser or not myPassword or not myEmail:
            msg = 'Please fill out the form!'
            return render_template('register.html', options=accOptions, msg=msg)
        else:
            hashedPassword = generate_password_hash(myPassword)

        sql = """"""
        # Changes SQL query based off of what type of account is being made
        if myPerm == "STUDENT":
            sql = """
                    insert into accounts (student_id, username, password, email, permissions)
                    values (%s, %s, %s, %s, %s)
                """
            cursor.execute(sql, [myID, myUser, hashedPassword, myEmail, myPerm])
        elif myPerm == "INSTRUCTOR":
            sql = """
                    insert into accounts (instructor_id, username, password, email, permissions)
                    values (%s, %s, %s, %s, %s)
                """
            cursor.execute(sql, [myID, myUser, hashedPassword, myEmail, myPerm])
        elif myPerm == "ADMIN":
            sql = """
                    insert into accounts (username, password, email, permissions)
                    values (%s, %s, %s, %s)
                """
            cursor.execute(sql, [myUser, hashedPassword, myEmail, myPerm])
        db.commit()
        cursor.close()
        msg = "Account created!"
        
    return render_template('register.html', options=accOptions, msg=msg)

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ INSTRUCTOR SECTION PAGE //////////////////////////////////////
@app.route('/instructorsectionsearch', methods = ['GET','POST'])
def instructorSectionSearchPage():
    if session["permissions"] != "INSTRUCTOR":
        return redirect(url_for('loginPage'))
    if request.method == 'GET':
        cursor = db.cursor()
        sql = """select year from section group by year order by year"""
        cursor.execute(sql)
        years = cursor.fetchall()
        cursor = db.cursor()
        sql = """select semester from section group by semester order by semester"""
        cursor.execute(sql)
        semesters = cursor.fetchall()
        
        return render_template('instructorsection/instructorsectionsearch.html', years=years, semesters=semesters)
    if request.method == 'POST':
        year = request.form["year"]
        semester = request.form["semester"]
        return redirect(url_for('instructorSectionPage', year=year, semester=semester))
    return render_template('instructorsection/instructorsectionsearch.html')

@app.route('/instructorsection/<year>/<semester>', methods = ['GET','POST'])
def instructorSectionPage(year, semester):
    if session["permissions"] != "INSTRUCTOR":
        return redirect(url_for('loginPage'))
    if request.method == 'GET':
        cursor = db.cursor()
        # shitty SQL query here but I don't give a damn -Z
        sql = """
                select * from section where exists (
                    select * from teaches 
                    where ID = %s AND year = %s AND semester = %s AND 
                    section.course_id = teaches.course_id AND
                    section.sec_id = teaches.sec_id AND
                    section.semester = teaches.semester AND
                    section.year = teaches.year
                ) 
            """
        cursor.execute(sql, [session["instructor_id"], year, semester])
        sections = cursor.fetchall()
        print(sections)
        cursor.close()
        return render_template('instructorsection/instructorsection.html', data=sections)
    if request.method == 'POST':
        courseID = request.form["course_id"]
        secID = request.form["sec_id"]
        semester = request.form["semester"]
        year = request.form["year"]
        return redirect(url_for('instructorSectionInspectPage', courseID=courseID, secID=secID, semester=semester, year=year))
    return render_template('instructorsection/instructorsection.html')

@app.route('/instructorsectioninspect/<courseID>/<secID>/<year>/<semester>', methods = ['GET','POST'])
def instructorSectionInspectPage(courseID, secID, year, semester):
    if session["permissions"] != "INSTRUCTOR":
        return redirect(url_for('loginPage'))
    if request.method == 'GET':
        cursor = db.cursor()
        sql = """
                select * from student where stu_ID in (
                    select stu_ID from takes 
                    where course_id = %s AND sec_id = %s AND year = %s AND semester = %s 
                ) 
            """
        cursor.execute(sql, [courseID, secID, year, semester])
        students = cursor.fetchall()
        cursor.close()
        print(students)
        return render_template('instructorsection/instructorsectioninspect.html', data=students)
    if request.method == 'POST':
        stu_ID = request.form["ID"]
        cursor = db.cursor()
        sql = "delete from takes where stu_ID = %s AND course_id = %s AND sec_id = %s AND year = %s AND semester = %s"
        cursor.execute(sql, [stu_ID, courseID, secID, year, semester])
        db.commit()
        sql = """
                select * from student where stu_ID in (
                    select stu_ID from takes 
                    where course_id = %s AND sec_id = %s AND year = %s AND semester = %s 
                ) 
            """
        cursor.execute(sql, [courseID, secID, year, semester])
        students = cursor.fetchall()
        cursor.close()    
        return render_template('instructorsection/instructorsectioninspect.html', data=students)
    return render_template('instructorsection/instructorsectioninspect.html')

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ PROFILE PAGE ////////////////////////////////////////////
@app.route('/profile', methods = ['GET','POST'])
def profilePage():
    cursor = db.cursor()
    if request.method == "GET":
        if 'logged-in' in session:
            cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
            account = cursor.fetchone()
            userData = {}
            if session["permissions"] == "INSTRUCTOR": 
                cursor.execute('SELECT * FROM instructor WHERE id = %s', [session["instructor_id"]])
                userData = cursor.fetchone()
            if session["permissions"] == "STUDENT": 
                cursor.execute('SELECT * FROM student WHERE stu_ID = %s', [session["student_id"]])
                userData = cursor.fetchone()
            return render_template('profile.html', account=account, user_data = userData)
    if request.method == "POST":
        action = request.form["action"]
        if action == "update": 
            newUsername = request.form["username"]
            newPassword = request.form["password"]
            if newPassword == "":
                sql = """
                    update accounts
                    set
                        username = %s
                    WHERE id = %s
                    """
                cursor.execute(sql, [newUsername, session["id"]])
                db.commit()
            else:
                sql = """
                    update accounts
                    set
                        username = %s,
                        password = %s
                    WHERE id = %s
                    """
                cursor.execute(sql, [newUsername, generate_password_hash(newPassword), session["id"]])
                db.commit()
            
            if session["permissions"] == "INSTRUCTOR": 
                newName = request.form["name"]
                sql = """
                    update instructor
                    set
                        name = %s
                    WHERE id = %s
                    """
                cursor.execute(sql, [newName, session["instructor_id"]])
            if session["permissions"] == "STUDENT":
                newName = request.form["name"]
                sql = """
                    update student
                    set
                        name = %s
                    WHERE stu_ID = %s
                    """
                cursor.execute(sql, [newName, session["student_id"]])
                db.commit()
                print(session["student_id"])

            return redirect(url_for('profilePage'))
        if action == "log_out":
            session.pop('logged-in', None)
            session.pop('student_id', None)
            session.pop('instructor_id', None)
            session.pop('username', None)
            session.pop('email', None)
            session.pop('permissions', None)
            return redirect(url_for('loginPage'))
    cursor.close()
    return redirect(url_for('loginPage'))

if __name__ == '__main__':    
    cursor = db.cursor()
    sql = "SELECT * from student;"
    cursor.execute(sql)            
    data = cursor.fetchall()    
    cursor.close()
    finalList = []
    dictionary = {}
    for item in data:        
        dictionary = {}
        dictionary['_id'] = item[0]
        dictionary['name'] = item[1]
        dictionary['dept_name'] = item[2]
        dictionary['credits'] = int(item[3])
        finalList.append(dictionary)
    
    pretty_json = json.dumps(finalList, indent=4)
    #print(pretty_json)
    cursor = db.cursor()
    sql = "SELECT * from student;"
    cursor.execute(sql)            
    data = cursor.fetchall()    
    cursor.close()
    finalList = []
    dictionary = {}
    for item in data:        
        dictionary = {}
        dictionary['_id'] = item[0]
        dictionary['name'] = item[1]
        dictionary['dept_name'] = item[2]
        dictionary['tot_cred'] = int(item[3])
        finalList.append(dictionary)
    
    pretty_json = json.dumps(finalList, indent=4)
    #print(pretty_json)
    app.run(port = 4500)
"""
    cursor = dblocal.cursor()
    sql = "SELECT * from advisor;"
    cursor.execute(sql)            
    data = cursor.fetchall()    
    cursor.close()
    finalList = []
    dictionary = {}
    for item in data:        
        dictionary = {}
        dictionary['_id_student'] = item[0]
        dictionary['_id_instructor'] = item[1]
        finalList.append(dictionary)
    
    pretty_json = json.dumps(finalList, indent=4)
    print(pretty_json)"""