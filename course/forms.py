from django import forms
from django.contrib.auth.models import User

from .models import Message, ChatMessage
from instructor.models import Submission


# This class represents the form to send a message in the forum.
class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ['content']


# This class represents the form to add a submission for an assignment.
class SubmissionForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ['file_submitted']

class ChatMessageForm(forms.ModelForm):
    
    class Meta:
        model = ChatMessage
        fields = ['receiver', 'msg_content']

class JoinCourseForm(forms.Form):
    course_access_code = forms.CharField(max_length=100)