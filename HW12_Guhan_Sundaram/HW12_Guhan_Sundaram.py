from flask import Flask, render_template
import sqlite3
from collections import defaultdict
import os.path

app = Flask(__name__)

@app.route('/table')
def table():
    try:
        fp = os.path.join(os.path.dirname(__file__), 'hw11.db')
        database = sqlite3.connect(fp)
        query = "select instructors.CWID, instructors.name, instructors.Dept, grades.Course, count(*) as Number_of_Students from instructors join grades on instructors.CWID = grades.InstructorCWID group by grades.Course, grades.instructorCWID order by instructors.CWID asc"
        result = database.execute(query)
        data = [{'CWID': cwid, 'Name': name, 'Department': dept, 'Course': course, 'Students': students} for cwid, name, dept, course, students in result]
        return render_template('table.html', title='Stevens Repository', table_title='Courses and Student Counts', data=data)
    except Exception as e:
        # Outputs all exceptions to HTML
        return render_template('exception.html', exception = e)

app.run(debug=True)
