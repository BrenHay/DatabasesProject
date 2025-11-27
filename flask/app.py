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
        if request.method == 'GET':
            #Function with pymysql
            cursor = db.cursor()
            sql = "SELECT * from student;"
            cursor.execute(sql)            
            data = cursor.fetchall()
            cursor.close()
            print(data)
            #return f"Done!! Query Result is {data}"
            return render_template('student.html', data=data)
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
        "studentschedule.html",
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
        return render_template('newstudent.html', data = edited)
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
        return render_template('newstudent.html', data=edited)
    
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