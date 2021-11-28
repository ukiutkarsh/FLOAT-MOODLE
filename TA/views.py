## @brief Views for the instructor app.
import os
from wsgiref.util import FileWrapper
from django.contrib.auth.decorators import login_required

from TA.models import TeachingAssistant,TA_ship
from instructor.models import Feedback, Instructor, Submission, Assignment
from course.models import Course, Message, Notification, Student
from django.shortcuts import render, HttpResponse, redirect
from instructor.forms import AssignmentForm, NotificationForm, ResourceForm, FeedbackForm, SendInviteForm, StudentBulkUploadForm
from course.forms import MessageForm
import datetime,threading
from float_moodle import settings
from instructor.functions import send_email,course_invite_text
from django.utils import timezone


email_from = 'shah.adish13@gmail.com'

@login_required
def TA_index(request):
    user = request.user
    TA = TeachingAssistant.objects.get(user=request.user)
    courses = TA.course_list.all()
    context = {
        'user': user,
        'TA': TA,
        'courses': courses,
    }
    return render(request, 'TA/TA_index.html', context)



@login_required
def TA_detail(request, course_id):
    user = request.user
    TA = TeachingAssistant.objects.get(user=request.user)
    courses = TA.course_list.all()
    course = Course.objects.get(id=course_id)
    instructor = course.instructor
    messages = Message.objects.filter(course=course)
    form = MessageForm(request.POST or None)
    disabled_forum = course.disabled_forum

    if request.method == 'POST':
        if form.is_valid():
            message = form.save(commit=False)
            message.course = course
            message.sender = user
            message.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y') # get the current date,time and convert into string
            message.save()
            try:
                student = Student.objects.get(user=request.user)
                return redirect('course:detail', course_id)

            except:
                return redirect('TA:TA_detail', course.id)

    else:
        form = MessageForm()

        context = {
                'user': user,
                'instructor': instructor,
                'course': course,
                'courses': courses,
                'messages': messages,
                'form' : form,
                'disabled_forum':disabled_forum,
                'TA':TA
            }

        return render(request, 'TA/TA_detail.html', context)


@login_required
def add_notification(request, course_id):
    course = Course.objects.get(id=course_id)
    TA = TeachingAssistant.objects.get(user=request.user)
    taship = TA_ship.objects.get(TA= TA, course = course)
    if taship.can_notify:    
        form = NotificationForm(request.POST or None)
        course = Course.objects.get(id=course_id)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.course = course
            notification.time = timezone.now().strftime('%H:%M, %d/%m/%y') # get the current date,time and convert into string
            notification.save()
            return redirect('TA:TA_detail', course.id)
        return render(request, 'TA/add_notification.html', {'course': course, 'form': form})
    else:
        return render(request,'TA/access_denied.html',{'course':course})


@login_required
def add_assignment(request, course_id):
    course = Course.objects.get(id=course_id)
    TA = TeachingAssistant.objects.get(user=request.user)
    taship = TA_ship.objects.get(TA= TA, course = course)

    if taship.can_add_assignments:
        form = AssignmentForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.file = request.FILES['file']
            assignment.post_time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
            assignment.course = course
            assignment.save()
            #increase total for course
            course.total +=1
            course.save()
            if taship.can_notify:
                notification = Notification()
                notification.content = "New Assignment Uploaded |" + " Due at "+ str(assignment.deadline)[:-9]
                notification.course = course
                notification.time = timezone.now()
                notification.save()
            return redirect('TA:TA_detail', course.id)

        return render(request, 'TA/create_assignment.html', {'form': form, 'course': course})
    else:
        return render(request,'TA/access_denied.html',{'course':course})


@login_required
def TA_add_resource(request, course_id):
    course = Course.objects.get(id=course_id)
    TA = TeachingAssistant.objects.get(user=request.user)
    taship = TA_ship.objects.get(TA= TA, course = course)
    if taship.can_add_resources:    
        form = ResourceForm(request.POST or None, request.FILES or None)
        course = Course.objects.get(id=course_id)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.file_resource = request.FILES['file_resource']
            resource.course = course
            resource.save()
            #increase total for course
            course.total +=1
            course.save()
            if taship.can_notify:
                notification = Notification()
                notification.content = "New Resource Added - " + resource.title
                notification.course = course
                notification.time = timezone.now()
                notification.save()
            return redirect('TA:TA_detail', course.id)

        return render(request, 'TA/add_resource.html', {'form': form, 'course': course})
    else:
        return render(request,'TA/access_denied.html',{'course':course})



# # view for the assignments page of a course.
# # This view is called by <course_id>/view_all_assignments url.\n
# # It returns the webpage containing all the assignments of the course and links to their submissions and feedbacks given by the students.
# @login_required
# def view_all_assignments(request, course_id):
#     course = Course.objects.get(id=course_id)
#     assignments = Assignment.objects.filter(course=course)
#     return render(request, 'instructor/view_all_assignments.html', {'assignments' : assignments,'course': course})


# # view for the submissions page of an assignment.
# # This view is called by <assignment_id>/view_all_submissions url.\n
# # It returns the webpage containing links to all the submissions of an assignment.
# @login_required
# def view_all_submissions(request,assignment_id):
#     assignment = Assignment.objects.get(id=assignment_id)
#     submissions = Submission.objects.filter(assignment=assignment)
#     course = assignment.course
#     return render(request, 'instructor/view_all_submissions.html', {'submissions' : submissions,'course': course})

# @login_required
# def download(request,file_name):
#     file_path = settings.MEDIA_ROOT +'/'+ file_name
#     file_wrapper = FileWrapper(file(file_path,'rb'))
#     file_mimetype = mimetypes.guess_type(file_path)
#     response = HttpResponse(file_wrapper, content_type=file_mimetype )
#     response['X-Sendfile'] = file_path
#     response['Content-Length'] = os.stat(file_path).st_size
#     response['Content-Disposition'] = 'attachment; filename=%s/' % smart_str(file_name) 
#     return response


# view for the feedback page containing an histogram of all the feddbacks provided by the students.
# This view is called by <assignment_id>/view_feedback url.\n
# It returns a webpage containing the feedback received by the students organized in the form of histogram.
# @login_required
# def give_feedback(request, submission_id):
#     form = FeedbackForm(request.POST or None, request.FILES or None)
#     submission = Submission.objects.get(id=submission_id)
#     course = submission.assignment.course
#     if form.is_valid():
#         feedback = form.save(commit=False)
#         feedback.submission = submission
#         feedback.save()
#         # notification = Notification()
#         # notification.content = "Feedback added - " + submission.assignment.description
#         # notification.course = course
#         # notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
#         # notification.save()
#         return redirect('instructor:instructor_detail', course.id)

#     return render(request, 'instructor/give_feedback.html', {'form': form,'course': course})


def send_invite(request,course_id):
    course = Course.objects.get(id=course_id)
    TA = TeachingAssistant.objects.get(user=request.user)
    taship = TA_ship.objects.get(TA= TA, course = course)
    if taship.can_add_students:
        form = SendInviteForm(request.POST or None)
        if form.is_valid():
            email_list = [s.strip() for s in form.cleaned_data.get('email_list').split(",")]
            message = course_invite_text(course.name,course.course_access_code)
            subject = 'Course invitation for course ' + course.name
            recipient_list = email_list
            thread = threading.Thread(target=send_email,args=(subject, message, email_from, recipient_list, None,))
            thread.start()
            return redirect('TA:TA_detail', course.id)
        return render(request, 'TA/send_invite.html', {'course': course, 'form': form})
    else:
        return render(request,'TA/access_denied.html',{'course':course})




# #view to add grades using a csv file
# @login_required
# def add_grades(request, assignment_id):
#     assignment = Assignment.objects.get(id=assignment_id)
#     course = assignment.course
#     if request.method == 'GET':
#         form = StudentBulkUploadForm()
#         return render(request, 'instructor/add_grades.html', {'form':form, 'course':course, 'name':assignment.name})

#     # If not GET method then proceed
#     try:
#         form = StudentBulkUploadForm(data=request.POST, files=request.FILES)
#         if form.is_valid():
#             csv_file = form.cleaned_data['csv_file']

#             file_data = csv_file.read().decode('utf-8')
#             lines = file_data.split('\n')

#             # loop over the lines and save them in db. If error, store as string and then display
#             for line in lines[:-1]:
#                 fields = line.split(',')
#                 student = Student.objects.get(name = str(fields[0]))
#                 submission = Submission.objects.get(user=student.user, assignment=assignment)
#                 marks = fields[1]
#                 content = str(fields[2])
#                 #add feedback
#                 feedback = Feedback()
#                 feedback.content = content
#                 feedback.submission = submission
#                 feedback.marks = marks
#                 feedback.save()
            
#             notification = Notification()
#             notification.content = "Feedback added - " + str(assignment.name)
#             notification.course = course
#             notification.time = timezone.now()
#             notification.save()

#             return redirect('view_all_assignments', course.id)

#     except Exception as e:
#         return redirect('add_grades', assignment_id)
