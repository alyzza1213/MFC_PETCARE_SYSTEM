from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # ✅ import built-in auth views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('index/', views.index, name='index'),
    

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='main/password_reset.html'
         ), 
         name='password_reset'),
    path('logout/', views.logout_view, name='logout'),

    # ✅ Forgot Password (Password Reset)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='main/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),

    # Pets
    path('pet-profile/', views.pet_profile, name='pet_profile'),
    path('pet/<int:pet_id>/', views.pet_detail, name='pet_detail'),
    path('pet/<int:pet_id>/delete/', views.delete_pet, name='delete_pet'),
    path('add-pet/', views.add_or_edit_pet, name='add_pet'),
    path('pet/<int:pet_id>/edit/', views.add_or_edit_pet, name='edit_pet'),
    path('pet/<int:pet_id>/update-image/', views.update_pet_image, name='update_pet_image'),
    path('pet-records/', views.pet_records, name='pet_records'),


    # Vaccine
    path('vaccine-records/', views.vaccine_records, name='vaccine_records'),
    path('vaccine/<int:pet_id>/', views.vaccine_detail, name='vaccine_detail'),


    # Vet availability & appointments
    path('vet-availability/', views.vet_availability, name='vet_availability'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),

    # Client pet records
path('pet-records/', views.pet_records, name='pet_records'),


   # Admin side
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('user-registry/', views.user_registry, name='user_registry'),
path('pet-records/', views.pet_records_admin, name='pet_records'),

path('vaccine-records-admin/', views.vaccine_records_admin, name='vaccine_records_admin'),
path('appointment-hub/', views.appointment_hub, name='appointment_hub'),
path('vet-availability-admin/', views.vet_availability_admin, name='vet_availability_admin'),
path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

]

# Serve uploaded images (MEDIA_URL) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
