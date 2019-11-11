from datetime import datetime, timedelta
from prettytable import PrettyTable
from collections import defaultdict
import os


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

    def addCourse(self, cname, cgrade, ccwid):
        if(self.scwid == ccwid):
            self.courses[cname] = cgrade


class Instructor:
    """Details for given instructor"""

    def __init__(self, icwid, iname, dept):
        self.icwid = icwid
        self.iname = iname
        self.dept = dept
        self.courses = defaultdict(int)

    def addCourse(self, cname, ccwid):
        if(self.icwid == ccwid):
            self.courses[cname] += 1

class Course:
    """Details for each course taken from Instructors"""

    def __init__(self, cwid, name, dept, course, students):
        self.cwid = cwid
        self.name = name
        self.dept = dept
        self.course = course
        self.students = students

def addInstructorsToCourses(instructors):
    """Morphs instructor list to course list"""

    courses = []

    for ins in instructors:
        for course in ins.courses:
            temp = Course(ins.icwid, ins.iname, ins.dept, course, ins.courses[course])
            courses.append(temp)

    return courses

class Repository:
    """Contains data for each university"""

    def __init__(self, uni_name=None):
        self.students = []
        self.instructors = []
        self.uni_name = uni_name

    def addStudentToStudents(self, scwid, sname, major):
        self.students.append(Student(scwid, sname, major))

    def addInstructorToInstructors(self, icwid, iname, dept):
        self.instructors.append(Instructor(icwid, iname, dept))

    def readStudents(self):
        for cwid, name, major in file_reading_gen('/Users/guhan/Desktop/students.txt', 3, sep='\t', header=False):
            self.addStudentToStudents(cwid, name, major)

    def readInstructors(self):
        for cwid, name, dept in file_reading_gen('/Users/guhan/Desktop/instructors.txt', 3, sep='\t', header=False):
            self.addInstructorToInstructors(cwid, name, dept)

    def readCourses(self):
        for scwid, ccwid, grade, icwid in file_reading_gen('/Users/guhan/Desktop/grades.txt', 4, sep='\t', header=False):
            for ins in self.instructors:
                ins.addCourse(ccwid, icwid)
            for stu in self.students:
                stu.addCourse(ccwid, grade, scwid)


def main():
    """Prints out data from txt files"""

    rep = Repository()
    rep.readStudents()
    rep.readInstructors()
    rep.readCourses()

    print("Student Summary")
    pt = PrettyTable()
    pt.field_names = ["CWID", "Name", "Completed Courses"]
    for stu in rep.students:
        myList = []
        for key in stu.courses:
            myList.append(key)
        myList.sort()
        pt.add_row([stu.scwid, stu.sname, myList])
    print(pt)

    print("Instructor Summary")
    pt3 = PrettyTable()
    pt3.field_names = ["CWID", "Name", "Dept", "Course", "Students"]
    for co in addInstructorsToCourses(rep.instructors):
        pt3.add_row([co.cwid, co.name, co.dept, co.course, co.students])
    print(pt3)

if __name__ == "__main__":
    main()
