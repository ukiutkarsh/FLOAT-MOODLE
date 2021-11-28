import django.core.mail as dcm
from course.models import Membership
from instructor.models import Course
import matplotlib.pyplot as plt

def send_email( subject, message, email_from, recipient_list, html_message ):
    try:
        if html_message:
            dcm.send_mail( subject, message, email_from, recipient_list, html_message=html_message ) 
        else :
            dcm.send_mail( subject, message, email_from, recipient_list ) 
        print('success', recipient_list)
    except :
        print('Email failed')

def course_invite_text(course_name,access_code):
    text = "Welcome to Float Moodle." + "\n" + "The access code for " + course_name + " is " + access_code+"\n"+"You can join the course by entering this code." "\n \n Sent by team BruteForces."
    return text

def course_resource_text(course_name,link):
    text = "New resource added for course " + course_name + ". \n You can view it at the following link "+link+"\n Sent by team BruteForces."
    return text

def course_assignment_text(course_name,link,deadline):
    text = "New Assignment added for course " + course_name + ".\n Deadline for the assignment is "+str(deadline)+ ". \n You can view it at the following link "+link+"\n Sent by team BruteForces."
    return text

def TA_text(course_name):
    text = "Welcome to Float Moodle."+"\n" +"You have been added as a TA for the course " + course_name + "\n \n Sent by team BruteForces."
    return text

def email_from():
    return "shah.adish13@gmail.com"

def get_student_emails(course_id):
    memberships = Membership.objects.filter(course=course_id)
    course = Course.objects.get(id=course_id)
    email_list = []
    for membership in memberships:
        email_list.append(membership.student.user.email)
    return email_list
