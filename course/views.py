from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from .models import Progress, Student, Message, Notification, Resources, ChatMessage
from .models import Student, Message, Notification, Resources, ChatMessage,Membership
from instructor.models import Assignment, Course, Feedback, Instructor,Submission
from django.shortcuts import render, redirect
from .forms import MessageForm, SubmissionForm, ChatMessageForm,JoinCourseForm
import datetime
import threading
from django.utils import timezone
from django.template.defaulttags import register
from TA.models import TeachingAssistant
from instructor.functions import send_email

email_from = "shah.adish13@gmail.com"
#register custom filter for looking up from dictionary
@register.filter
def get_progress(dictionary, key):
    return dictionary.get(key)

## @brief view for the index page of the student.
#
# This view is called by /index url.\n
# It returns the student's homepage containing links to all the courses he is enrolled in and all the notifications.
@login_required
def index(request):
    student = Student.objects.get(user = request.user)
    courses = student.course_list.all()
    progress_list={}
    for c in courses:
        progress = Progress.objects.get(student = student, course = c)
        assignments = Assignment.objects.filter(course=c)
        for a in assignments:
            #close the assignment if over due and add a notification
            if not a.closed:
                if timezone.now()>= a.deadline:
                    a.closed = True
                    a.save()
                    newnotif = Notification()
                    newnotif.course=c
                    newnotif.time= a.deadline
                    newnotif.content = str(a.name) + " Assignment over-due"
                    newnotif.save()
        p = 0
        if(c.total>0):
            p = int(progress.done/c.total*100)
        progress_list[c.id]=str(p)+"%"

    notifications = Notification.objects.filter(course__in = courses)
    return render(request, 'course/index.html', {'courses': courses, 'notifications': notifications,'progress_list': progress_list})


# view for the detail page of the course.
# This view is called by <course_id>/detail url.\n
# It returns the course's detail page containing forum and links to all the assignments and resources.
@login_required
def detail(request, course_id):
    user = request.user
    student = Student.objects.get(user=request.user)
    courses = student.course_list.all()
    course = Course.objects.get(id=course_id)
    instructor = course.instructor
    messages = Message.objects.filter(course=course)
    form = MessageForm(request.POST or None)
    disabled_forum = course.disabled_forum
    #find all assignments to be completed in the course
    progress = Progress.objects.get(student = student, course = course)
    assignments = Assignment.objects.filter(course = course, closed = False)
    resources = Resources.objects.filter(course = course)
    finished_assignments = progress.assignments
    finished_resources = progress.resources

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
                return redirect('instructor:instructor_detail', course.id)

    else:
        form = MessageForm()

        context = {
            'course': course,
            'user': user,
            'instructor': instructor,
            'student': student,
            'courses': courses,
            'messages': messages,
            'form': form,
            'disabled_forum':disabled_forum,
            'assignments': assignments,
            'resources': resources,
            'finished_assignments': finished_assignments,
            'finished_resources': finished_resources,
        }

        return render(request, 'course/detail.html', context)


# view for the assignments page of a course.
# This view is called by <course_id>/view_assignments url.\n
# It returns the webpage containing all the assignments of the course and links to download them and upload submissions.
@login_required
def view_assignments(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    student = Student.objects.get(user = request.user)
    progress = Progress.objects.get(course = course, student =student)
    context = {
        'course' : course,
        'assignments' : assignments,
        'progress':progress,
    }
    return render(request,'course/view_assignments.html',context)


# view for the resources page of a course.
# This view is called by <course_id>/view_resources url.\n
# It returns the webpage containing all the resources of the course and links to download them.
@login_required
def view_resources(request, course_id):
    course = Course.objects.get(id=course_id)
    resources = Resources.objects.filter(course=course)
    student = Student.objects.get(user = request.user)
    progress = Progress.objects.get(course = course, student =student)
    context = {
        'course' : course,
        'resources' : resources,
        'progress':progress,
    }
    return render(request,'course/view_resources.html',context)


# view for the assignment's submission page.
# This view is called by <assignment_id>/upload_submission url.\n
# It returns the webpage containing a form to upload submission and redirects to the assignments page again after the form is submitted.
@login_required
def upload_submission(request, assignment_id):
    form = SubmissionForm(request.POST or None, request.FILES or None)
    assignment = Assignment.objects.get(id=assignment_id)
    course_id = assignment.course.id
    course = Course.objects.get(id=course_id)
    if form.is_valid():
        submission = form.save(commit=False)
        submission.user = request.user
        submission.assignment = assignment
        submission.time_submitted = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        submission.save()

        # link = 
        # email
        message = "You have submitted your assignment for " + assignment.name + "of the course" + course.code
        subject = 'Assignment submitted' + assignment.name
        recipient_list = [request.user.email]
        thread = threading.Thread(target=send_email,args=(subject, message,email_from, recipient_list, None,))
        thread.start()
        return view_assignments(request, course_id)

    return render(request, 'course/upload_submission.html', {'form': form,'course': course})

@login_required
def view_submissions(request,assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(user=request.user, assignment = assignment)
    course = assignment.course
    return render(request, 'course/view_submissions.html', {'submissions' : submissions,'course': course, 'name':assignment.name})

@login_required
def view_feedback(request,submission_id):
    feedback = Feedback.objects.filter(submission=submission_id)
    submission = Submission.objects.get(id=submission_id)
    course = submission.assignment.course
    # content = feedback.content
    # marks = feedback.marks
    return render(request, 'course/view_feedback.html', {'feedback': feedback,'course': course})

#these views enable messaging between students and also teachers
#Deleting sent messages is also implemented
@login_required
def send_message(request):
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.published_at = timezone.now()
            message.save()
            return redirect('view_messages')

    else:
        form = ChatMessageForm()
    try:
        student = Student.objects.get(user=request.user)
        return render(request,'course/chat.html',{'form':form})
    except:
        try:
            ta = TeachingAssistant.objects.get(user=request.user)
            return render(request,'TA/chat.html',{'form':form})
        except:
            return render(request, 'instructor/chat.html',{'form':form})

@login_required
def view_messages(request):
    inbox_messages = ChatMessage.objects.filter(receiver=request.user).order_by('published_at').reverse()[:20]
    sent_messages = ChatMessage.objects.filter(sender=request.user).order_by('published_at').reverse()[:20]
    try:
        student = Student.objects.get(user=request.user)
        return render(request, 'course/inbox.html', {'inbox_messages': inbox_messages, 'sent_messages':sent_messages})
    except:
        try:
            ta = TeachingAssistant.objects.get(user=request.user)
            return render(request,'TA/inbox.html', {'inbox_messages': inbox_messages, 'sent_messages':sent_messages})
        except:
            return render(request, 'instructor/inbox.html', {'inbox_messages': inbox_messages, 'sent_messages':sent_messages})

@login_required
def dashboard(request):
    user = request.user 
    return render(request,'course/dashboard.html',{'user':user})

@login_required
def delete_message(request,message_id=None):
    message_to_delete=ChatMessage.objects.get(id=message_id)
    message_to_delete.delete()
    return redirect('view_messages')

#view to mark_as_done assignments and resources
@login_required
def mark_as_done(request, course_id, is_it_res, id, done):
    course = Course.objects.get(id = course_id)
    student = Student.objects.get(user=request.user)
    progress = Progress.objects.get(student=student, course=course)
    if(int(is_it_res) == 1):
        resource = Resources.objects.get(id=id)
        #if not done add resource to resources list of progress
        if int(done)==0:
            progress.done +=1
            progress.resources.add(resource)
        else:
            progress.done -=1
            progress.resources.remove(resource)
        progress.save()
        return redirect('view_resources', course_id)
    else:
        assignment = Assignment.objects.get(id=id)
        #if not done add assignment to assignments list of progress
        if int(done) == 0:
            progress.done +=1
            progress.assignments.add(assignment)
        else:
            progress.done -=1
            progress.assignments.remove(assignment)
        progress.save()
        return redirect('view_assignments', course_id)

@login_required
def join_course(request):
    if request.method == 'POST':
        form = JoinCourseForm(request.POST)
        if form.is_valid():
            student = Student.objects.get(user = request.user)
            if Course.objects.filter(course_access_code = form.cleaned_data.get('course_access_code')):
                course = Course.objects.filter(course_access_code = form.cleaned_data.get('course_access_code')).first()
                enroll = Membership(student=student , course = course)
                enroll.save()
                progress=Progress()
                progress.student=student
                progress.course = course
                progress.save()  
                print('Added to course successfully')
            else:
                print('No course exists with access code: ', form.cleaned_data.get('access_code'))
        return redirect('dashboard', permanent = True)
    else:
        form = JoinCourseForm()
        return render(request , 'course/join_course.html',{'form': form})

#dashboard
@login_required
def dashboard(request):
    user = request.user 
    student = Student.objects.get(user=request.user)
    courses = student.course_list.all()
    return render(request,'course/dashboard.html',{'user':user, 'student':student, 'courses':courses})


#register custom filter for looking up marks from dictionary
@register.filter
def get_marks(dictionary, key):
    return dictionary.get(key)
@register.filter
def get_total(dictionary, key):
    return dictionary.get(key)

#view grades using this view
def view_grades(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    marks_list = {}
    total_list = {}
    contents = {}
    total_marks = 0
    course_total =0
    students = Student.objects.filter(course_list__id = course_id)
    try:
        for a in assignments:
            try:
                submission = Submission.objects.get(user = request.user, assignment =a)
                feedback = Feedback.objects.filter(submission = submission)[0]
                marks_list[a.id] = float(feedback.marks)
                total_list[a.id] = float(feedback.marks*float(a.weightage)/100)
                total_marks += total_list[a.id]
                course_total += marks_list[a.id]
                contents[a.id] = str(feedback.content)
            except:
                True

        total_marks_list=[]
        try:
            for s in students:
                ag=0
                for a in assignments:
                    try:
                        submission = Submission.objects.get(user = s.user, assignment =a)
                        feedback = Feedback.objects.filter(submission = submission)[0]
                        ag+=float(feedback.marks*(a.weightage)/100)
                    except:
                        True
                total_marks_list.append(ag)
        except:
            True
        average = sum(total_marks_list)/len(total_marks_list)
        lagging_behind = False
        if total_marks<average:
            lagging_behind = True
        context = {
            'course' : course,
            'assignments' : assignments,
            'marks_list' : marks_list,
            'total_list': total_list,
            'total_marks':total_marks,
            'course_total':course_total,
            'contents':contents,
            'average':average,
            'lagging_behind':lagging_behind,
        }
        return render(request,'course/view_grades.html',context)
    except:
        return redirect('course:detail', course_id)

def view_progress(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    marks_list = {}
    total_list = {}
    total_marks = 0
    try:
        for a in assignments:
            submission = Submission.objects.get(user = request.user, assignment =a)
            feedback = Feedback.objects.filter(submission = submission)[0]
            marks_list[a.id] = int(feedback.marks)
            total_list[a.id] = int(feedback.marks*int(a.weightage)/100)
            total_marks += total_list[a.id]
        context = {
            'course' : course,
            'assignments' : assignments,
            'marks_list' : marks_list,
            'total_list': total_list,
            'total_marks':total_marks
        }
        return render(request,'course/view_grades.html',context)
    except:
        return redirect('course:detail', course_id)
