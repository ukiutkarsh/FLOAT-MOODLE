## @brief urls for the instructor app.

from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

## @brief url patterns for the instructor app.
urlpatterns = [
    url(r'^instructor_index/$', views.instructor_index, name='instructor_index'),
    url(r'^(?P<course_id>[0-9]+)/instructor_detail/$', views.instructor_detail, name='instructor_detail'),
    url(r'^(?P<course_id>[0-9]+)/add_assignment/$', views.add_assignment, name='add_assignment'),
    url(r'^(?P<course_id>[0-9]+)/add_resource/$', views.add_resource, name='add_resource'),
    url(r'^(?P<course_id>[0-9]+)/add_notification/$', views.add_notification, name='add_notification'),
    url(r'^(?P<course_id>[0-9]+)/view_all_assignments/$', views.view_all_assignments, name='view_all_assignments'),
    url(r'^(?P<assignment_id>[0-9]+)/view_all_submissions/$', views.view_all_submissions, name='view_all_submissions'),
    url(r'^(?P<course_id>[0-9]+)/instructor_detail/disable_forum/$', views.disable_forum, name='disable_forum'),
    url(r'^(?P<course_id>[0-9]+)/all_assignment_stats/$', views.all_assignment_stats, name='all_assignment_stats'),
    url(r'^(?P<course_id>[0-9]+)/instructor_detail/enable_forum/$', views.enable_forum, name='enable_forum'),
    url(r'^(?P<course_id>[0-9]+)/instructor_detail/send_invite/$', views.send_invite, name='send_invite'),
    url(r'^(?P<course_id>[0-9]+)/instructor_detail/add_TA/$', views.add_TA, name='add_TA'),
    # url(r'^download/(?P<file_name>.+)$', views.download,name='download_submission'),
    url(r'^(?P<submission_id>[0-9]+)/give_feedback/$', views.give_feedback, name='give_feedback'),
    url(r'^(?P<assignment_id>[0-9]+)/add_grades/$', views.add_grades, name='add_grades'),
    url(r'^(?P<assignment_id>[0-9]+)/view_grades/$', views.view_grades, name='view_grades'),
    url(r'^(?P<course_id>[0-9]+)/(?P<id>[0-9]+)/(?P<done>\d)/mark_as_done/$', views.mark_as_done, name='mark_as_done'),
    url(r'^(?P<assignment_id>[0-9]+)/grading_statistics/$', views.grading_statistics, name='grading_statistics'),
    
    # url(r'^(?P<assignment_id>[0-9]+)/view_feedback/$', views.view_feedback, name='view_feedback'),
]

urlpatterns += staticfiles_urlpatterns()