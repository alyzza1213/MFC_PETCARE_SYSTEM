from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [

    #----------BOTH ADMIN AND USER VIEWS NI SIYA HA TAS SA LOGIN/REGISTER------------------

        #LANDING PAGE
            path('', views.landing_page, name='landing'),

        #HOMEPAGE
            path('', views.homepage, name='homepage'),

        #--------------
            path('index/', views.index, name='index'),

        
        #AUTHENTICATION
            path('register/', views.register, name='register'),
            path('login/', views.login_view, name='login'),
            path('logout/', views.logout_view, name='logout'),


        # PASSWORD RESET
            path('password_reset/', auth_views.PasswordResetView.as_view(
                template_name='main/password_reset.html'), name='password_reset'),

            path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
                template_name='main/password_reset_done.html'), name='password_reset_done'),

            path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),

            path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
                template_name='main/password_reset_complete.html'), name='password_reset_complete'),

   






    #------------------------CLIENT SIDE---------------------------------------------------------------------------------------------------------
   


        # -----VIEW PET PROFILE & DETAILS, ADD/EDIT/DELETE PET,PET RECORDS-------

             # PET PROFILE 
                    
                    path('pet-profile/', views.pet_profile, name='pet_profile'),

             # PET DETAILS
                    path('pet/<int:pet_id>/', views.pet_detail, name='pet_detail'),
            
             # ADD
                    path('pet/add/', views.add_pet, name='add_pet'),

             # ADD OR EDIT PET
                    path('add-pet/', views.add_or_edit_pet_user, name='add_pet_user'),
                    path('pet/<int:pet_id>/edit/', views.add_or_edit_pet_user, name='add_or_edit_pet_user'),

             
             # PET RECORDS
                    path('pet-records/', views.pet_records_user, name='pet_records_user'),

             # UPDATE IMAGE
                    path('pet/<int:pet_id>/update-image/', views.update_pet_image, name='update_pet_image'),

              #------------------------------      
                    path('', views.homepage, name='homepage'),
             
             # BACK BUTTON
                    path('pet/<int:pet_id>/', views.pet_detail, name='pet_detail'),
                 
         #---------------------VACCINE RECORDS-------------------------------------------
    
             # VACCINE RECORDS
                    path('vaccine-records/', views.vaccine_records, name='vaccine_records'),

             # PET DETAILS
                    path('vaccine/<int:pet_id>/', views.vaccine_detail, name='vaccine_detail'),

             # ADD VACCINE
                    path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),
                    path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),
    

         #--------------------MEDICAL HISTORY/CHECKUPS/CONSULTATION-------------------------
             # MEDICAL 
                path('medical-records/', views.view_medical_records, name='view_medical_records'),

         # ------------------------VET AVAILABILITY & APPOINTMENTS--------------------------

             # VET AVAILABILITY
                    path('vet-availability/', views.vet_availability, name='vet_availability'),

             # BOOK APPOINTMENT
                    path('book-appointment/', views.book_appointment, name='book_appointment'),
            
             # MY APPOINTMENT
                    path('my-appointments/', views.my_appointments, name='my_appointments'),
        
             # APPOINTMENT LIST
                    path('appointment-list/', views.appointment_list, name='appointment_list'),
            
             # APPOINTMENT STATUS
                    path('appointment/<int:appointment_id>/update-status/', views.appointment_update_status, name='appointment_update_status'),
   
    
   
 

  
    #--------------------------------------------CLIENTS SIDE END---------------------------------------------------------------------------------------








   

    #------------------------------------------------------ADMIN SIDE----------------------------------------------------------------------------------
        

        # ------------------------VIEW ADMIN DASHBOARD---------------------------------

             # ADMIN DASHBOARD
                 path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
                 path('admin/calendar/events/', views.admin_appointments_json, name='admin_appointments_json'),

        #------------------------CLIENTS & PETS------------------------------------------

             # CLIENTS & PETS
                 path('clients/', views.clients_pets, name='clients_pets'),
                 

            # CLIENTS LIST
                 path('clients/', views.clients_pets, name='clients_pets'),


            # CLIENTS DETAILS
                 path('client/<int:user_id>/', views.client_detail, name='client_detail'),
                 path('clients/<int:client_id>/', views.client_detail, name='client_detail'),

            

         # ---------------------VIEW/ADD/EDIT---------------------------------------

             # ADD PET 
                 path('add-pet-admin/', views.add_or_edit_pet_admin, name='add_pet_admin'),

             # EDIT PET ADMIN
                 path('pets/<int:pet_id>/edit/', views.edit_pet_admin, name='edit_pet_admin'),  
                 path('edit-pet/<int:pet_id>/', views.edit_pet_admin, name='edit_pet_admin'),
                 path('pet/<int:pet_id>/edit-admin/', views.add_or_edit_pet_admin, name='edit_pet_admin'),
            
             # EDIT USER ADMIN
                 path('edit-user/<int:client_id>/', views.edit_user_admin, name='edit_user_admin'),

             # EDIT PET USER
                 path('pet/<int:pet_id>/edit/', views.edit_pet_user, name='edit_pet_user'),

             # VIEW PET
                 path('pet/<int:pet_id>/', views.view_pet, name='view_pet'),


         # ---------------------PET DETAIL/PET RECORDS---------------------------------------

             # PET DETAILS
                 path('pets/<int:pet_id>/', views.pet_detail_admin, name='pet_detail_admin'),


             # PET RECORDS 
                 path('pet-records-admin/', views.pet_records_admin, name='pet_records_admin'),   
                 path('pet-records/<int:pet_id>/', views.pet_records_admin, name='pet_records_admin'),
                 path('pet-records-admin/<int:pet_id>/', views.pet_records_admin, name='pet_records_admin'),
                 path('pet-records/', views.pet_records_admin, name='pet_records_admin'),

             # PET RECORDS DETAIL
                 path('pet-records-admin/<int:pet_id>/', views.pet_record_detail_admin, name='pet_record_detail_admin'),
                 path('pet-records/<int:pet_id>/', views.pet_record_detail_admin, name='pet_record_detail_admin'),


         # ---------------------VACCINE RECORDS---------------------------------------

             # ADD VACCINE
                 path('vaccine-records-admin/add/', views.add_vaccine, name='add_vaccine'),
                
                 path('vaccine-records-admin/add/<int:pet_id>/', views.add_vaccine, name='add_vaccine'),
                 

             # VACCINE RECORDS
                 path('vaccine-records-admin/', views.vaccine_records_admin, name='vaccine_records_admin'),
                
                path ('vaccine-records-admin/<int:pet_id>/', views.vaccine_records_admin, name='vaccine_records_admin'),
                 path('vaccine-records-admin/<int:pet_id>/', views.vaccine_records_admin, name='vaccine_records_admin'),

             # UPDATE VACCINE RECORDS
                 path('vaccine-records-admin/update/<int:record_id>/', views.update_vaccine, name='update_vaccine'),

             # DELETE VACCINE RECORDS
                 path('vaccine-records-admin/delete/<int:record_id>/', views.delete_vaccine, name='delete_vaccine'),


         #----------------------PET HISTORY/HEALTH CHECKUPS/CONSULTATION/GROOMING RECORDS--------------------------------------------

             # PET HISTORY
                 path('pet/<int:pet_id>/history/add/', views.add_history, name='add_history'),

             # COMBINE ANG CHECK-UP AND CONSULTATION
                   path('pets/<int:pet_id>/medical-history/', views.medical_history, name='medical_history'),
                   
                    # ADD CHECK-UP
                        

                    # EDIT CHECK-UP
                       
                        



             # CONSULTATIONS
                 
            
             # GROOMING
                 path('pets/<int:pet_id>/grooming/', views.view_grooming, name='view_grooming'),


         #----------------------APPOINTMENT HUB--------------------------------------------

             # APPOINMENT LIST
                    path('appointment-list/', views.appointment_list, name='appointment_list'),


         #------------------------WORKING DAYS---------------------------------------------------------
           
             # ADD WOORKING DAY
                 path('add-working-day/', views.add_working_day, name='add_working_day'),

             # TOGGLE WORKING DAY
                 path("toggle-working-day/", views.toggle_working_day, name="toggle_working_day"),

             # EDIT WORKING DAY
                 path('vet-availability-admin/edit/<str:date>/', views.edit_working_day, name='edit_working_day'),


         #------------------------VET AVAILABILITY---------------------------------------------------------
    
             #VET AVAILABILITY
                 path('vet-availability-admin/', views.vet_availability_admin, name='vet_availability_admin'),
                  path('vet-availability-admin/edit/<date>/', views.edit_working_day, name='edit_working_day'),










    #--------------------------------------------ADMIN SIDE END---------------------------------------------------------------------------------------
    
]

# Serve uploaded images in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
