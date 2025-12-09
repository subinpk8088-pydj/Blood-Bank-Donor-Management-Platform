#Hospital management django

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('admin-panel/pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('admin-panel/approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    
    
    
    
    path("validate/username/", views.validate_username, name="validate_username"),
    path("validate/email/", views.validate_email, name="validate_email"),
    path("validate/phone/", views.validate_phone, name="validate_phone"),
    
    
    
    path('patients/', views.admin_patient_list, name='admin_patient_list'),
    path('patient/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    
    path('doctors/', views.doctor_list, name='doctor_list'),
     path('doctors/delete/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('donors/', views.donor_list, name='donor_list'),
    path('donors/delete/<int:pk>/', views.delete_donor, name='delete_donor'),

    
    path('change-password/', views.change_password, name='change_password'),
     path('change-password/', views.change_password, name='change_password'),
    
    
    path('request-appointment/', views.request_appointment, name='appointment_request'),
    path('appointments/', views.view_appointments, name='view_appointments'),
    path('consult-appointment/<int:appointment_id>/', views.consult_appointment, name='consult_appointment'),

    path('view-appointments/', views.view_all_appointments, name='view_all_appointments'),
    
    
    
    path('doctor/patients/', views.doctor_patient_list, name='doctor_patient_list'),
    path('doctor/donors/', views.donor_list_view_for_doctor, name='donor_list_view_for_doctor'),
    
    
     path('patients/donors/', views.donor_list_view_for_patient, name='patient_donor_list'),
     
     
     
     path('patient-blood/', views.patient_blood, name='patient_blood'),
     
     path('blood-request/', views.blood_request_view, name='blood_request'),
     path('request-blood/', views.request_blood, name='request_blood'),
     
     path('blood-requests/', views.view_blood_requests, name='view_blood_requests'),
     path('send-blood-request-emails/', views.send_blood_request_emails, name='send_blood_request_emails'),
     
     path('admin-chat/', views.admin_chat_view, name='admin_chat_view'),
    path('donor-chat/', views.donor_chat_view, name='donor_chat_view'),
    
    
     path('validate-email/', views.validate_email, name='validate_email'),
    path('validate-phone/', views.validate_phone, name='validate_phone'),
    path('validate-firstname/', views.validate_firstname, name='validate_firstname'),
]
