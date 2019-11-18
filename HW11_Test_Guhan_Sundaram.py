import unittest
from HW11_Guhan_Sundaram import *

class TestRepo(unittest.TestCase):

    def test_newinslist(self):
        """Tests the sqlite query with the old instructor table"""

        rep = Repository('/Users/guhan/Desktop')
        rep.inputValues()

        pti = PrettyTable()
        pti.field_names = ["CWID", "Name", "Dept", "Course", "Students"]
        for ins in rep.instructors.values():
            for coursename, students in ins.courses.items():
                pti.add_row([ins.icwid, ins.iname, ins.dept, coursename, students])        

        pti2 = rep.instructor_table_db('/Users/guhan/Desktop/hw11.db')

        self.assertTrue(str(pti).startswith("+-------+------------+------+---------+----------+") == str(pti2).startswith("+-------+------------+------+---------+----------+") )
        self.assertTrue("| 98763 | Rowland, J | SFEN | SSW 810 |    4     |" in str(pti) or "| 98763 | Rowland, J | SFEN | SSW 810 |    4     |" in pti2 )


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)