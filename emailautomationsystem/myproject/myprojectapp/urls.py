# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_student, name='register_student'),
    path('list/', views.student_list, name='student_list'),  # Correct root path
    path('send-emails/', views.send_emails, name='send_emails'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('', views.index, name='index'),  # Ensure this path is included
    path('email-sent/', views.email_sent, name='email_sent'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
]
