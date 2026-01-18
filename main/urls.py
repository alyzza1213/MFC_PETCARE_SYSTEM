from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('', views.landing_page, name='landing'),
    # --------------------------
    # Home
    # --------------------------
    
    path('', views.homepage, name='homepage'),
    path('index/', views.index, name='index'),

    # --------------------------
    # Authentication
    # --------------------------
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='main/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='main/password_reset_complete.html'), name='password_reset_complete'),

    # --------------------------
    # User Pets
    # --------------------------
    path('pet-profile/', views.pet_profile, name='pet_profile'),
    path('pet/<int:pet_id>/', views.pet_detail, name='pet_detail'),
    path('pet/<int:pet_id>/delete/', views.delete_pet, name='delete_pet'),
    path('add-pet/', views.add_or_edit_pet_user, name='add_pet_user'),
    path('pet/<int:pet_id>/edit/', views.add_or_edit_pet_user, name='add_or_edit_pet_user'),
    path('pet/<int:pet_id>/update-image/', views.update_pet_image, name='update_pet_image'),
    path('pet-records/', views.pet_records_user, name='pet_records_user'),
    
    path('pet/add/', views.add_pet, name='add_pet'),
    path('', views.homepage, name='homepage'),
    
    
    # --------------------------
    # Vaccine
    # --------------------------
     path('vaccine-records/', views.vaccine_records, name='vaccine_records'),
    path('vaccine/<int:pet_id>/', views.vaccine_detail, name='vaccine_detail'),
# Must include <int:pet_id> in the URL
path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),
 path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),

    # --------------------------
    # Vet availability & Appointments
    # --------------------------
    path('vet-availability/', views.vet_availability, name='vet_availability'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
 

    path('my-appointments/', views.my_appointments, name='my_appointments'),
   path('appointment-list/', views.appointment_list, name='appointment_list'),
    path('appointment/<int:appointment_id>/update-status/', views.appointment_update_status, name='appointment_update_status'),

    # --------------------------
    # Admin Side
    # --------------------------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('clients/', views.clients_pets, name='clients_pets'),
    path('client/<int:user_id>/', views.client_detail, name='client_detail'),
    path('clients/', views.clients_list, name='clients_pets'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),

    
path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
  # Admin delete user

    path('add-pet-admin/', views.add_or_edit_pet_admin, name='add_pet_admin'),
    path('vaccine-records-admin/add/', views.add_vaccine, name='add_vaccine'),
   
  
    path('pets/<int:pet_id>/edit/', views.edit_pet_admin, name='edit_pet_admin'),
    path('pets/<int:pet_id>/', views.pet_detail_admin, name='pet_detail_admin'),

    
    path('edit-user/<int:client_id>/', views.edit_user_admin, name='edit_user_admin'),
path('pet/<int:pet_id>/edit-admin/', views.add_or_edit_pet_admin, name='edit_pet_admin'),

# Soft-delete
path('pet/<int:pet_id>/remove/', views.remove_pet_admin, name='remove_pet_admin'),

# Removed pets list
path('admin-dashboard/removed-pets/', views.removed_pets_admin, name='removed_pets_admin'),

# Restore pet
path('pet/<int:pet_id>/restore/', views.restore_pet_admin, name='restore_pet_admin'),

# Permanently delete a pet
path('admin-dashboard/removed-pets/<int:pet_id>/delete/', views.delete_pet_permanent, name='delete_pet_permanent'),

path('pet/<int:pet_id>/', views.view_pet, name='view_pet'),


path('pet/<int:pet_id>/edit/', views.edit_pet_user, name='edit_pet_user'),



path('pet-records-admin/', views.pet_records_admin, name='pet_records_admin'),
path('pet-records-admin/<int:pet_id>/', views.pet_records_admin, name='pet_records_admin'),
path('pet-records-admin/<int:pet_id>/', views.pet_record_detail_admin, name='pet_record_detail_admin'),

  
    path('pet-records/<int:pet_id>/', views.pet_records_admin, name='pet_records_admin'),

    path('edit-pet/<int:pet_id>/', views.edit_pet_admin, name='edit_pet_admin'),
  path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),




# urls.py
path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),
path('pet/<int:pet_id>/history/add/', views.add_history, name='add_history'),

    



path('pet-records/<int:pet_id>/', views.pet_record_detail_admin, name='pet_record_detail_admin'),

 path('pet-records/', views.pet_records_admin, name='pet_records_admin'),

    path('vaccine-records-admin/', views.vaccine_records_admin, name='vaccine_records_admin'),

    # Admin vaccine detail
    path('vaccine/<int:pet_id>/admin/', views.vaccine_detail_admin, name='vaccine_detail_admin'),
    path('vaccine-records-admin/', views.vaccine_records_admin, name='vaccine_records_admin'),
    path('vaccine-records-admin/add/', views.add_vaccine, name='add_vaccine'),
    
    
    # Admin appointment hub
    path('appointment-list/', views.appointment_list, name='appointment_list'),
    path('add-working-day/', views.add_working_day, name='add_working_day'),
    path("toggle-working-day/", views.toggle_working_day, name="toggle_working_day"),
    path('vet-availability-admin/edit/<str:date>/', views.edit_working_day, name='edit_working_day'),



    # Admin clinic schedule
    path('vet-availability-admin/', views.vet_availability_admin, name='vet_availability_admin'),
]

# Serve uploaded images in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
