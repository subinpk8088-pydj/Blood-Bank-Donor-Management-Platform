from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('donor', 'Donor'),
        ('patient', 'Patient'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    patient_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    
    
    
# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    ]
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    doctor_findings = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Appointment with Dr. {self.doctor.get_full_name()} on {self.appointment_date}"
    
    
    
from django.db import models
from django.conf import settings
from app.models import CustomUser  # Update the import path if necessary

class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = CustomUser.BLOOD_GROUP_CHOICES

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    quantity = models.PositiveIntegerField(help_text="Units required")
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} requested {self.quantity} unit(s) of {self.blood_group}"




from django.db import models

class ChatMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def is_root_message(self):
        return self.parent is None
