from datetime import datetime, timedelta
from prettytable import PrettyTable
from collections import defaultdict
import os
import sqlite3

def file_reading_gen(path, fields, sep=',', header=False):
    """ Reads file with fixed number of fields with seperator"""

    try:
        lineCounter = 1
        for row in open(path, 'r'):
            if(header):
                tup = tuple(row.rstrip('\n').split(sep))
                if(len(tup) != fields):
                    raise ValueError(path + " has " + str(len(tup)) + " fields on line " + str(
                        lineCounter) + " but expected " + str(fields))
                header = False
                lineCounter += 1
                continue
            else:
                tup = tuple(row.rstrip('\n').split(sep))
                if(len(tup) != fields):
                    raise ValueError(path + " has " + str(len(tup)) + " fields on line " + str(
                        lineCounter) + " but expected " + str(fields))
                lineCounter += 1
                yield tup
    except FileNotFoundError as e:
        raise e

class Student:
    """Details for given student"""

    def __init__(self, scwid, sname, major):
        self.scwid = scwid
        self.sname = sname
        self.major = major
        self.courses = defaultdict(str)
        self.requiredCourses = []
        self.electiveCourses = []

    def addCourse(self, cname, cgrade, cscwid):
        if(self.scwid == cscwid):
            self.courses[cname] = cgrade

    def remainingRequiredCourses(self, major):
        if(major.mname == self.major):
            reqList = major.requiredCourses
            for reqCourse in reqList:
                if(reqCourse not in self.courses.keys()):
                    self.requiredCourses.append(reqCourse)
                elif(self.courses[reqCourse] not in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']):
                    self.requiredCourses.append(reqCourse)

    def remainingElectiveCourses(self, major):
        counter = 0
        if(major.mname == self.major):
            eleList = major.electiveCourses
            for eleCourse in eleList:
                if(eleCourse in self.courses.keys()):
                    if(self.courses[eleCourse] in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']):
                        counter += 1
            if(counter == 0):
                self.electiveCourses = major.electiveCourses

class Instructor:
    """Details for given instructor"""

    def __init__(self, icwid, iname, dept):
        self.icwid = icwid
        self.iname = iname
        self.dept = dept
        self.courses = defaultdict(int)

    def addCourse(self, cname, cicwid):
        if(self.icwid == cicwid):
            self.courses[cname] += 1

class Major:
    """Details for each major"""

    def __init__(self, mname):
        self.mname = mname
        self.requiredCourses = []
        self.electiveCourses = []

    def addCourseToMajor(self, cname, re):
        if(re == 'R'):
            self.requiredCourses.append(cname)
        elif(re == 'E'):
            self.electiveCourses.append(cname)
        else:
            raise Exception('Course ' + cname + ' has required/elective as ' + re + ' when it must be R or E')

class Repository:
    """Details for entire university"""

    def __init__(self, fileLocation):
        self.students = defaultdict(str)
        self.instructors = defaultdict(str)
        self.majors = defaultdict(str)
        self.fileLocation = fileLocation
        if not os.path.exists(self.fileLocation):
            raise Exception("File directory not found")

    def inputValues(self):
        """Finds all the input values for the tables"""
        try:
            for scwid, sname, major in file_reading_gen(os.path.join(self.fileLocation, 'students.txt'), 3, sep='\t', header=True):
                self.students[scwid] = Student(scwid, sname, major)

            for icwid, iname, dept in file_reading_gen(os.path.join(self.fileLocation, 'instructors.txt'), 3, sep='\t', header=True):
                self.instructors[icwid] = Instructor(icwid, iname, dept)

            for scwid, cname, cgrade, icwid in file_reading_gen(os.path.join(self.fileLocation, 'grades.txt'), 4, sep='\t', header=True):
                if(scwid in self.students.keys()):
                    self.students[scwid].addCourse(cname, cgrade, scwid)
                else:
                    raise Exception("Student " + scwid + " not in students.txt")

                if(icwid in self.instructors.keys()):
                    self.instructors[icwid].addCourse(cname, icwid)
                else:
                    raise Exception("Instructor " + icwid + " not in instructors.txt")

            for mname, re, cname in file_reading_gen(os.path.join(self.fileLocation, 'majors.txt'), 3, sep='\t', header = True):
                if mname not in self.majors.keys():
                    self.majors[mname] = Major(mname)
                    self.majors[mname].addCourseToMajor(cname, re)
                else:
                    self.majors[mname].addCourseToMajor(cname, re)

            for stu in self.students.values():
                for maj in self.majors.values():
                    stu.remainingRequiredCourses(maj)

            for stu in self.students.values():
                for maj in self.majors.values():
                    stu.remainingElectiveCourses(maj)
        except FileNotFoundError as e:
            print(e)


    def instructor_table_db(self, db_path):
        """Uses database query to output instructor table"""

        try:
            database = sqlite3.connect(db_path)
            query = "select instructors.CWID, instructors.name, instructors.Dept, grades.Course, count(*) as Number_of_Students from instructors join grades on instructors.CWID = grades.InstructorCWID group by grades.Course, grades.instructorCWID order by instructors.CWID desc"
            result = database.execute(query)
            pti2 = PrettyTable()
            pti2.field_names = (['CWID', 'Name', 'Dept', 'Course', 'Students'])
            for data in result:
                pti2.add_row(list(data))
            return pti2
        except Exception as e:
            print(e)

def main():

    rep = Repository('/Users/guhan/Desktop')
    rep.inputValues()

    print("Major Summary")
    ptm = PrettyTable()
    ptm.field_names = ["Dept", "Required", "Electives"]
    for maj in rep.majors.values():
        ptm.add_row([maj.mname, maj.requiredCourses, maj.electiveCourses])
    print(ptm)         

    print("Student Summary")
    pts = PrettyTable()
    pts.field_names = ["CWID", "Name", "Major", "Completed Courses", "Remaining Required", "Remaining Electives"]
    for stu in rep.students.values():
        myList = []
        for key in stu.courses:
            myList.append(key)
        myList.sort()
        pts.add_row([stu.scwid, stu.sname, stu.major, myList, stu.requiredCourses, stu.electiveCourses])
    print(pts)

    print("Instructor Summary")
    pti = PrettyTable()
    pti.field_names = ["CWID", "Name", "Dept", "Course", "Students"]
    for ins in rep.instructors.values():
        for coursename, students in ins.courses.items():
            pti.add_row([ins.icwid, ins.iname, ins.dept, coursename, students])        
    print(pti)

    print("New Instructor Summary from Database")
    pti2 = rep.instructor_table_db('/Users/guhan/Desktop/hw11.db')
    print(pti2)


if __name__ == "__main__":
    main()
