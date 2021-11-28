## @brief urls for the instructor app.

from django.conf.urls import url, include
from django.contrib import admin
from . import views

## @brief url patterns for the instructor app.
urlpatterns = [
    url(r'^TA_index/$', views.TA_index, name='TA_index'),
    url(r'^(?P<course_id>[0-9]+)/TA_detail/$', views.TA_detail, name='TA_detail'),
    url(r'^(?P<course_id>[0-9]+)/TA_add_assignment/$', views.add_assignment, name='TA_add_assignment'),
    url(r'^(?P<course_id>[0-9]+)/TA_add_resource/$', views.TA_add_resource, name='TA_add_resource'),
    url(r'^(?P<course_id>[0-9]+)/add_notification/$', views.add_notification, name='TA_add_notification'),
    # url(r'^(?P<course_id>[0-9]+)/view_all_assignments/$', views.view_all_assignments, name='view_all_assignments'),
    # url(r'^(?P<assignment_id>[0-9]+)/view_all_submissions/$', views.view_all_submissions, name='view_all_submissions'),
    url(r'^(?P<course_id>[0-9]+)/TA_detail/send_invite/$', views.send_invite, name='TA_send_invite'),
    # url(r'^download/(?P<file_name>.+)$', views.download,name='download_submission'),
    # url(r'^(?P<submission_id>[0-9]+)/give_feedback/$', views.give_feedback, name='give_feedback'),
    # url(r'^(?P<assignment_id>[0-9]+)/add_grades/$', views.add_grades, name='add_grades')
    
    # url(r'^(?P<assignment_id>[0-9]+)/view_feedback/$', views.view_feedback, name='view_feedback'),
]

app_name = 'TA'
