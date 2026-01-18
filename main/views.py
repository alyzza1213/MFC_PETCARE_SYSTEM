from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .forms import PetForm, VaccinationForm, VaccineForm
from .models import (
    Pet, Owner, Service,
    WorkingDay, Appointment, VetAvailability,
    History, Vaccination, VaccineRecord,
    Vaccine, Grooming,MedicalRecord
)
from .notifications import (
    send_registration_email,
    send_appointment_approval_email,
    send_payment_confirmation_email
)

from datetime import date, datetime, time, timedelta
from calendar import monthrange
import calendar
import os
import qrcode
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMessage

from django.db.models import Count


    #---------------BOTH ADMIN AND USER VIEWS NI SIYA HA TAS SA LOGIN/REGISTER-------------

# LANDING PAGE
def landing_page(request):
    return render(request, 'main/homepage.html') 

# HOMEPAGE
def homepage(request):
    return render(request, 'main/homepage.html')

# INDEX 
def index(request):
     return render(request, 'main/index.html')

# RESISTER
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Gmail only
        if not email.endswith('@gmail.com'):
            messages.error(request, 'Gmail account lang ang pwede gamiton.')
            return render(request, 'main/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # ✅ SEND EMAIL NOTIFICATION
            email_subject = "Welcome to MFC Pet Life 🐾"
            email_body = f"""
            Hi {username},

            Your account has been successfully created!

            You can now log in using your username and password.

            Thank you,
            MFC Pet Life Team
            """

            email_message = EmailMessage(
                email_subject,
                email_body,
                to=[email]
            )
            email_message.send()

            messages.success(request, 'Account created successfully! Check your email.')
            return redirect('login')

    return render(request, 'main/register.html')

     # LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Safe access to is_staff
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('homepage')
        else:
            # Invalid login
            messages.error(request, 'Invalid username or password')
            return render(request, 'main/login.html')

    # GET request
    return render(request, 'main/login.html')


def logout_view(request):
            logout(request)
            return redirect('login')














#----------------USER PET VIEWS SA CLIENT SIDE NI------------------

     # PET PROFILE
def pet_profile(request):
            pets = Pet.objects.filter(owner=request.user)
            for pet in pets:
                pet.years = pet.age // 12
                pet.months = pet.age % 12
            return render(request, 'clients/pet_profile.html', {'pets': pets})

     #ADD OR EDIT PET USER
def add_pet(request, pet_id=None):
            pet = None
            if pet_id:
                pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
            if request.method == 'POST':
                name = request.POST.get('name')
                species = request.POST.get('species')
                breed = request.POST.get('breed')
                gender = request.POST.get('gender')
                color = request.POST.get('color')
                birthday = request.POST.get('birthday')
                weight = request.POST.get('weight')
                image = request.FILES.get('image')

                age_total_months = 0
                if birthday:
                    try:
                        bday = timezone.datetime.strptime(birthday, '%Y-%m-%d').date()
                        today = timezone.now().date()
                        age_total_months = (today.year - bday.year) * 12 + (today.month - bday.month)
                    except ValueError:
                        messages.error(request, "Invalid birthday format.")
                        return redirect('add_pet_user')

                if pet:
                    pet.name = name
                    pet.species = species
                    pet.breed = breed
                    pet.gender = gender
                    pet.color = color
                    pet.birthday = birthday
                    pet.age = age_total_months
                    pet.weight = weight if weight else pet.weight
                    if image:
                        pet.image = image
                    pet.save()
                    messages.success(request, "Pet updated successfully!")
                else:
                    pet = Pet.objects.create(
                        owner=request.user,
                        name=name,
                        species=species,
                        breed=breed,
                        gender=gender,
                        color=color,
                        birthday=birthday,
                        age=age_total_months,
                        weight=weight if weight else None,
                        image=image
                    )
                    messages.success(request, "Pet added successfully!")

                return redirect('pet_detail', pet_id=pet.id)

            return render(request, "clients/add_edit_pet.html", {"pet": pet})

# PET DETAIL
def pet_detail(request, pet_id):
    # Admin can view any pet, client only their own
    if request.user.is_staff:
        pet = get_object_or_404(Pet, id=pet_id)
    else:
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)

    # Age calculation
    if pet.birthday:
        today = date.today()
        age_in_months = (today.year - pet.birthday.year) * 12 + (today.month - pet.birthday.month)
        pet.years = age_in_months // 12
        pet.months = age_in_months % 12
    else:
        pet.years = '-'
        pet.months = '-'

    # Vaccine records
    vaccines = pet.vaccine_records.all().order_by('-date_given')

    # Medical records
    medical_records = MedicalRecord.objects.filter(
        pet=pet
    ).select_related('vet').order_by('-date')

    # Pass everything to template
    return render(request, 'clients/pet_detail.html', {
        'pet': pet,
        'vaccines': vaccines,
        'medical_records': medical_records,  # ✅ correctly defined
    })

#------------------------DRI KAY MAG ADD OG PET TAS IMAGE SA PET PROFILE (CLIENTS SIDE NI)---------------------------
    
# UPDATE PET IMAGE
def update_pet_image(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST' and request.FILES.get('image'):
        pet.image = request.FILES['image']
        pet.save()
    return JsonResponse({'status': 'success', 'image_url': pet.image.url})
    return JsonResponse({'status': 'error'}, status=400)

# ADD PET




#------------------------------- VIEW SINGLE PET DETAIL NI SIYA -----------------------

def view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, 'clients/view_pet.html', {'pet': pet})

# CLIENTS PET VACCINE RECORDS NI
def pet_records_user(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'clients/pet_records.html', {'pets': pets})

def vaccine_records(request):
    records = Vaccination.objects.filter(pet__owner=request.user)
    return render(request, 'clients/vaccine_records.html', {'records': records})

def vaccine_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    vaccines = Vaccination.objects.filter(pet=pet)
    return render(request, 'clients/vaccine_detail.html', {'pet': pet, 'vaccines': vaccines})



#-----------------------BOOKING APPOINTMENT NI SIYA SA CLIENT SIDE LANG NI----------------------- 

def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'clients/my_appointments.html', {'appointments': appointments})

def vet_availability(request):
    today = date.today()
    year = today.year
    month = today.month

    # ✅ calendar alignment
    first_day = date(year, month, 1)
    start_weekday = first_day.weekday()  # Mon = 0
    empty_days_start = range(start_weekday)

    num_days = monthrange(year, month)[1]
    month_days = []

    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)

        # ❌ DO NOT SKIP PAST DAYS (important for alignment)
        working_day, _ = WorkingDay.objects.get_or_create(date=day_date)

        available_times = []

        # Disable booking for past dates
        if day_date >= today:
            appointments = Appointment.objects.filter(date=day_date)

            # Morning
            if working_day.morning_open:
                slot = datetime.combine(day_date, time(7, 30))
                end = datetime.combine(day_date, time(11, 30))
                while slot <= end:
                    if not appointments.filter(time=slot.time()).exists():
                        available_times.append(slot.time())
                    slot += timedelta(minutes=30)

            # Afternoon
            if working_day.afternoon_open:
                slot = datetime.combine(day_date, time(13, 0))
                end = datetime.combine(day_date, time(17, 0))
                while slot <= end:
                    if not appointments.filter(time=slot.time()).exists():
                        available_times.append(slot.time())
                    slot += timedelta(minutes=30)

        # Status
        if working_day.morning_open and working_day.afternoon_open:
            status = 'whole'
        elif working_day.morning_open or working_day.afternoon_open:
            status = 'half'
        else:
            status = 'closed'

        month_days.append({
            'date': day_date,
            'available_times': available_times,
            'status': status,
            'is_past': day_date < today
        })

    # optional: fill last row
    total_cells = start_weekday + num_days
    empty_days_end = range((7 - total_cells % 7) % 7)

    context = {
        'month_days': month_days,
        'current_month': today,
        'empty_days_start': empty_days_start,
        'empty_days_end': empty_days_end,
    }

    return render(request, "clients/vet_availability.html", context)


#----------------SERVICE DURATION------------------
    
SERVICE_DURATION = {
    "Consultation": 30,
    "Check-up": 30,
    "Vaccination": 20,
    "Grooming": 60,
}

def get_available_slots(target_date, service_type="Check-up"):
    duration = timedelta(minutes=SERVICE_DURATION.get(service_type, 30))

    # Get working day
    try:
        day = WorkingDay.objects.get(date=target_date)
    except WorkingDay.DoesNotExist:
        return []

    slots = []

    # Helper to check if a slot is free
    def is_free(start_time):
        start_dt = datetime.combine(target_date, start_time)
        end_dt = start_dt + duration
        overlapping = Appointment.objects.filter(
            date=target_date,
            time__lt=end_dt.time(),
        ).exclude(time__gte=end_dt.time())
        return not overlapping.exists()

    # Morning slots
    if day.morning_open:
        current = datetime.combine(target_date, time(7, 30))
        end = datetime.combine(target_date, time(11, 30))
        while current + duration <= end:
            if is_free(current.time()):
                slots.append(current.time())
            current += timedelta(minutes=10)

    # Afternoon slots
    if day.afternoon_open:
        current = datetime.combine(target_date, time(13, 0))
        end = datetime.combine(target_date, time(17, 0))
        while current + duration <= end:
            if is_free(current.time()):
                slots.append(current.time())
            current += timedelta(minutes=10)

    return slots


def book_appointment(request):
    user = request.user
    pets = Pet.objects.filter(owner=user)
    qr_code_url = None

    # Get target date
    target_date_str = request.GET.get("date")
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date() if target_date_str else date.today()
    except ValueError:
        target_date = date.today()

    # Determine service type
    service_type = request.POST.get("service_1", "Check-up")
    available_slots = get_available_slots(target_date, service_type)

    if request.method == "POST":
        selected_pets = request.POST.getlist("selected_pets")
        slot_str = request.POST.get("slot")
        notes = request.POST.get("notes", "")

        if slot_str and selected_pets:
            slot_time = datetime.strptime(slot_str, "%H:%M").time()
            for pet_id in selected_pets:
                pet = Pet.objects.get(id=pet_id)
                service_type = request.POST.get(f"service_{pet_id}", "Check-up")

                # Save appointment (duration handled in model property)
                Appointment.objects.create(
                    user=user,
                    pet=pet,
                    date=target_date,
                    time=slot_time,
                    appointment_type=service_type,
                    notes=notes,
                    status="Pending"
                )

            qr_code_url = "/path/to/gcash_qr.png"
            messages.success(request, "Your appointment has been successfully booked! Please complete the payment below.")

    context = {
        "pets": pets,
        "available_slots": available_slots,
        "qr_code_url": qr_code_url,
        "target_date": target_date,
    }
    return render(request, "clients/book_appointment.html", context)


def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.appointment_type in ['Check-up', 'Consultation']:
        MedicalRecord.objects.create(
            pet=appointment.pet,
            record_type=appointment.appointment_type,
            concern=appointment.notes,
            vet=request.user  # admin vet
        )

    appointment.status = 'Approved'
    appointment.save()
    return redirect('appointment_list') 


# CALENDAR NI NA PART

def client_calendar(request):
    today = date.today()
    year = today.year
    month = today.month
    num_days = monthrange(year, month)[1]

    month_days = []

    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)

        # Get or create working day
        working_day, _ = WorkingDay.objects.get_or_create(date=day_date)

        # Get appointments for the day
        appointments = Appointment.objects.filter(date=day_date).order_by('time')

        available_times = []

        # Morning session
        if working_day.morning_open:
            start_time = datetime.combine(day_date, time(7, 30))
            end_time = datetime.combine(day_date, time(11, 30))
            slot = start_time
            while slot <= end_time:
                if not appointments.filter(time=slot.time()).exists():
                    available_times.append(slot.time())
                slot += timedelta(minutes=30)

        # Afternoon session
        if working_day.afternoon_open:
            start_time = datetime.combine(day_date, time(13, 0))
            end_time = datetime.combine(day_date, time(17, 0))
            slot = start_time
            while slot <= end_time:
                if not appointments.filter(time=slot.time()).exists():
                    available_times.append(slot.time())
                slot += timedelta(minutes=30)

        # Compute status dynamically
        if working_day.morning_open and working_day.afternoon_open:
            status = 'whole'
        elif working_day.morning_open or working_day.afternoon_open:
            status = 'half'
        else:
            status = 'closed'

        month_days.append({
            'date': day_date,
            'is_working': working_day.morning_open or working_day.afternoon_open,
            'appointments': appointments,
            'available_times': available_times,
            'status': status,
        })

    # Determine empty start/end for correct calendar alignment
    first_weekday = date(year, month, 1).weekday()  # Mon=0
    empty_days_start = list(range(first_weekday))
    remainder = (first_weekday + num_days) % 7
    empty_days_end = [] if remainder == 0 else list(range(7 - remainder))

    context = {
        'month_days': month_days,
        'current_month': date(year, month, 1),
        'empty_days_start': empty_days_start,
        'empty_days_end': empty_days_end,
        'today': today,
    }

    return render(request, "client/client_calendar.html", context)

#---------------EDIT PET USER---------------------

def add_or_edit_pet_user(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == "POST":
        pet.name = request.POST.get("name")
        pet.species = request.POST.get("species")
        pet.breed = request.POST.get("breed")
        pet.gender = request.POST.get("gender")
        pet.birthday = request.POST.get("birthday")
        weight = request.POST.get("weight")
        pet.weight = float(weight) if weight else None
        pet.save()
        
        return redirect('pet_detail', pet_id=pet.id)  # or your user view page

        return render(request, 'pet/user_edit_pet.html', {'pet': pet})


#-----------------------SERVICE RECORDS NI NA PART----------------------

#-------------CHECK-UP HISTORY----------------
def view_checkups(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    checkups = pet.checkup_set.all().order_by('-date')
    return render(request, 'client/view_checkups.html', {'pet': pet, 'checkups': checkups})

def view_medical_records(request):
    # Get all medical records for the logged-in user's pets
    medical_records = MedicalRecord.objects.filter(pet__user=request.user).order_by('-date')
    return render(request, 'clients/view_medical_records.html', {'medical_records': medical_records})


#---------------------CLIENTS SIDE END ----------------------




















#----------------ADMIN SIDE NA PART SA BABA TANAN---------------

    #------ADMIN DASHBOARD NI----------


def is_admin(user):
    return user.is_staff


def admin_dashboard(request):
    total_users = User.objects.count()
    total_pets = Pet.objects.filter(is_active=True).count()
    total_vaccines = Vaccine.objects.count()
    total_appointments = Appointment.objects.count()
    total_vets = VetAvailability.objects.count()

    context = {
        'total_users': total_users,
        'total_pets': total_pets,
        'total_vaccines': total_vaccines,
        'total_appointments': total_appointments,
        'total_vets': total_vets,
    }

    return render(request, 'admin/admin_dashboard.html', context)


def admin_appointments_json(request):
    events = []

    for a in Appointment.objects.all():
        events.append({
            "title": f"{a.pet.name} - {a.client.name}",
            "start": a.date.strftime("%Y-%m-%d"),
            "extendedProps": {
                "client": a.client.name,
                "pet": a.pet.name,
                "status": a.status,
            }
        })

    return JsonResponse(events, safe=False)

#-------VET AVAILABILITY ADMIN SA CALENDAR------------

def admin_calendar(request):
    today = date.today()
    current_month = date(today.year, today.month, 1)
    year, month = current_month.year, current_month.month

    first_weekday, total_days = calendar.monthrange(year, month)
    month_days = []

    for day in range(1, total_days + 1):
        d = date(year, month, day)
        wd = WorkingDay.objects.filter(date=d).first()

        # Determine status
        if wd:
            if not wd.is_active:
                status = 'closed'
            elif wd.morning_open and wd.afternoon_open:
                status = 'whole'
            else:
                status = 'half'
        else:
            status = 'whole'

        # Determine if the date is past
        is_past = d < today

        month_days.append({
            'date': d,
            'status': status,
            'is_working': status != 'closed',
            'is_past': is_past,
        })

    # Empty cells for calendar alignment
    empty_days_start = list(range(first_weekday))
    remainder = (first_weekday + total_days) % 7
    empty_days_end = [] if remainder == 0 else list(range(7 - remainder))

    context = {
        "current_month": current_month,
        "month_days": month_days,
        "empty_days_start": empty_days_start,
        "empty_days_end": empty_days_end,
    }

    return render(request, "admin_calendar.html", context)

# ---------CLIENTS LIST------------
    def clients_list(request):
        clients = User.objects.filter(is_staff=False)
        return render(request, 'admin/clients_list.html', {'clients': clients})
            

# ---------CLIENTS DETAIL / PET DETAILS -----------     
        
    # CLIENTS DETAILS   

def client_detail(request, client_id):
    client = get_object_or_404(User, id=client_id)
    pets = Pet.objects.filter(owner=client, is_active=True)
    return render(request, "admin/client_detail.html", {"client": client, "pets": pets})
            

    # PET DETAILS ADMIN

def pet_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    # Get vaccinations and appointments safely
    vaccinations = pet.vaccine_records.all()  # matches related_name in Vaccine
    appointments = pet.appointments.all()     # matches related_name in Appointment

    if request.method == "POST":
        # Update pet fields safely
        pet.name = request.POST.get("name", pet.name).strip()
        pet.species = request.POST.get("species", pet.species).strip()
        pet.breed = request.POST.get("breed", pet.breed).strip()
        pet.gender = request.POST.get("gender", pet.gender)
        pet.birthday = request.POST.get("birthday") or pet.birthday

        # Handle weight
        weight = request.POST.get("weight")
        if weight:
            try:
                pet.weight = float(weight)
            except ValueError:
                messages.error(request, "Weight must be a valid number.")
                return render(request, 'admin/pet_detail_admin.html', {
                    'pet': pet,
                    'vaccinations': vaccinations,
                    'appointments': appointments
                })

        try:
            pet.save()
            messages.success(request, "Pet info updated successfully!")
            return redirect('pet_records_admin')  # or wherever you want
        except Exception as e:
            messages.error(request, f"Error saving pet: {e}")
            return render(request, 'admin/pet_detail_admin.html', {
                'pet': pet,
                'vaccinations': vaccinations,
                'appointments': appointments
            })

    return render(request, 'admin/pet_detail_admin.html', {
        'pet': pet,
        'vaccinations': vaccinations,
        'appointments': appointments
    })

# -------CLIENTS & PETS ------------
def clients_pets(request):
    show = request.GET.get('show', 'clients')

    clients = User.objects.filter(is_staff=False)
    pets = Pet.objects.all()

    total_pets = pets.count()

    return render(request, 'admin/clients_pets.html', {
        'clients': clients,
        'pets': pets,
        'total_pets': total_pets,
        'show': show,
    })


#-------PETS VACCINE RECORDS--------------

def add_vaccine(request, pet_id):  # <-- include pet_id
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == "POST":
        form = VaccinationForm(request.POST)
        if form.is_valid():
            vaccination = form.save(commit=False)
            vaccination.pet = pet  # link the vaccination to this pet
            vaccination.save()
            return redirect('pet_detail_admin', pet.id)
        else:
                form = VaccinationForm()

                context = {
                    'form': form,
                    'pet': pet
                }
                return render(request, 'admin/vaccine_records_admin.html', context)
            
        # ADD VACCINE 
def add_vaccine(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == "POST":
        date_given = request.POST.get("date_given")
        vaccine_name = request.POST.get("vaccine_name", "").strip()

                        # Prevent duplicate
    exists = Vaccine.objects.filter(
        pet=pet,
        date_given=date_given,
        vaccine_name__iexact=vaccine_name
        )

    if not exists.exists():
        Vaccine.objects.create(
            pet=pet,
            date_given=date_given or None,
            next_due=request.POST.get("next_due") or None,
            weight=float(request.POST.get("weight", 0)) if request.POST.get("weight") else None,
            vaccine_name=vaccine_name,
            manufacturer=request.POST.get("manufacturer", "").strip(),
            veterinarian=request.POST.get("veterinarian", "").strip()
            )

        return redirect('vaccine_records_admin', pet_id=pet.id)
            

def vaccine_records_admin(request, pet_id=None):
    if pet_id:
            pet = get_object_or_404(Pet, id=pet_id)
            context = {'pet': pet}
            return render(request, 'admin/vaccine_records_admin.html', context)
    else:
                    # Redirect or show a list of pets
        return redirect('clients_pets')

        # UPDATE VACCINE
def update_vaccine(request, record_id):
    record = Vaccine.objects.get(id=record_id)

    if request.method == "POST":
        record.date_given = request.POST.get("date_given") or record.date_given
        record.next_due = request.POST.get("next_due") or None
        record.weight = float(request.POST.get("weight", 0)) if request.POST.get("weight") else record.weight
        record.vaccine_name = request.POST.get("vaccine_name", record.vaccine_name).strip()
        record.manufacturer = request.POST.get("manufacturer", record.manufacturer).strip()
        record.veterinarian = request.POST.get("veterinarian", record.veterinarian).strip()
        record.save()
        return redirect('vaccine_records_admin', pet_id=record.pet.id)
            

        # DELETE VACCINE
def delete_vaccine(request, record_id):
    record = Vaccine.objects.get(id=record_id)
    pet_id = record.pet.id
    record.delete()
    return redirect('vaccine_records_admin', pet_id=pet_id)

#----------PET RECORDS ADMIN--------

def pet_records_admin(request):
    pets = Pet.objects.select_related('owner').all()
    return render(request, 'admin/pet_records_admin.html', {'pets': pets})
            



# ------------PET RECORDS DETAILS----------------

def pet_record_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, 'admin/pet_record_detail_admin.html', {'pet': pet})



    #-----------APPOINTMENT LIST ----------
SERVICE_DURATION = {
    "Consultation": 30,
    "Check-up": 30,
    "Vaccination": 20,
    "Grooming": 60,
}

def get_available_slots(target_date, service_type="Check-up"):
    duration = timedelta(minutes=SERVICE_DURATION.get(service_type, 30))
    slots = []

    # Morning slots: 7:30 AM – 11:30 AM
    current = datetime.combine(target_date, time(7, 30))
    end = datetime.combine(target_date, time(11, 30))

    while current + duration <= end:
        if not Appointment.objects.filter(
            date=target_date,
            time__lt=(current + duration).time(),   # ✅ FIX
            time__gte=current.time()                # ✅ FIX
        ).exists():
            slots.append(current.time())
        current += timedelta(minutes=10)

    # Afternoon slots: 1:00 PM – 5:00 PM
    current = datetime.combine(target_date, time(13, 0))
    end = datetime.combine(target_date, time(17, 0))

    while current + duration <= end:
        if not Appointment.objects.filter(
            date=target_date,
            time__lt=(current + duration).time(),   # ✅ FIX
            time__gte=current.time()                # ✅ FIX
        ).exists():
            slots.append(current.time())
        current += timedelta(minutes=10)

    return slots


def generate_qr_code_url(appointment):
    """
    Generate a QR code PNG for the appointment payment link,
    save it under MEDIA_ROOT/qr_codes/, and return the media URL.
    """
    # Ensure QR code folder exists
    qr_folder = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_folder, exist_ok=True)

    # File name example: appointment-<id>.png
    filename = f"appointment-{appointment.id}.png"
    filepath = os.path.join(qr_folder, filename)

    # Example QR data (can be dynamic link to payment page or GCash)
    qr_data = f"Payment for Appointment #{appointment.id} - Client: {appointment.client.username}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)

    # Return media URL for HTML/email
    return f"{settings.MEDIA_URL}qr_codes/{filename}"

# --- Send payment email with embedded QR ---
def send_payment_email(appointment):
    subject = "Complete Your Appointment Payment"
    qr_url = appointment.qr_code_url
    message = f"""
    Hi {appointment.client.username},<br><br>
    Please complete your payment to confirm your appointment for {appointment.pet.name} at {appointment.slot}.<br>
    Scan the QR code below to pay via GCash:<br>
    <img src="{qr_url}" width="250px"><br><br>
    Thank you!
    """
    email = EmailMessage(subject, message, to=[appointment.client.email])
    email.content_subtype = "html"
    email.send()


def book_appointment(request):
    pets = Pet.objects.filter(owner=request.user)
    target_date = timezone.now().date()  # Or let client choose date

    if request.method == "POST":
        selected_pets = request.POST.getlist('selected_pets')
        slot_str = request.POST.get('slot')
        notes = request.POST.get('notes', '')

        if not selected_pets or not slot_str:
            return render(request, 'booking.html', {
                'pets': pets,
                'available_slots': get_available_slots(target_date),
                'error': "Please select pet(s) and slot."
            })

        slot_time = datetime.strptime(slot_str, "%H:%M").time()
        service_type = request.POST.get(f'service_{selected_pets[0]}', "Check-up")
        available_slots = get_available_slots(target_date, service_type)

        if slot_time not in available_slots:
            return render(request, 'booking.html', {
                'pets': pets,
                'available_slots': available_slots,
                'error': "Slot already booked. Please select another."
            })

        # Create pending appointments
        for pet_id in selected_pets:
            service = request.POST.get(f'service_{pet_id}', "Check-up")
            concern = request.POST.get(f'concern_{pet_id}', '')
            pet = Pet.objects.get(id=pet_id)
            appointment = Appointment.objects.create(
                client=request.user,
                pet=pet,
                service=service,
                concern=concern,
                slot=slot_time,
                status='pending'
            )

            # Generate QR code URL (your function)
            qr_code_url = generate_qr_code_url(appointment)
            appointment.qr_code_url = qr_code_url
            appointment.save()

            # Send email
            send_payment_email(appointment)

        return redirect('booking_success')

    # GET request
    default_service = "Check-up"
    available_slots = get_available_slots(target_date, default_service)
    return render(request, 'booking.html', {
        'pets': pets,
        'available_slots': available_slots
    })




    #-------UPDATE APPOINTMENT STATUS -----

def appointment_update_status(request, appointment_id):
        appt = get_object_or_404(Appointment, id=appointment_id)

        if request.method == "POST":
            new_status = request.POST.get("status")
            if new_status in ["Approved", "Rejected"]:
                appt.status = new_status
                appt.save()

            return redirect('appointment_list')

    
     # BOOK MULTIPLE APPOINTMENTS

def book_multi_pet_appointment(request):
    user_pets = Pet.objects.filter(owner=request.user)

    if request.method == "POST":
        day_date = datetime.strptime(request.POST.get('date'), "%Y-%m-%d").date()
        selected_pets_services = []  # List of dicts {'pet': Pet, 'service_type': str}

        for pet in user_pets:
            service_type = request.POST.get(f'service_{pet.id}')
            if service_type:
                selected_pets_services.append({'pet': pet, 'service_type': service_type})

            if not selected_pets_services:
                messages.error(request, "Please select at least one pet and service.")
                return redirect('booking_page')

                    # Calculate total duration
                total_duration = timedelta()
                for ps in selected_pets_services:
                        if ps['service_type'] == 'Grooming':
                            total_duration += timedelta(minutes=60)
                        else:
                            total_duration += timedelta(minutes=30)

                    # Find earliest available start time
                appointment_time = find_next_available_time(day_date, total_duration)
                if appointment_time:
                    for ps in selected_pets_services:
                        duration = timedelta(minutes=60 if ps['service_type']=='Grooming' else 30)
                        Appointment.objects.create(
                            user=request.user,
                            pet=ps['pet'],
                            date=day_date,
                                time=appointment_time,
                            appointment_type=ps['service_type'],
                                status='Pending'
                            )
                            # Increment start time for next pet
                        appointment_time = (datetime.combine(day_date, appointment_time) + duration).time()
                        messages.success(request, "Appointments booked successfully!")
                else:
                    messages.error(request, "No available slot for this booking on the selected day.")

                return redirect('booking_page')

            return render(request, 'booking_page.html', {'pets': user_pets})

def appointment_list(request):
    # Select related foreign keys
    appointments = Appointment.objects.select_related('user', 'pet').all().order_by('-date', 'time')

    total_users = User.objects.filter(is_staff=False).count()
    total_pets = Pet.objects.count()
    total_appointments = appointments.count()

    context = {
        'appointments': appointments,
        'total_users': total_users,
        'total_pets': total_pets,
        'total_appointments': total_appointments
    }

    return render(request, 'admin/appointment_list.html', context)

#-------WORKING DAY-------------

def add_working_day(request):
    if request.method == "POST":
        date_str = request.POST.get("working_day")

    if date_str:
        day_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        WorkingDay.objects.get_or_create(date=day_date)  # Avoid duplicates
        return redirect("vet_availability_admin")
            

def edit_working_day(request, date):
    # Convert string to date
    day_date = datetime.strptime(date, "%Y-%m-%d").date()
    working_day, _ = WorkingDay.objects.get_or_create(date=day_date)

    if request.method == 'POST':
        working_day.morning_open = 'morning_open' in request.POST
        working_day.afternoon_open = 'afternoon_open' in request.POST
        working_day.save()
        return redirect('vet_availability_admin')

    # GET request → render form
    context = {
        'day_date': day_date,
        'morning_open': working_day.morning_open,
        'afternoon_open': working_day.afternoon_open,
    }
    return render(request, 'admin/edit_working_day.html', context)


def toggle_working_day(request, day_id):
    day = get_object_or_404(WorkingDay, id=day_id)
    day.is_active = not day.is_active
    day.save()

    return redirect('vet_availability_admin')

#------VET AVAILABILITY -----------

def vet_availability_admin(request):
    today = date.today()
    year = today.year
    month = today.month

    num_days = monthrange(year, month)[1]
    month_days = []

    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)

        # Get or create working day
        working_day, _ = WorkingDay.objects.get_or_create(date=day_date)

        # Get appointments for the day
        appointments = Appointment.objects.filter(date=day_date).order_by('time')

        available_times = []

        # Morning session
        if working_day.morning_open:
            start_time = datetime.combine(day_date, time(7, 30))
            end_time = datetime.combine(day_date, time(11, 30))
            slot = start_time
            while slot <= end_time:
                if not appointments.filter(time=slot.time()).exists():
                    available_times.append(slot.time())
                slot += timedelta(minutes=30)

        # Afternoon session
        if working_day.afternoon_open:
            start_time = datetime.combine(day_date, time(13, 0))
            end_time = datetime.combine(day_date, time(17, 0))
            slot = start_time
            while slot <= end_time:
                if not appointments.filter(time=slot.time()).exists():
                    available_times.append(slot.time())
                slot += timedelta(minutes=30)

        # Compute status dynamically
        if working_day.morning_open and working_day.afternoon_open:
            status = 'whole'
        elif working_day.morning_open or working_day.afternoon_open:
            status = 'half'
        else:
            status = 'closed'

        month_days.append({
            'date': day_date,
            'is_working': working_day.morning_open or working_day.afternoon_open,
            'appointments': appointments,
            'available_times': available_times,
            'status': status,
        })

    context = {
        'month_days': month_days,
        'current_month': today,
    }

    return render(request, "admin/vet_availability_admin.html", context)


    # AVAILABLE TIME

def find_next_available_time(day_date, total_duration):

    sessions = [
        (time(7, 30), time(11, 30)),   # Morning
        (time(13, 0), time(17, 0))     # Afternoon
    ]

    appointments = Appointment.objects.filter(
        date=day_date,
        status__in=['Pending', 'Approved'],
        time__isnull=False
    ).order_by('time')

    blocked = []
    for appt in appointments:
        appt_start = datetime.combine(day_date, appt.time)
        appt_end = appt_start + appt.duration
        blocked.append((appt_start, appt_end))

    for start, end in sessions:
        current = datetime.combine(day_date, start)
        session_end = datetime.combine(day_date, end)

        while current + total_duration <= session_end:
            slot_end = current + total_duration

            overlaps = any(
                current < b_end and slot_end > b_start
                for b_start, b_end in blocked
            )

            if not overlaps:
                return current.time()   # ✅ earliest available

            # ✅ move forward if overlap
            current += timedelta(minutes=5)

    # ✅ only return None after ALL sessions checked
    return None


    #------------ADD OR EDIT PET SA ADMIN SIDE -------------

def add_or_edit_pet_admin(request, pet_id=None):
    pet = None
    
    if pet_id:
        pet = get_object_or_404(Pet, id=pet_id)

    owners = User.objects.filter(is_staff=False)

    if request.method == 'POST':
        name = request.POST.get('name')
        species = request.POST.get('species')
        breed = request.POST.get('breed')
        gender = request.POST.get('gender')
        color = request.POST.get('color')
        birthday = request.POST.get('birthday')
        weight = request.POST.get('weight')
        owner_id = request.POST.get('owner')
        image = request.FILES.get('image')

        # Convert birthday to date
        bday_obj = None
        age_total_months = 0
        if birthday:
            try:
                bday_obj = timezone.datetime.strptime(birthday, '%Y-%m-%d').date()
                today = timezone.now().date()
                age_total_months = (today.year - bday_obj.year) * 12 + (today.month - bday_obj.month)
            except ValueError:
                messages.error(request, "Invalid birthday format.")
                return redirect('add_pet_admin')

        owner = get_object_or_404(User, id=owner_id)

        if pet:
            pet.name = name
            pet.species = species
            pet.breed = breed
            pet.gender = gender
            pet.color = color
            pet.birthday = bday_obj
            pet.age = age_total_months
            pet.weight = weight if weight else pet.weight
            pet.owner = owner
            if image:
                pet.image = image
            pet.save()
            messages.success(request, "Pet updated successfully!")
        else:
            pet = Pet.objects.create(
                owner=owner,
                name=name,
                species=species,
                breed=breed,
                gender=gender,
                color=color,
                birthday=bday_obj,
                age=age_total_months,
                weight=weight if weight else None,
                image=image
            )
            messages.success(request, "Pet added successfully!")

        return redirect('pet_records_admin')

    return render(request, "admin/add_edit_pet_admin.html", {"pet": pet, "owners": owners})


#--------------------EDIT ADMIN--------------------------------------------------------------

    # USER ADMIN
def edit_user_admin(request, client_id):
    client = get_object_or_404(User, id=client_id)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        client.username = username
        client.email = email
        client.save()

        return redirect("client_detail", client_id=client.id)

        return render(request, "admin/edit_user_admin.html", {"client": client})
            
def edit_pet_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)

    if form.is_valid():
                form.save()
                return redirect('pet_detail_admin', pet_id=pet.id)
    
    else:
                form = PetForm(instance=pet)
                return render(request, 'admin/edit_pet_admin.html', {'form': form, 'pet': pet})


    # PET ADMIN
def edit_pet_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)

    if form.is_valid():
            form.save()
            return redirect('pet_records_admin', pet_id=pet.id)
    
    else:
                form = PetForm(instance=pet)
                return render(request, 'admin/edit_pet.html', {'form': form, 'pet': pet})

    # PET USER
def edit_pet_user(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
                
    if request.method == "POST":
         form = PetForm(request.POST, instance=pet)

    if form.is_valid():
            form.save()
            return redirect('pet_records')  # redirect sa pet list
    else:
            form = PetForm(instance=pet)

            return render(request, 'clients/edit_pet_user.html', {'form': form, 'pet': pet})


#---------------------HISTORY--------------------------------------------------------------------------------------------------
def add_history(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == "POST":
        date = request.POST.get("date")
        description = request.POST.get("description")
        diagnosis = request.POST.get("diagnosis")
        treatment = request.POST.get("treatment")

        History.objects.create(
            pet=pet,
            date=date,
            description=description,
            diagnosis=diagnosis,
            treatment=treatment
            )
        
        return redirect('pet_detail_admin', pet_id=pet.id)

        return render(request, 'admin/add_history.html', {'pet': pet})


#--------------------------------------SERVICE LIST---------------------------------------------------------------

    #----------COMBINE ANG CHECK-UPS AND CONSULTATIONS-----------------
def medical_history(request, pet_id):
    """
    Single page: shows all medical records (Check-Up / Consultation / Emergency)
    with appointment date for each record.
    Admin can add new record, client can view.
    """
    pet = get_object_or_404(Pet, id=pet_id)

    # Admin adds a record
    if request.method == 'POST' and request.user.is_staff:
        weight = request.POST.get('weight')
        findings = request.POST.get('findings', '')
        treatment = request.POST.get('treatment', '')
        record_type = request.POST.get('record_type', 'Check-Up')

        # Optionally link to an appointment
        appointment_id = request.POST.get('appointment_id')
        appointment = Appointment.objects.filter(id=appointment_id).first() if appointment_id else None

        MedicalRecord.objects.create(
            pet=pet,
            weight=weight,
            findings=findings,
            treatment=treatment,
            reason_for_visit=record_type,
            vet=request.user,
            date=timezone.now(),
            appointment=appointment
        )

    # Fetch all medical records
    records = MedicalRecord.objects.filter(pet=pet).order_by('-date')

    return render(request, 'admin/medical_history.html', {
        'pet': pet,
        'records': records
    })

    
        # ADD CHECK-UPS

        # GROOMING
def view_grooming(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    grooming_records = Grooming.objects.filter(pet=pet)
    return render(request, 'admin/grooming.html', {
        'pet': pet,
        'grooming': grooming_records
})






#-------------NOTIFICATIONS-----------------------