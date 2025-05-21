import pandas as pd
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import Student
from .forms import StudentForm
import os
import logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
# views.py
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('index')  # Redirect to the index page or any other page
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
@login_required
def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'register_student.html', {'form': form})

@login_required
def student_list(request):
    students = Student.objects.all()
    if request.method == 'POST':
        if 'delete_selected' in request.POST:
            selected_students = request.POST.getlist('selected_students')
            Student.objects.filter(id__in=selected_students).delete()
            messages.success(request, 'Selected students have been deleted successfully.')
        elif 'delete_all' in request.POST:
            Student.objects.all().delete()
            messages.success(request, 'All students have been deleted successfully.')
        return redirect('student_list')
    return render(request, 'student_list.html', {'students': students})

logger = logging.getLogger(__name__)

@user_passes_test(lambda u: u.is_superuser)
@login_required
def send_emails(request):
    if request.method == 'POST':
        logger.debug('POST request received.')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        selected_students = request.POST.getlist('students')
        attached_files = request.FILES.getlist('attached_files')

        if 'all' in selected_students:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(id__in=selected_students)

        file_paths = []
        for attached_file in attached_files:
            fs = FileSystemStorage()
            filename = fs.save(attached_file.name, attached_file)
            file_paths.append(fs.path(filename))
            logger.debug(f'Uploaded file path: {fs.path(filename)}')

        for student in students:
            email = EmailMessage(
                subject,
                f'Hello {student.name},\n\n{message}',
                settings.EMAIL_HOST_USER,
                [student.email]
            )
            for file_path in file_paths:
                email.attach_file(file_path)
            email.send(fail_silently=False)
            logger.debug(f'Email sent to {student.email}')

        # Clean up uploaded files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f'Removed file: {file_path}')

        # Add a success message
        messages.success(request, 'Emails have been sent successfully.')
        logger.debug('Emails sent successfully, redirecting to email_sent.')
        return redirect('email_sent')

    students = Student.objects.all()
    return render(request, 'send_emails.html', {'students': students})

@login_required
def upload_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)

        # Read the Excel file
        df = pd.read_excel(file_path)

        # Process each row in the DataFrame
        for _, row in df.iterrows():
            student = Student(
                name=row['name'],
                email=row['email']
            )
            student.save()

        return redirect('student_list')
    return render(request, 'upload_excel.html')

@login_required
def index(request):
    return render(request, 'base_generic.html')

@login_required
def email_sent(request):
    return render(request, 'email_sent.html')

def logout(request):
    return render(request, 'loged_out.html')