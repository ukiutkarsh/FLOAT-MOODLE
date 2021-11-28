from getpass import getpass
from colorama import init
import requests

init()
isInstructor = input("Type 'yes' if you are an instructor : ")
if isInstructor=="yes":
    username = input("Enter username : ")
    name = input("Enter your name : ")
    password = getpass()
else:
    username = input("Enter username : ")
    roll_num = input("Enter Roll Number : ")
    password = getpass()

while True:
    # command to view courses
    cmd = input('Float_Moodle $ ')
    if (cmd =='courses'):
        response = requests.post('http://127.0.0.1:8000/cli/courses/', data = {'username':username, 'roll_num':roll_num, 'password':password})
        try:
            course_list = response.json()['courses']
            instructor_list = response.json()['instructors']
            for i in range(len(course_list)):
                print(str(i+1)+" Course Name : " + course_list[i] + " Instructor Name : " + instructor_list[i])
        except Exception as e:
            print("Error- ", e)
    
    # Command to view pending assignments and resources
    elif (cmd =='pending'):
        try:
            response = requests.post('http://127.0.0.1:8000/cli/pending/', data = {'username':username,'roll_num':roll_num, 'password':password})
            print(response.json())
            course_list = response.json()['courses']
            pending_assignments_list = response.json()['pending_assignments_list']
            pending_resources_list = response.json()['pending_resources_list']
            for i in range(len(course_list)):
                print(str(i+1)+ " Course Name :" + course_list[i])
                print(" Pending Assignments :")
                print(pending_assignments_list[i])
                print(" Pending Resources :")
                print(pending_resources_list[i])
        except Exception as e:
            print("Error- ", e)
    
    elif (cmd =='students_enrolled'):
        response = requests.post('http://127.0.0.1:8000/cli/student_list/', data = {'username':username,'name':name,'password':password})
        try:
            course_list = response.json()['courses']
            student_list = response.json()['student_list']
            for i in range(len(course_list)):
                print(str(i+1)+" Course Name : " + course_list[i] + " Instructor Name : " + instructor_list[i])
        except Exception as e:
            print("Error- ", e)
