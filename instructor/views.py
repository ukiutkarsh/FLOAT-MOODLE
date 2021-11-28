## @brief Views for the instructor app.
from django.contrib.auth.decorators import login_required

from TA.models import TeachingAssistant,TA_ship
from .models import Feedback, ImageObject, Instructor, Submission, Assignment
from .models import Feedback, Instructor, Submission, Assignment,ProgressInstructor
from course.models import Course, Membership, Message, Notification, Student
from django.shortcuts import render, HttpResponse, redirect
from .forms import AssignmentForm, NotificationForm, ResourceForm, FeedbackForm, SendInviteForm,AddTAForm
from .forms import AssignmentForm, NotificationForm, ResourceForm, FeedbackForm, StudentBulkUploadForm
from course.forms import MessageForm
import datetime,threading
from float_moodle import settings
from .functions import send_email,course_invite_text,TA_text,get_student_emails,course_resource_text
from .functions import course_assignment_text
from django.utils import timezone
from django.template.defaulttags import register
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from django.core.files.base import ContentFile, File
from io import StringIO, BytesIO

# view for the index page of the instructor.
# This view is called by /instructor_index url.\n
# It returns the instructor's homepage containing links to all the courses he teaches.
email_from = 'shah.adish13@gmail.com'

@login_required
def instructor_index(request):
    user = request.user
    instructor = Instructor.objects.get(user=request.user)
    courses = Course.objects.filter(instructor=instructor)
    context = {
        'user': user,
        'instructor': instructor,
        'courses': courses,
    }
    return render(request, 'instructor/instructor_index.html', context)


# view for the detail page of the course.
# This view is called by <course_id>/instructor_detail url.\n
# It returns the course's detail page containing forum and links to add assignment,resource,notifications
# and view all the assignments and their submissions.
@login_required
def instructor_detail(request, course_id):
    user = request.user
    instructor = Instructor.objects.get(user=request.user)
    courses = Course.objects.filter(instructor=instructor)
    course = Course.objects.get(id=course_id)
    messages = Message.objects.filter(course=course)
    form = MessageForm(request.POST or None)
    disabled_forum = course.disabled_forum

    if request.method == 'POST':
        if form.is_valid():
            message = form.save(commit=False)
            message.course = course
            message.sender = user
            message.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
            message.save()
            try:
                student = Student.objects.get(user=request.user)
                return redirect('course:detail', course_id)

            except:
                return redirect('instructor:instructor_detail', course.id)

    else:
        form = MessageForm()
        #find assignments to be graded in this course
        progress = ProgressInstructor.objects.get(instructor=instructor, course = course)
        assignments = Assignment.objects.filter(course = course)
        finished_assignments = progress.assignments

        context = {
                'user': user,
                'instructor': instructor,
                'course': course,
                'courses': courses,
                'messages': messages,
                'form' : form,
                'disabled_forum':disabled_forum,
                'assignments':assignments,
                'finished_assignments':finished_assignments,
            }

        return render(request, 'instructor/instructor_detail.html', context)


# view for the course's add-notification page
# This view is called by <course_id>/add_notification url.\n
# It returns the webpage containing a form to add notification and redirects to the course's detail page again after the form is submitted.
@login_required
def add_notification(request, course_id):
    form = NotificationForm(request.POST or None)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        notification = form.save(commit=False)
        notification.course = course
        notification.time = timezone.now() # get the current date,time and convert into string
        notification.save()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/add_notification.html', {'course': course, 'form': form})


# view for the course's add-assignment page.
# This view is called by <course_id>/add_assignment url.\n
# It returns the webpage containing a form to add an assignment and redirects to the course's detail page again after the form is submitted.
@login_required
def add_assignment(request, course_id):
    form = AssignmentForm(request.POST or None, request.FILES or None)
    course = Course.objects.get(id=course_id)
    instructor = Instructor.objects.get(user=request.user)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.file = request.FILES['file']
        assignment.post_time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        assignment.course = course
        assignment.save()
        #increase total for course
        course.total +=1
        course.save()
        notification = Notification()
        notification.link = "http://127.0.0.1:8000/course/"+course_id+"/view_assignments/"
        notification.content = "New Assignment Uploaded |" + " Due at "+ str(assignment.deadline)[:-9]
        notification.course = course
        notification.time = timezone.now()
        notification.save()

        # email
        message = course_assignment_text(course.name,notification.link,assignment.deadline)
        subject ='Assignment added for ' + course.name
        recipient_list = get_student_emails(course_id)
        thread = threading.Thread(target=send_email,args=(subject, message, email_from, recipient_list, None,))
        thread.start()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/create_assignment.html', {'form': form, 'course': course})


## @brief view for the course's add-resource page.
#
# This view is called by <course_id>/add_resource url.\n
# It returns the webpage containing a form to add a resource and redirects to the course's detail page again after the form is submitted.
@login_required
def add_resource(request, course_id):
    form = ResourceForm(request.POST or None, request.FILES or None)
    instructor = Instructor.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.file_resource = request.FILES['file_resource']
        resource.course = course
        resource.post_time = timezone.now()
        resource.save()
        #increase total for course
        course.total +=1
        course.save()
        notification = Notification()
        notification.link = "http://127.0.0.1:8000/course/"+course_id+"/view_resources/"
        notification.content = "New Resource Added - " + resource.title
        notification.course = course
        notification.time = timezone.now()
        notification.save()

        # email
        message = course_resource_text(course.name,notification.link)
        subject = 'Resource added for ' + course.name
        recipient_list = get_student_emails(course_id)
        thread = threading.Thread(target=send_email,args=(subject, message, email_from, recipient_list, None,))
        thread.start()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/add_resource.html', {'form': form, 'course': course})


# view for the assignments page of a course.
# This view is called by <course_id>/view_all_assignments url.\n
# It returns the webpage containing all the assignments of the course and links to their submissions and feedbacks given by the students.
@login_required
def view_all_assignments(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    instructor = Instructor.objects.get(user=request.user)
    progress = ProgressInstructor.objects.get(instructor = instructor, course=course)
    return render(request, 'instructor/view_all_assignments.html', {'assignments' : assignments,'course': course, 'progress':progress})


# view for the submissions page of an assignment.
# This view is called by <assignment_id>/view_all_submissions url.\n
# It returns the webpage containing links to all the submissions of an assignment.
@login_required
def view_all_submissions(request,assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    course = assignment.course
    return render(request, 'instructor/view_all_submissions.html', {'submissions' : submissions,'course': course})

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
@login_required
def give_feedback(request, submission_id):
    form = FeedbackForm(request.POST or None, request.FILES or None)
    submission = Submission.objects.get(id=submission_id)
    course = submission.assignment.course
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.submission = submission
        feedback.save()
        # notification = Notification()
        # notification.content = "Feedback added - " + submission.assignment.description
        # notification.course = course
        # notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        # notification.save()
        return redirect('instructor:instructor_detail', course.id)

    return render(request, 'instructor/give_feedback.html', {'form': form,'course': course})

#view to disable discussion forum when needed by teacher
@login_required
def disable_forum(request, course_id=None):
    course_to_disable = Course.objects.get(id=course_id)
    course_to_disable.disabled_forum = True
    course_to_disable.save()
    return redirect('instructor_detail', course_id)

#view to enable discussion forum when needed by teacher
@login_required
def enable_forum(request, course_id=None):
    course_to_enable = Course.objects.get(id=course_id)
    course_to_enable.disabled_forum = False
    course_to_enable.save()
    return redirect('instructor_detail', course_id)

@login_required
def send_invite(request,course_id):
    form = SendInviteForm(request.POST or None)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        email_list = [s.strip() for s in form.cleaned_data.get('email_list').split(",")]
        message = course_invite_text(course.name,course.course_access_code)
        subject = 'Course invitation for course ' + course.name
        recipient_list = email_list
        thread = threading.Thread(target=send_email,args=(subject, message, email_from, recipient_list, None,))
        thread.start()
        return redirect('instructor:instructor_detail', course.id)
    return render(request, 'instructor/send_invite.html', {'course': course, 'form': form})

# invite TAs
def add_TA(request,course_id):
    form = AddTAForm(request.POST or None)
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        TA = TeachingAssistant.objects.filter(name=form.cleaned_data['username']).first()
        print(TA)
        enroll = TA_ship(TA=TA, course = course)
        enroll.can_add_students = form.cleaned_data.get('can_add_students')
        enroll.can_add_assignments  = form.cleaned_data.get('can_add_assignments')
        enroll.can_add_resources = form.cleaned_data.get('can_add_resources') 
        enroll.can_notify = form.cleaned_data.get('can_notify')
        enroll.save()
        email_list = [TA.user.email]
        print(email_list)
        message = TA_text(course.name)    
        subject = 'TAship for course ' + course.name
        recipient_list = email_list
        thread = threading.Thread(target=send_email,args=(subject, message, email_from, recipient_list, None,))
        thread.start()
        return redirect('instructor:instructor_detail', course.id)
    return render(request, 'instructor/add_TA.html', {'course': course, 'form': form})

#view to add grades using a csv file
@login_required
def add_grades(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    course = assignment.course
    if request.method == 'GET':
        form = StudentBulkUploadForm()
        return render(request, 'instructor/add_grades.html', {'form':form, 'course':course, 'name':assignment.name})

    # If not GET method then proceed
    try:
        form = StudentBulkUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']

            file_data = csv_file.read().decode('utf-8')
            lines = file_data.split('\n')

            # loop over the lines and save them in db. If error, store as string and then display
            for line in lines[:-1]:
                fields = line.split(',')
                student = Student.objects.get(name = str(fields[0]))
                submission = Submission.objects.get(user=student.user, assignment=assignment)
                marks = fields[1]
                content = str(fields[2])
                #add feedback
                feedback = Feedback()
                feedback.content = content
                feedback.submission = submission
                feedback.marks = marks
                feedback.save()
            
            notification = Notification()
            notification.link = "http://127.0.0.1:8000/course/"+course.id+"/view_feedback/"
            notification.content = "Feedback added - " + str(assignment.name)
            notification.course = course
            notification.time = timezone.now()
            notification.save()

            return redirect('view_all_assignments', course.id)

    except Exception as e:
        return redirect('add_grades', assignment_id)

@register.filter
def get(dictionary, key):
    return dictionary.get(key)

#view to view grading stats by teacher
@login_required
def view_grades(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    course = assignment.course
    students = Student.objects.filter(course_list__id=course.id)
    marks={}
    contents = {}
    try:
        for s in students:
            submission = Submission.objects.filter(assignment = assignment, user = s.user)[0]
            feedback = Feedback.objects.filter(submission=submission)[0]
            marks[s.id]=feedback.marks
            contents[s.id] = str(feedback.content)

        context = {
            'course':course,
            'assignment':assignment,
            'students':students,
            'marks':marks,
            'contents':contents,
        }
        return render(request, 'instructor/view_grades.html',context)
    except:
        return redirect('view_all_assignments',course.id)

# view for grading statistics
@login_required
def grading_statistics(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    course = assignment.course
    students = Student.objects.filter(course_list__id=course.id)
    marks_list =[]
    try:
        for s in students:
            submission = Submission.objects.filter(assignment = assignment, user = s.user)[0]
            feedback = Feedback.objects.filter(submission=submission)[0]
            marks_list.append(feedback.marks)

        # calculate stats
        average = (sum(marks_list) / len(marks_list))
        variance = sum((i - average) ** 2 for i in marks_list) / len(marks_list)
        variance = int(variance)
        average = int(average)
        # ----------plot the image here and save it-------
        # Creating histogram
        fig, axs = plt.subplots(1, 1,
                        figsize =(8, 4),
                        tight_layout = True)
        n_bins = [0,10,20,30,40,50,60,70,80,90,100]

        # Add padding between axes and labels
        axs.xaxis.set_tick_params(pad = 10)
        axs.yaxis.set_tick_params(pad = 10)
 
        # Add x, y gridlines
        axs.grid(b = True, color ='grey',
                linestyle ='-.', linewidth = 0.5,
                alpha = 0.6)
 
        # Creating histogram
        N, bins, patches = axs.hist(marks_list, bins = n_bins)
 
        # Setting color
        fracs = ((N**(1 / 5)) / N.max())
        norm = colors.Normalize(fracs.min(), fracs.max())
 
        for thisfrac, thispatch in zip(fracs, patches):
            color = plt.cm.viridis(norm(thisfrac))
            thispatch.set_facecolor(color)
 
        # Adding extra features   
        plt.xlabel("Marks")
        plt.ylabel("No Of Students")
        plt.title('Grading Statistics - '+str(assignment.name))
        plt.xticks = n_bins
 
        # Save plot
        plt.savefig('media/histogram.png')

        #Make ImageObject Instance
        i = ImageObject()
        with open('media/histogram.png','rb') as f:
            i.image.save('histogram.png', File(f))
        i.save()
        imgdata = StringIO()
        imgdata.truncate(0)
        imgdata.seek(0)
        plt.savefig(imgdata, format='svg')
        imgdata.seek(0)
        data = imgdata.getvalue()
        plt.clf()
        #------------plot saved-------------
        context = {
            'course':course,
            'assignment':assignment,
            'marks_list':marks_list,
            'average':average,
            'variance':variance,
            'i':i,
            'data': data,
        }
        return render(request, 'instructor/grading_statistics.html',context)
    except:
        return redirect('view_all_assignments',course.id)

#view to mark_as_done assignments
@login_required
def mark_as_done(request, course_id, id, done):
    course = Course.objects.get(id = course_id)
    instructor = Instructor.objects.get(user=request.user)
    progress = ProgressInstructor.objects.get(instructor = instructor, course=course)
    assignment = Assignment.objects.get(id=id)
    #if not done add assignment to assignments list of progress
    if int(done) == 0:
        progress.assignments.add(assignment)
    else:
        progress.assignments.remove(assignment)
    progress.save()
    return redirect('view_all_assignments', course_id)


# view for assignments statistics
@login_required
def all_assignment_stats(request, course_id):
    course = Course.objects.get(id = course_id)
    students = Student.objects.filter(course_list__id=course.id)
    assignments = Assignment.objects.filter(course = course)
    x_list = []
    mean_list=[]
    variance_list=[]
    x_list = []
    try:
        for a in assignments:
            x_list.append(a.name)
            marks_list=[]
            for s in students:
                try:
                    submission = Submission.objects.filter(assignment = a, user = s.user)[0]
                    feedback = Feedback.objects.filter(submission=submission)[0]
                    marks_list.append(feedback.marks)
                except:
                    True
            # calculate stats
            try:
                average = (sum(marks_list) / len(marks_list))
                variance = sum((i - average) ** 2 for i in marks_list) / len(marks_list)
                variance = int(variance)
                average = int(average)
                mean_list.append(average)
                variance_list.append(variance)
                x_list.append(a.name)
            except:
                True
        #plot graph
        plt.plot(x_list,mean_list)
        plt.plot(x_list,variance_list)
         
        plt.xlabel("Assignments")
        plt.ylabel("Mean and Variance")
        plt.title('Course Statistics - '+str(course.name))
        plt.plot([], c='#D7191C', label='Variances')
        plt.plot([], c='#2C7BB6', label='Means')
        plt.legend()
 
        # Save plot
        plt.savefig('media/graph.png')

        #Make ImageObject Instance
        i = ImageObject()
        with open('media/graph.png','rb') as f:
            i.image.save('graph.png', File(f))
        i.save()
        imgdata = StringIO()
        imgdata.truncate(0)
        imgdata.seek(0)
        plt.savefig(imgdata, format='svg')
        imgdata.seek(0)
        data = imgdata.getvalue()
        plt.clf()

        return render(request, 'instructor/all_assignment_stats.html',{'data':data,'course':course,'i':i})


    
    except:
        return redirect('view_all_assignments',course.id)
