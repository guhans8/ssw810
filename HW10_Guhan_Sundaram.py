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

    remainingReq = []
    remainingEle = []
    courseNames = []

    def __init__(self, scwid, sname, major):
        self.scwid = scwid
        self.sname = sname
        self.major = major
        self.courses = defaultdict(str)

    def addCourse(self, cname, cgrade, ccwid):
        if(self.scwid == ccwid):
            self.courses[cname] = cgrade

    def doCourseNames(self):
        for key, val in self.courses.items():
            self.courseNames.append(key)

    def addUnCourse(self, major, course, re):
        self.doCourseNames()
        if(re == "R"):
            if not(course in self.remainingReq) and not(course in self.courseNames):
                self.remainingReq.append(course)
        elif(re == "E"):
            if not(course in self.remainingEle) and not(course in self.courseNames):
                self.remainingEle.append(course)
        else:
            raise ValueError("Major course must have R or E as R/E value")


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

class Major:
    """Details for each major"""

    def __init__(self, major):
        self.major = major
        self.courses = defaultdict(str)

    def addCourse(self, major, course, re):
        if(self.major == major):
            self.courses[course] = re


def addInstructorsToCourses(instructors):
    """Morphs instructor list to course list"""

    courses = []

    for ins in instructors:
        for course in ins.courses:
            temp = Course(ins.icwid, ins.iname, ins.dept,
                          course, ins.courses[course])
            courses.append(temp)

    return courses


class Repository:
    """Contains data for each university"""

    def __init__(self, uni_name=None):
        self.students = []
        self.instructors = []
        self.majors = []
        self.uni_name = uni_name

    def addStudentToStudents(self, scwid, sname, major):
        self.students.append(Student(scwid, sname, major))

    def addInstructorToInstructors(self, icwid, iname, dept):
        self.instructors.append(Instructor(icwid, iname, dept))

    def addMajorToMajors(self, major):
        self.majors.append(Major(major))

    def readStudents(self):
        for cwid, name, major in file_reading_gen('/Users/guhan/Desktop/students.txt', 3, sep=';', header=True):
            self.addStudentToStudents(cwid, name, major)

    def readInstructors(self):
        for cwid, name, dept in file_reading_gen('/Users/guhan/Desktop/instructors.txt', 3, sep='|', header=True):
            self.addInstructorToInstructors(cwid, name, dept)

    def readMajors(self):
        for majo, tem, tes in file_reading_gen('/Users/guhan/Desktop/majors.txt', 3, sep='\t', header=True):
            temp = 0
            for maj in self.majors:
                if(maj.major == majo):
                    temp = 5
                    break
            if(temp != 5):
                self.addMajorToMajors(majo)

    def readCourses(self):
        for scwid, ccwid, grade, icwid in file_reading_gen('/Users/guhan/Desktop/grades.txt', 4, sep='|', header=True):
            for ins in self.instructors:
                ins.addCourse(ccwid, icwid)
            for stu in self.students:
                stu.addCourse(ccwid, grade, scwid)
        for major, re, course in file_reading_gen('/Users/guhan/Desktop/majors.txt', 3, sep='\t', header=True):
            for maj in self.majors:
                maj.addCourse(major, course, re)

    def addUnCourses(self, students, majors):
        for maj in majors:
            for stu in students:
                if(maj.major == stu.major):
                    for key, val in maj.courses.items():
                        stu.addUnCourse(maj.major, key, val)


def main():
    """Prints out data from txt files"""

    rep = Repository()
    rep.readStudents()
    rep.readInstructors()
    rep.readMajors()
    rep.readCourses()
    rep.addUnCourses(rep.students, rep.majors)

    print("Majors Summary")
    pt0 = PrettyTable()
    pt0.field_names = ["Dept", "Required", "Electives"]
    for maj in rep.majors:
        req = []
        ele = []
        for key, val in maj.courses.items():
            if(val == "R"):
                req.append(key)
            elif(val == "E"):
                ele.append(key)
            else:
                raise ValueError("Major course must have R or E as R/E value")
        pt0.add_row([maj.major, sorted(req), sorted(ele)])
    print(pt0)

    print("Student Summary")
    pt = PrettyTable()
    pt.field_names = ["CWID", "Name", "Major", "Completed Courses",
                      "Remaining Required", "Remaining Electives"]
    for stu in rep.students:
        myList = []
        for key in stu.courses:
            myList.append(key)
        myList.sort()

        reqs = []
        for key in stu.remainingReq:
            reqs.append(key)

        eles = []
        for key in stu.remainingEle:
            eles.append(key)

        pt.add_row([stu.scwid, stu.sname, stu.major, myList, reqs, eles])
    print(pt)

    print("Instructor Summary")
    pt3 = PrettyTable()
    pt3.field_names = ["CWID", "Name", "Dept", "Course", "Students"]
    for co in addInstructorsToCourses(rep.instructors):
        pt3.add_row([co.cwid, co.name, co.dept, co.course, co.students])
    print(pt3)


if __name__ == "__main__":
    main()
