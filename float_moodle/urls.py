## @brief urls for the website.
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views #import this
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

## @brief url patterns for the website.
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # path('', include('django.contrib.auth.urls')),  
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),  
    url(r'^login/', views.login_user, name='login_user'),
    url(r'^divide/', views.divide, name='divide'),
    url(r'^register_user/$', views.register_user, name='register_user'),
    url(r'^register_instructor/$', views.register_instructor, name='register_instructor'),
    url(r'^register_TA/$', views.register_TA, name='register_TA'),
    url(r'^logout/$', views.logout_user, name='logout_user'),
    url(r'^course/', include(('course.urls', 'course'), namespace='course')),
    url(r'^instructor/', include(('instructor.urls', 'instructor'), namespace='instructor')),
    url(r'^create_course/$', views.add_course, name='create_course'),
    path('',include('course.urls')),
    path('',include('instructor.urls')), 
    path('',include('TA.urls')),

]
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)