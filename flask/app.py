#! /usr/bin/python3
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import config

#for the pymysql look at the faculty url, on that the two ways to access the CS database will be shown


#Configuration for pymysql
db = config.dblocal



app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello')
def hello():
    return 'Hello message'

@app.route('/hellothere')
def hellothere():
    name =  "General Kenobi"
    return render_template("hellothere.html", values=name)

@app.route('/search',  methods = ['GET','POST'])
def search():
    if request.method == 'POST':
        myName = request.form['name']
        myId = request.form['id']
        values = {
            'name': myName,
            'id': myId }
        return render_template('results.html', **values)
    if request.method == 'GET':
        return render_template('form.html')

@app.route('/values')
def values():
    myInteger = 3
    return render_template('values.html', value = myInteger)

@app.route('/pokedex')
def loop():
    pokedex = ["Pikachu", "Charizard", "Squirtle", "Jigglypuff",  
           "Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia", "Gyarados"]     
    return render_template('pokedex.html', pokedex = pokedex)
       
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
    
@app.route('/countfaculty',  methods = ['GET','POST'])
def countFaculty():
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
        return render_template('count.html', data = edited)
    if request.method == 'POST':
        dept = request.form['depts']  
        cursor = db.cursor()      
        sql = "SELECT dept_count(%s);"
        cursor.execute(sql,[dept])
        data = cursor.fetchall()
        cursor.close()
        edited = []
        print(data)
        for i in data:
            edited.append(i[0])
        return render_template('total.html', data=edited[0])
    
@app.route('/function',  methods = ['GET','POST'])
def countdeptfuntion():
    if request.method == 'POST':
        if request.method == 'POST':
            dept = request.form['dept']        
            cursor = db.cursor()
            sql = "SELECT dept_count(%s);"
            cursor.execute(sql, [dept])
            data = cursor.fetchall()
            cursor.close()
            edited = []
            for i in data:
                edited.append(i[0])
        return render_template('countdept.html', data = edited[0])
    if request.method == 'GET':
        cursor = db.cursor()
        sql ="SELECT dept_name as dept_name from department;"
        cursor.execute(sql)
        data = cursor.fetchall()        
        cursor.close()
        edited = []
        print(data)
        for i in data:
            edited.append(i[0])
        return render_template('function.html', data = edited)

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