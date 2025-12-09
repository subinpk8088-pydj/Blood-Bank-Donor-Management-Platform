from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
def home(request):
    """Landing page view"""
    return render(request, 'home.html')



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')

            # Assuming CustomUser model with role field
            if hasattr(user, 'role'):
                if user.role == 'doctor':
                    return redirect('dashboard')
                elif user.role == 'donor':
                    return redirect('dashboard')
                elif user.role == 'patient':
                    return redirect('dashboard')
            
            # fallback if role is undefined
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login_view')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')



def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')



import random, string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from .models import CustomUser

User = get_user_model()

def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Admin check for pending approvals and approval actions
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def pending_approvals(request):
    pending_users = CustomUser.objects.filter(is_approved=False, role__in=['doctor', 'donor'])
    return render(request, 'admin/pending_approvals.html', {'pending_users': pending_users})

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import datetime

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Generate new password
    new_password = generate_password()
    user.set_password(new_password)
    user.is_active = True
    user.is_approved = True
    user.save()

    # Create styled HTML content for email
    subject = '🎉 Your Blood Center Account Has Been Approved!'
    from_email = 'yourhospital@example.com'
    to_email = user.email

    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
                color: #333;
            }}
            .email-container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
                max-width: 600px;
                margin: auto;
            }}
            .header {{
                text-align: center;
                color: #dc3545;
            }}
            .credentials {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
                font-family: monospace;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #dc3545;
                color: #ffffff;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #999;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h2>🎉 Welcome to Blood Center</h2>
                <p>Your account has been approved!</p>
            </div>
            <p>Hi {user.first_name},</p>
            <p>We’re happy to let you know your account has been approved. Here are your login details:</p>

            <div class="credentials">
                <strong>Username:</strong> {user.username}<br>
                <strong>Password:</strong> {new_password}
            </div>

            <p>Click below to log in and get started:</p>
            <p><a class="btn" href="http://yourdomain.com/login">Login to Your Account</a></p>

            <p>If you have any questions, feel free to reach out to us.</p>

            <div class="footer">
                &copy; {datetime.datetime.now().year} Blood Center. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    # Send email
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()

    messages.success(request, f'{user.username} has been approved successfully and credentials have been emailed.')
    return redirect('pending_approvals')


from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import datetime
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def signup_view(request):
    if request.method == 'POST':
        role = request.POST['role']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        profile_image = request.FILES.get('profile_image')
        
        # Get blood group if donor role was selected
        blood_group = None
        if role == 'donor':
            blood_group = request.POST['blood_group']
        
        password = generate_password()
        
        is_approved = False if role in ['doctor', 'donor'] else True
        is_active = is_approved
        
        # Create user object but don't save yet
        user = CustomUser(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            address=address,
            phone=phone,
            profile_image=profile_image,
            is_active=is_active,
            is_approved=is_approved
        )
        
        # Add blood group for donors
        if role == 'donor' and blood_group:
            user.blood_group = blood_group
        
        # Generate patient ID for patients only
        if role == 'patient':
            # Generate a unique patient ID (format: P-yyyymmdd-XXXX)
            today = datetime.datetime.now().strftime('%Y%m%d')
            random_suffix = ''.join(random.choices('0123456789', k=4))
            patient_id = f"P-{today}-{random_suffix}"
            
            # Check if this ID already exists and regenerate if necessary
            while CustomUser.objects.filter(patient_id=patient_id).exists():
                random_suffix = ''.join(random.choices('0123456789', k=4))
                patient_id = f"P-{today}-{random_suffix}"
            
            user.patient_id = patient_id
        
        # Set password and save
        user.set_password(password)
        user.save()
        
        if role == 'patient':
            # Styled HTML Email with patient ID included
            html_content = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                    <h2 style="color: #e63946;">Welcome to Blood Center, {first_name}!</h2>
                    <p>Your account has been successfully created. Below are your login credentials:</p>
                    <div style="margin: 20px 0; padding: 15px; background-color: #f1f1f1; border-left: 5px solid #e63946;">
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Password:</strong> {password}</p>
                        <p><strong>Patient ID:</strong> {patient_id}</p>
                    </div>
                    <p>For your security, please change your password after logging in.</p>
                    <br>
                    <p>Best regards,<br><strong>Blood Center Team</strong></p>
                    <hr style="margin-top: 40px;">
                    <p style="font-size: 12px; color: #888;">&copy; {datetime.datetime.now().year} Blood Center. All rights reserved.</p>
                </div>
            """
            text_content = strip_tags(html_content)
            
            email_message = EmailMultiAlternatives(
                subject='Welcome to Blood Center',
                body=text_content,
                from_email='yourhospital@example.com',
                to=[email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
            
            messages.success(request, 'Account created and credentials sent to your email.')
        elif role == 'donor':
            # Styled HTML Email for donor
            html_content = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                    <h2 style="color: #e63946;">Thank you for registering as a donor, {first_name}!</h2>
                    <p>Your account request has been submitted for approval. Below are your login credentials:</p>
                    <div style="margin: 20px 0; padding: 15px; background-color: #f1f1f1; border-left: 5px solid #e63946;">
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Password:</strong> {password}</p>
                        <p><strong>Blood Group:</strong> {blood_group}</p>
                    </div>
                    <p>You will receive an email once your account has been approved.</p>
                    <br>
                    <p>Best regards,<br><strong>Blood Center Team</strong></p>
                    <hr style="margin-top: 40px;">
                    <p style="font-size: 12px; color: #888;">&copy; {datetime.datetime.now().year} Blood Center. All rights reserved.</p>
                </div>
            """
            text_content = strip_tags(html_content)
            
            email_message = EmailMultiAlternatives(
                subject='Blood Center - Donor Registration',
                body=text_content,
                from_email='yourhospital@example.com',
                to=[email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
            
            messages.info(request, 'Your account request has been sent for admin approval.')
        else:
            messages.info(request, 'Your account request has been sent for admin approval.')
        
        return redirect('login_view')
    
    return render(request, 'signup.html')


from django.http import JsonResponse
from .models import CustomUser

def validate_username(request):
    username = request.GET.get("value", "")
    exists = CustomUser.objects.filter(username__iexact=username).exists()
    message = "This username is already taken." if exists else ""
    return JsonResponse({"exists": exists, "message": message})

from django.http import JsonResponse
from .models import CustomUser

def validate_email(request):
    email = request.GET.get("value", "").strip()
    
    # Check if email ends with '.com'
    if not email.lower().endswith(".com"):
        return JsonResponse({
            "exists": True, 
            "message": "Email must end with .com extension."
        })
    
    exists = CustomUser.objects.filter(email__iexact=email).exists()
    message = "This email is already registered." if exists else ""
    
    return JsonResponse({"exists": exists, "message": message})

from django.http import JsonResponse
from .models import CustomUser

def validate_phone(request):
    phone = request.GET.get("value", "").strip()

    # Check if it's exactly 10 digits
    if not phone.isdigit() or len(phone) != 10:
        return JsonResponse({
            "exists": True,
            "message": "Phone number must be exactly 10 digits."
        })

    exists = CustomUser.objects.filter(phone=phone).exists()
    message = "This phone number is already registered." if exists else ""

    return JsonResponse({"exists": exists, "message": message})





from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')









from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import CustomUser


def admin_patient_list(request):
    # Get all patients
    patients_list = CustomUser.objects.filter(role='patient').order_by('-date_joined')
    
    # Apply search filters
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    if search_query:
        patients_list = patients_list.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(patient_id__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(phone__icontains=search_query) |
            Q(username__icontains=search_query)
        )
        
    if status:
        is_active = True if status == 'active' else False
        patients_list = patients_list.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(patients_list, 10)
    page = request.GET.get('page', 1)
    patients = paginator.get_page(page)
    
    context = {
        'patients': patients,
    }
    
    return render(request, 'admin/admin_patient_list.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def is_admin(user):
    return user.is_superuser or user.is_staff  # Adjust based on your admin logic

@login_required
@user_passes_test(is_admin)
def delete_patient(request, patient_id):
    patient = get_object_or_404(CustomUser, id=patient_id, role='patient')
    
    if request.method == 'POST':
        patient.delete()
        messages.success(request, f"Patient {patient.get_full_name()} has been deleted.")
        return redirect('admin_patient_list')  # Redirect back to the patient list page
    
    return HttpResponseForbidden("Invalid request method.")


from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect, render
import re


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if old password is correct
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')  # Stay on the same page
        
        elif new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('change_password')  # Stay on the same page
        
        else:
            # Password validation
            errors = []
            
            if len(new_password) < 8:
                errors.append('Password must be at least 8 characters long.')
            
            if not re.search(r'[A-Z]', new_password):
                errors.append('Password must contain at least one uppercase letter.')
                
            if not re.search(r'[a-z]', new_password):
                errors.append('Password must contain at least one lowercase letter.')
                
            if not re.search(r'[0-9]', new_password):
                errors.append('Password must contain at least one number.')
                
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                errors.append('Password must contain at least one special character.')
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('change_password')  # Stay on the same page
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Your password was successfully updated. Please login again.')
                return redirect('login_view')  # Redirect to login page after successful password change
    
    return render(request, 'change_password.html')

from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CustomUser

def doctor_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    doctors = CustomUser.objects.filter(role='doctor')  # Fixed field name

    if search_query:
        doctors = doctors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if status_filter:
        if status_filter == 'active':
            doctors = doctors.filter(is_active=True)
        elif status_filter == 'inactive':
            doctors = doctors.filter(is_active=False)

    paginator = Paginator(doctors, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/doctor_list.html', {
        'doctors': page_obj,
    })
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def is_admin(user):
    return user.is_superuser or user.is_staff  # Adjust based on your admin logic

@login_required
@user_passes_test(is_admin)
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id)

    if doctor.is_staff:  # Optional: prevent deleting admin/staff accidentally
        messages.warning(request, "Cannot delete an admin/staff user.")
        return redirect('doctor_list')

    doctor.delete()
    messages.success(request, "Doctor deleted successfully.")
    return redirect('doctor_list')  # Use the actual name of your doctor list URL

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CustomUser
from django.core.paginator import Paginator

def donor_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    blood_group_filter = request.GET.get('blood_group', '')
    
    # Start with all donors
    donors = CustomUser.objects.filter(role='donor')
    
    # Apply filters
    if search_query:
        donors = donors.filter(
            first_name__icontains=search_query
        ) | donors.filter(
            last_name__icontains=search_query
        ) | donors.filter(
            username__icontains=search_query
        ) | donors.filter(
            email__icontains=search_query
        ) | donors.filter(
            phone__icontains=search_query
        )
    
    if status_filter:
        is_active = True if status_filter == 'active' else False
        donors = donors.filter(is_active=is_active)
    
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)
    
    # Get all unique blood groups for filter dropdown
    all_blood_groups = CustomUser.objects.filter(
        role='donor',
        blood_group__isnull=False
    ).values_list('blood_group', flat=True).distinct().order_by('blood_group')
    
    # Paginate results
    paginator = Paginator(donors, 10)  # Show 10 donors per page
    page = request.GET.get('page')
    donors_paginated = paginator.get_page(page)
    
    context = {
        'donors': donors_paginated,
        'all_blood_groups': all_blood_groups,
        'search_query': search_query,
        'status_filter': status_filter,
        'blood_group_filter': blood_group_filter,
    }
    
    return render(request, 'admin/donor_list.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import CustomUser  # Adjust the import based on your project structure

User = get_user_model()

def is_admin(user):
    return user.is_superuser or user.is_staff  # Adjust based on your admin logic

@login_required
@user_passes_test(is_admin)
def delete_donor(request, pk):
    donor = get_object_or_404(CustomUser, pk=pk)
    donor.delete()
    messages.success(request, "Donor deleted successfully.")
    return redirect('donor_list')  # Replace with your actual list view name


@login_required
def request_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST['doctor']
        date = request.POST['date']
        time = request.POST['time']
        reason = request.POST['reason']
        
        # Removed doctor limit check - doctors can have unlimited appointments per day
        
        # Check if patient already has 5 appointments with the same doctor on the same date
        existing_with_doctor_same_date = Appointment.objects.filter(
            patient=request.user,
            doctor_id=doctor_id,
            appointment_date=date
        ).count()
        
        if existing_with_doctor_same_date >= 5:
            messages.error(request, "You already have 5 appointments with this doctor on this date. Please choose another date or doctor.")
            return redirect('appointment_request')
        
        # Check if patient already has an appointment at the same time with the same doctor
        existing_same_time_same_doctor = Appointment.objects.filter(
            patient=request.user,
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time
        ).exists()
        
        if existing_same_time_same_doctor:
            messages.error(request, "You already have an appointment with this doctor at this time. Please choose a different time.")
            return redirect('appointment_request')
        
        # All checks passed — create the appointment
        Appointment.objects.create(
            patient=request.user,
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time,
            reason=reason,
            status='Pending'
        )
        messages.success(request, "Your appointment request has been submitted.")
        return redirect('appointment_request')
    
    doctors = CustomUser.objects.filter(role='doctor')
    return render(request, 'dashboard/appointment_request.html', {'doctors': doctors})
@login_required
def view_appointments(request):
    if request.user.role != 'doctor':
        # messages.error(request, "Access denied.")
        return redirect('home')

    appointments = Appointment.objects.filter(doctor=request.user).order_by('-appointment_date', '-appointment_time')
    return render(request, 'dashboard/doctor_appointments.html', {'appointments': appointments})


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Appointment

@login_required
def consult_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user.role != 'doctor':
        return redirect('home')  # No message added here, so nothing flashes

    if request.method == 'POST':
        consult_reason = request.POST.get('consult_reason')
        appointment.doctor_findings = consult_reason
        appointment.status = 'Consulted'
        appointment.save()

        messages.success(request, "Consultation recorded successfully.")
        return redirect('view_appointments')  # Only this page gets the success message


# views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Appointment
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef

User = get_user_model()

@login_required
def view_all_appointments(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('home')  # Make sure 'home' URL exists
    
    # Get query parameters
    doctor_id = request.GET.get('doctor_id')
    
    # Get only doctors who have appointments
    doctors_with_appointments = User.objects.filter(
        Exists(Appointment.objects.filter(doctor=OuterRef('pk')))
    ).order_by('first_name', 'last_name')
    
    # Filter appointments based on doctor if specified
    if doctor_id:
        appointments = Appointment.objects.filter(doctor_id=doctor_id).order_by('-appointment_date', '-appointment_time')
    else:
        appointments = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments,
        'doctors': doctors_with_appointments,
        'selected_doctor_id': doctor_id,
    }
    
    return render(request, 'admin/view_all_appointments.html', context)












from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CustomUser

def doctor_patient_list(request):
    patients = CustomUser.objects.filter(role='patient').order_by('-date_joined')

    search = request.GET.get('search', '')
    if search:
        patients = patients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    paginator = Paginator(patients, 10)
    page = request.GET.get('page')
    patients = paginator.get_page(page)

    return render(request, 'dashboard/doctor_patient_list.html', {'patients': patients})





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import CustomUser
from django.core.paginator import Paginator

@login_required
def donor_list_view_for_doctor(request):
    search_query = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')

    donors = CustomUser.objects.filter(role='donor')

    if search_query:
        donors = donors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    donors = donors.order_by('-date_joined')
    paginator = Paginator(donors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_blood_groups = CustomUser.objects \
        .filter(role='donor') \
        .exclude(blood_group__isnull=True) \
        .exclude(blood_group='') \
        .values_list('blood_group', flat=True) \
        .distinct()

    return render(request, 'dashboard/doctor_donor_list.html', {
        'donors': page_obj,
        'all_blood_groups': all_blood_groups,
    })



# utils.py or inside views.py (top of the file if keeping it simple)
def get_filtered_donors(request):
    search_query = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')

    donors = CustomUser.objects.filter(role='donor')

    if search_query:
        donors = donors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    donors = donors.order_by('-date_joined')
    return donors

# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DonorForm
from .models import CustomUser
from django.core.paginator import Paginator
from django.db.models import Q
import uuid
import random
import string

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import uuid, random, string
from .forms import DonorForm
from .models import CustomUser


@login_required
def patient_blood(request):
    """View for patients to add new donors to the system"""
    if request.method == 'POST':
        form = DonorForm(request.POST)
        
        if form.is_valid():
            try:
                donor = form.save(commit=False)
                donor.role = 'donor'
                username = donor.email.split('@')[0]
                
                if CustomUser.objects.filter(username=username).exists():
                    username = f"{username}{random.randint(100,999)}"
                donor.username = username

                random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                donor.set_password(random_password)

                if not donor.patient_id:
                    donor.patient_id = str(uuid.uuid4())[:8].upper()

                donor.save()

                messages.success(request, f'Donor {donor.first_name} {donor.last_name} has been added successfully.')
                return redirect('patient_blood')
            except Exception as e:
                print(f"Error saving donor: {str(e)}")
                messages.error(request, f'Error saving donor: {str(e)}')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f'Form validation errors: {form.errors}')
    else:
        form = DonorForm()
    
    return render(request, 'dashboard/patient_blood.html', {'form': form})


def validate_email(request):
    email = request.GET.get('email')
    exists = CustomUser.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})


def validate_phone(request):
    phone = request.GET.get('phone')
    exists = CustomUser.objects.filter(phone=phone).exists()
    return JsonResponse({'exists': exists})


def validate_firstname(request):
    first_name = request.GET.get('first_name')
    exists = CustomUser.objects.filter(first_name__iexact=first_name).exists()
    return JsonResponse({'exists': exists})

@login_required
def donor_list_view_for_patient(request):
    """View for patients to see the list of donors"""
    search_query = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')

    donors = CustomUser.objects.filter(role='donor')

    if search_query:
        donors = donors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    donors = donors.order_by('-date_joined')
    paginator = Paginator(donors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Exclude None values from blood group list
    all_blood_groups = CustomUser.objects \
        .filter(role='donor') \
        .exclude(blood_group__isnull=True) \
        .exclude(blood_group='') \
        .values_list('blood_group', flat=True) \
        .distinct()

    return render(request, 'dashboard/patient_donor_list.html', {
        'donors': page_obj,
        'all_blood_groups': all_blood_groups,
    })
    
    
    
    



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BloodRequest

@login_required
def blood_request_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        blood_group = request.POST.get('blood_group')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')

        if not (full_name and blood_group and quantity and reason):
            messages.error(request, "All fields are required.")
        else:
            try:
                quantity = int(quantity)
                blood_request = BloodRequest.objects.create(
                    patient=request.user,
                    full_name=full_name,
                    blood_group=blood_group,
                    quantity=quantity,
                    reason=reason
                )
                messages.success(request, "Blood request submitted successfully.")
                return redirect('blood_request')
            except ValueError:
                messages.error(request, "Quantity must be a number.")

    return render(request, 'dashboard/blood_request_form.html')
    
    
    
    
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import BloodRequest
from app.models import CustomUser  # adjust if your app name is different


@login_required
@login_required
def request_blood(request):
    if request.method == "POST":
        blood_group = request.POST.get('blood_group')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')

        if not (blood_group and quantity and reason):
            messages.error(request, "All fields are required.")
        else:
            BloodRequest.objects.create(
                patient=request.user,
                full_name=request.user.get_full_name(),  # Automatically set from logged-in user
                blood_group=blood_group,
                quantity=quantity,
                reason=reason
            )
            messages.success(request, "Your blood request has been submitted.")
            return redirect('request_blood')

    blood_groups = CustomUser.BLOOD_GROUP_CHOICES
    return render(request, "dashboard/request_blood.html", {"blood_groups": blood_groups})


def is_admin(user):
    return user.is_superuser  # Customize as needed


@login_required
@user_passes_test(is_admin)
def view_blood_requests(request):
    requests = BloodRequest.objects.filter(is_processed=False).order_by('-created_at')
    
    # Get blood group filter parameter
    blood_group_filter = request.GET.get('blood_group', '')
    
    # Apply blood group filter if provided
    if blood_group_filter:
        requests = requests.filter(blood_group=blood_group_filter)
    
    # Get all donors
    donors = CustomUser.objects.filter(role='donor')
    
    # Get unique blood groups for filter dropdown
    blood_groups = BloodRequest.objects.values_list('blood_group', flat=True).distinct()
    
    return render(request, 'admin/view_blood_requests.html', {
        'requests': requests, 
        'donors': donors,
        'blood_groups': blood_groups,
        'current_filter': blood_group_filter
    })
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import BloodRequest, CustomUser

@login_required
def send_blood_request_emails(request):
    if request.method == 'POST':
        blood_requests = BloodRequest.objects.filter(is_processed=False)
        donors = CustomUser.objects.filter(role='donor', is_active=True, is_approved=True)

        for blood_request in blood_requests:
            for donor in donors:
                subject = f"Urgent Blood Request for Patient {blood_request.patient.get_full_name()}"
                message = (
                    f"Dear {donor.get_full_name()},\n\n"
                    f"A patient urgently needs blood of group {blood_request.blood_group}.\n\n"
                    f"Patient: {blood_request.patient.get_full_name()}\n"
                    f"Required Quantity: {blood_request.quantity} units\n"
                    f"Reason: {blood_request.reason}\n\n"
                    f"If you are able to donate or know someone who can, please contact the hospital immediately.\n\n"
                    f"Thank you for your generosity!\n\nBlood Donation System"
                )
                send_mail(subject, message, 'noreply@yourdomain.com', [donor.email])

            # Mark this request as processed
            blood_request.is_processed = True
            blood_request.save()

        messages.success(request, "Emails have been sent to all donors.")
        return redirect('view_blood_requests')

    return HttpResponse("Invalid request method.", status=400)





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatMessage

@login_required
def admin_chat_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    messages_qs = ChatMessage.objects.filter(parent=None).order_by('-timestamp')
    receivers = CustomUser.objects.filter(role='donor')

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        receiver_id = request.POST.get('receiver')
        parent_id = request.POST.get('parent')

        if message_text:
            receiver = CustomUser.objects.filter(id=receiver_id).first() if receiver_id else None
            parent_msg = ChatMessage.objects.filter(id=parent_id).first() if parent_id else None

            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message_text,
                parent=parent_msg
            )
            return redirect('admin_chat_view')
        else:
            messages.error(request, "Message cannot be empty.")

    return render(request, 'admin/admin_chat.html', {
        'messages': messages_qs,
        'receivers': receivers
    })


@login_required
def donor_chat_view(request):
    if request.user.role != 'donor':
        return redirect('home')

    # Only messages sent to this donor or public messages
    messages_qs = ChatMessage.objects.filter(
        parent=None
    ).filter(
        receiver__isnull=True
    ) | ChatMessage.objects.filter(
        parent=None, receiver=request.user
    )
    messages_qs = messages_qs.order_by('-timestamp')

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        parent_id = request.POST.get('parent')

        if message_text and parent_id:
            parent_msg = ChatMessage.objects.filter(id=parent_id).first()
            if parent_msg:
                ChatMessage.objects.create(
                    sender=request.user,
                    receiver=parent_msg.sender,  # Reply back to Admin
                    message=message_text,
                    parent=parent_msg
                )
            return redirect('donor_chat_view')
        else:
            messages.error(request, "Reply cannot be empty.")

    return render(request, 'dashboard/donor_chat.html', {
        'messages': messages_qs
    })
