from django import views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.utils import timezone

from .forms import PetForm, VaccinationForm, VaccineForm
from .models import (
    Pet, Owner, Service,
    WorkingDay, Appointment, VetAvailability,
    History, Vaccination, VaccineRecord,
    Vaccine, Grooming, MedicalRecord, ServiceImage, Payment, 
    GcashQR, ClinicSettings, VaccinationReminderLog
)
from .notifications import (
    send_registration_email,
    send_appointment_approval_email,
    send_payment_confirmation_email
)

from datetime import date, datetime, time, timedelta
from calendar import monthrange
import calendar
from io import BytesIO
import qrcode
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import IntegrityError

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
   


#---------------BOTH ADMIN AND USER VIEWS NI SIYA HA TAS SA LOGIN/REGISTER-------------


# LANDING PAGE
def landing_page(request):
    return render(request, 'main/landing_page.html')

def homepage(request):
    return redirect('home')

# RESISTER
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email.endswith('@gmail.com'):
            messages.error(request, 'Gmail account lang ang pwede gamiton.')
            return render(request, 'main/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'main/register.html')

        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
        except IntegrityError:
            messages.error(request, 'Error creating account.')
            return render(request, 'main/register.html')

        messages.success(request, 'Account created! Check your email.')
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

            print("LOGIN:", request.user.is_authenticated)

            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('home')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'main/login.html')



def logout_view(request):
    logout(request)
    return redirect('landing_page')










#----------------USER PET VIEWS SA CLIENT SIDE NI------------------

def client_dashboard_legacy(request):
    return render(request, 'clients/client_dashboard.html')



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

    grooming_records = pet.grooming_records.all().order_by('-date')

    # Pass everything to template
    return render(request, 'clients/pet_detail.html', {
        'pet': pet,
        'vaccines': vaccines,
        'medical_records': medical_records,  # ✅ correctly defined
        'grooming_records': grooming_records,
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
    pets = Pet.objects.filter(owner=request.user).prefetch_related('vaccine_records')
    records = Vaccination.objects.filter(pet__owner=request.user)
    return render(request, 'clients/vaccine_records.html', {'pets': pets, 'records': records})

def vaccine_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    vaccines = Vaccination.objects.filter(pet=pet)
    return render(request, 'clients/vaccine_detail.html', {'pet': pet, 'vaccines': vaccines})



#-----------------------BOOKING APPOINTMENT NI SIYA SA CLIENT SIDE LANG NI----------------------- 

@login_required(login_url='login')
def home(request):
    today = timezone.localdate()
    pets = list(Pet.objects.filter(owner=request.user, is_active=True).order_by('name'))
    upcoming_appointments = list(
        Appointment.objects.filter(user=request.user, date__gte=today)
        .select_related('pet')
        .order_by('date', 'time')[:5]
    )
    recent_appointments = list(
        Appointment.objects.filter(user=request.user)
        .select_related('pet')
        .order_by('-date', '-time')[:4]
    )
    recent_vaccinations = list(
        Vaccination.objects.filter(pet__owner=request.user, pet__is_active=True)
        .select_related('pet')
        .order_by('-date_given')[:5]
    )
    pending_payments = list(
        Payment.objects.filter(appointment__user=request.user, status='pending')
        .select_related('appointment__pet')
        .order_by('-created_at')[:3]
    )

    for pet in pets[:3]:
        pet.display_age = pet.calculate_age() if pet.birthday else pet.age

    next_due_count = Vaccine.objects.filter(
        pet__owner=request.user,
        pet__is_active=True,
        next_due__isnull=False,
        next_due__gte=today,
    ).count()

    context = {
        'today': today,
        'pets': pets[:3],
        'total_pets': len(pets),
        'upcoming_appointments': upcoming_appointments,
        'upcoming_count': len(upcoming_appointments),
        'recent_appointments': recent_appointments,
        'recent_vaccinations': recent_vaccinations,
        'vaccination_count': len(recent_vaccinations),
        'next_due_count': next_due_count,
        'pending_payments': pending_payments,
        'pending_payment_count': len(pending_payments),
        'next_appointment': upcoming_appointments[0] if upcoming_appointments else None,
    }
    return render(request, 'clients/client_dashboard.html', context)

@login_required(login_url='/login/')
def my_appointments(request):
    appointments = list(Appointment.objects.filter(user=request.user).order_by('date', 'time'))
    payments_by_appointment = {
        payment.appointment_id: payment
        for payment in Payment.objects.filter(appointment__user=request.user).select_related('appointment')
    }
    for appointment in appointments:
        appointment.payment_record = payments_by_appointment.get(appointment.id)
    return render(request, 'clients/my_appointments.html', {
        'appointments': appointments,
    })


def get_working_day_status(day_date, working_day=None):
    if day_date.weekday() == 6:
        return "closed"

    if working_day is None:
        return "not_set"

    if not working_day.is_active:
        return "closed"

    if working_day.morning_open and working_day.afternoon_open:
        return "whole"

    if working_day.morning_open or working_day.afternoon_open:
        return "half"

    return "closed"


def get_schedule_choice(day_date, working_day=None):
    if day_date.weekday() == 6:
        return "closed"

    if working_day is None:
        return "not_set"

    if not working_day.is_active:
        return "closed"

    if working_day.morning_open and working_day.afternoon_open:
        return "whole"

    if working_day.morning_open:
        return "morning"

    if working_day.afternoon_open:
        return "afternoon"

    return "closed"


def build_available_times(day_date, working_day, interval_minutes=30):
    status = get_working_day_status(day_date, working_day)
    if status in ["closed", "not_set"]:
        return []

    appointments = Appointment.objects.filter(date=day_date)
    available_times = []

    sessions = []
    if working_day.morning_open:
        sessions.append((time(7, 30), time(11, 30)))
    if working_day.afternoon_open:
        sessions.append((time(13, 0), time(17, 0)))

    for start_time, end_time in sessions:
        slot = datetime.combine(day_date, start_time)
        end = datetime.combine(day_date, end_time)
        while slot <= end:
            if not appointments.filter(time=slot.time()).exists():
                available_times.append(slot.time())
            slot += timedelta(minutes=interval_minutes)

    return available_times


def vet_availability(request):
    today = timezone.localdate()
    year = today.year
    month = today.month

    # ✅ calendar alignment
    first_day = date(year, month, 1)
    start_weekday = first_day.weekday()  # Mon = 0
    empty_days_start = range(start_weekday)

    num_days = monthrange(year, month)[1]
    month_days = []

    working_days = {
        item.date: item
        for item in WorkingDay.objects.filter(date__range=(first_day, date(year, month, num_days)))
    }

    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)
        working_day = working_days.get(day_date)
        status = get_working_day_status(day_date, working_day)
        available_times = build_available_times(day_date, working_day) if day_date >= today else []
        is_bookable = day_date >= today and status in ["whole", "half"] and bool(available_times)

        month_days.append({
            'date': day_date,
            'available_times': available_times,
            'status': status,
            'is_past': day_date < today,
            'is_bookable': is_bookable,
        })

    # optional: fill last row
    total_cells = start_weekday + num_days
    empty_days_end = range((7 - total_cells % 7) % 7)

    context = {
        'month_days': month_days,
        'current_month': today,
        'empty_days_start': empty_days_start,
        'empty_days_end': empty_days_end,
        'today': today,
    }

    return render(request, "clients/vet_availability.html", context)


#----------------SERVICE DURATION------------------
    
SERVICE_DURATION = {
    "Consultation": 30,
    "Check-up": 30,
    "Vaccination": 20,
    "Grooming": 60,
}


def get_service_amount(appointment_type):
    service = Service.objects.filter(name__iexact=appointment_type).first()
    return service.price if service else Decimal("0.00")

def get_available_slots(target_date, service_type="Check-up"):
    duration = timedelta(minutes=SERVICE_DURATION.get(service_type, 30))

    # Get working day
    day = WorkingDay.objects.filter(date=target_date).first()
    if get_working_day_status(target_date, day) in ["closed", "not_set"]:
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
    if day and day.morning_open:
        current = datetime.combine(target_date, time(7, 30))
        end = datetime.combine(target_date, time(11, 30))
        while current + duration <= end:
            if is_free(current.time()):
                slots.append(current.time())
            current += timedelta(minutes=10)

    # Afternoon slots
    if day and day.afternoon_open:
        current = datetime.combine(target_date, time(13, 0))
        end = datetime.combine(target_date, time(17, 0))
        while current + duration <= end:
            if is_free(current.time()):
                slots.append(current.time())
            current += timedelta(minutes=10)

    return slots


@login_required(login_url='login')
def book_appointment(request):
    user = request.user

    # Get all pets for this user
    pets = Pet.objects.filter(owner=user)
    qr_code_url = None

    # Get target date from GET params
    target_date_str = request.GET.get("date")
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date() if target_date_str else timezone.localdate()
    except ValueError:
        target_date = timezone.localdate()

    # ✅ FIXED: no more service_1
    available_slots = get_available_slots(target_date)

    if request.method == "POST":
        selected_pets = request.POST.getlist("selected_pets")
        slot_str = request.POST.get("slot")
        notes = request.POST.get("notes", "")

        # ✅ Validation (prevents 500 error)
        if not selected_pets:
            messages.error(request, "Please select at least one pet.")
            return redirect(request.path)

        if not slot_str:
            messages.error(request, "Please select a time slot.")
            return redirect(request.path)

        try:
            slot_time = datetime.strptime(slot_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid time slot.")
            return redirect(request.path)

        for pet_id in selected_pets:
            try:
                pet = Pet.objects.get(id=pet_id, owner=user)
                service_type = request.POST.get(f"service_{pet_id}", "Check-up")

                Appointment.objects.create(
                    user=user,
                    pet=pet,
                    date=target_date,
                    time=slot_time,
                    appointment_type=service_type,
                    notes=notes,
                    status="Pending"
                )

            except Pet.DoesNotExist:
                messages.error(request, f"Pet with ID {pet_id} not found.")
                continue

        # Optional QR
        qr_code_url = "/path/to/gcash_qr.png"

        messages.success(request, "Your appointment has been successfully booked!")
        return redirect('my_appointments')  # ✅ important redirect

    context = {
        "pets": pets,
        "available_slots": available_slots,
        "qr_code_url": qr_code_url,
        "target_date": target_date,
    }
    return render(request, "clients/book_appointment.html", context)


@login_required(login_url='login')
def submit_payment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('pet'),
        id=appointment_id,
        user=request.user,
    )
    qr = GcashQR.objects.first()
    payment = Payment.objects.filter(appointment=appointment).first()
    amount = get_service_amount(appointment.appointment_type)

    if request.method == "POST":
        if payment and payment.status == "verified":
            messages.info(request, "This appointment payment is already verified.")
            return redirect('submit_payment', appointment_id=appointment.id)

        gcash_ref_no = request.POST.get("gcash_ref_no", "").strip()
        screenshot = request.FILES.get("screenshot")

        if not gcash_ref_no:
            messages.error(request, "Please enter your GCash reference number.")
        else:
            if payment is None:
                payment = Payment.objects.create(
                    appointment=appointment,
                    gcash_ref_no=gcash_ref_no,
                    screenshot=screenshot,
                    amount=amount,
                    status="pending",
                )
            else:
                payment.gcash_ref_no = gcash_ref_no
                payment.amount = amount
                payment.status = "pending"
                if screenshot:
                    payment.screenshot = screenshot
                payment.save()

            appointment.payment_status = "Unpaid"
            appointment.save(update_fields=["payment_status"])
            messages.success(request, "Payment proof submitted. Please wait for verification.")
            return redirect('my_appointments')

    context = {
        "appointment": appointment,
        "payment": payment,
        "qr": qr,
        "amount": amount,
    }
    return render(request, "clients/payment_submission.html", context)


@login_required(login_url='login')
def approve_appointment(request, appointment_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access only.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method != "POST":
        return redirect('appointment_requests')

    if (
        appointment.pet
        and appointment.appointment_type in ['Check-up', 'Consultation']
        and not MedicalRecord.objects.filter(appointment=appointment).exists()
    ):
        MedicalRecord.objects.create(
            pet=appointment.pet,
            findings=appointment.notes or "",
            reason_for_visit=appointment.appointment_type,
            vet=request.user,
            appointment=appointment,
        )

    appointment.status = 'Approved'
    appointment.save(update_fields=['status'])
    messages.success(request, "Appointment approved successfully.")
    return redirect('appointment_requests')


@login_required(login_url='login')
def cancel_appointment(request, appointment_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access only.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        appointment.status = 'Rejected'
        appointment.save(update_fields=['status'])
        messages.success(request, "Appointment cancelled successfully.")

    return redirect('appointment_requests')


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
    total_users = User.objects.filter(is_staff=False).count()
    total_pets = Pet.objects.filter(is_active=True).count()
    pending_appointments_count = Appointment.objects.filter(status='Pending').count()
    completed_appointments_count = Appointment.objects.filter(status='Approved').count()
    pending_payments_count = Payment.objects.filter(status='pending').count()
    paid_payments_count = Payment.objects.filter(status='verified').count()

    clients_preview = User.objects.filter(is_staff=False).annotate(pet_count=Count('pet')).order_by('-date_joined')[:4]
    pending_appointments = Appointment.objects.select_related('user', 'pet').filter(status='Pending').order_by('date', 'time')[:4]
    services_preview = Service.objects.prefetch_related('images').order_by('name')[:5]

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_days = [week_start + timedelta(days=offset) for offset in range(7)]
    working_days = {item.date: item for item in WorkingDay.objects.filter(date__range=(week_days[0], week_days[-1]))}
    weekly_schedule = []

    for day in week_days:
        working_day = working_days.get(day)
        if day.weekday() == 6 or (working_day and not working_day.is_active):
            hours = "Closed"
            status = "closed"
        elif working_day and working_day.morning_open and working_day.afternoon_open:
            hours = "7:30 AM – 5:00 PM"
            status = "whole"
        elif working_day and working_day.morning_open:
            hours = "7:30 AM – 11:30 AM"
            status = "half"
        elif working_day and working_day.afternoon_open:
            hours = "1:00 PM – 5:00 PM"
            status = "half"
        else:
            hours = "Not Set"
            status = "not_set"

        weekly_schedule.append({
            "date": day,
            "hours": hours,
            "status": status,
        })

    notifications = []

    for a in pending_appointments:
        pet_name = a.pet.name if a.pet else "Deleted pet"
        notifications.append(f"Pending appointment: {pet_name} on {a.date:%b %d} at {a.time:%I:%M %p}")

    context = {
        'total_users': total_users,
        'total_pets': total_pets,
        'pending_appointments_count': pending_appointments_count,
        'completed_appointments_count': completed_appointments_count,
        'pending_payments_count': pending_payments_count,
        'paid_payments_count': paid_payments_count,
        'clients_preview': clients_preview,
        'pending_appointments': pending_appointments,
        'services_preview': services_preview,
        'weekly_schedule': weekly_schedule,
        'week_start': week_days[0],
        'week_end': week_days[-1],
        'notif_count': len(notifications),
        'notifications': notifications[:3],
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

    vaccinations = pet.vaccine_records.all()
    appointments = pet.appointments.all()
    medical_records = pet.medical_records.all().order_by('-date')
    grooming_records = pet.grooming_records.all().order_by('-date')

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
                    'appointments': appointments,
                    'medical_records': medical_records,
                    'grooming_records': grooming_records,
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
                'appointments': appointments,
                'medical_records': medical_records,
                'grooming_records': grooming_records,
            })

    return render(request, 'admin/pet_detail_admin.html', {
        'pet': pet,
        'vaccinations': vaccinations,
        'appointments': appointments,
        'medical_records': medical_records,
        'grooming_records': grooming_records,
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

def get_available_slots_legacy(target_date, service_type="Check-up"):
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
    save it through Django's configured storage, and return the file URL.
    """
    filename = f"qr_codes/appointment-{appointment.id}.png"
    client_name = appointment.user.username if appointment.user_id else "client"
    qr_data = f"Payment for Appointment #{appointment.id} - Client: {client_name}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    image_buffer = BytesIO()
    img.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    saved_path = default_storage.save(filename, ContentFile(image_buffer.getvalue()))
    return default_storage.url(saved_path)

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

def appointment_requests(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access only.")

    # Select related foreign keys
    appointments = Appointment.objects.select_related('user', 'pet').all().order_by('-date', 'time')

    total_users = User.objects.filter(is_staff=False).count()
    total_pets = Pet.objects.count()
    total_appointments = appointments.count()
    pending_appointments_total = Appointment.objects.filter(status='Pending').count()
    pending_appointments = Appointment.objects.filter(status='Pending').order_by('-created_at')[:3]

    notifications = [
        f"Pending appointment for {appointment.pet.name} on {appointment.date} at {appointment.time.strftime('%I:%M %p')}"
        for appointment in pending_appointments
        if appointment.pet and appointment.time
    ]

    context = {
        'appointments': appointments,
        'total_users': total_users,
        'total_pets': total_pets,
        'total_appointments': total_appointments,
        'pending_appointments_total': pending_appointments_total,
        'notif_count': len(notifications),
        'notifications': notifications,
    }

    return render(request, 'admin/appointment_requests.html', context)

#-------WORKING DAY-------------

def add_working_day(request):
    if request.method == "POST":
        date_str = request.POST.get("working_day")

    if date_str:
        day_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        WorkingDay.objects.get_or_create(date=day_date)  # Avoid duplicates
        return redirect("vet_availability_admin")
            

def toggle_working_day(request, day_id):
    day = get_object_or_404(WorkingDay, id=day_id)
    day.is_active = not day.is_active
    day.save()

    return redirect('vet_availability_admin')

#------VET AVAILABILITY -----------

def vet_availability_admin(request):

    today = date.today()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        current_month = date(year, month, 1)
    except ValueError:
        current_month = date(today.year, today.month, 1)
        year = current_month.year
        month = current_month.month

    # =========================
    # SAVE MODAL FORM
    # =========================
    if request.method == "POST":
        day_date = request.POST.get("day_date")
        schedule_status = request.POST.get("schedule_status", "not_set")

        day_obj = datetime.strptime(day_date, "%Y-%m-%d").date()

        if schedule_status == "not_set" and day_obj.weekday() != 6:
            WorkingDay.objects.filter(date=day_obj).delete()
            return redirect(f"{request.path}?year={day_obj.year}&month={day_obj.month}")

        obj, created = WorkingDay.objects.get_or_create(date=day_obj)
        if day_obj.weekday() == 6 or schedule_status == "closed":
            obj.is_active = False
            obj.morning_open = False
            obj.afternoon_open = False
        elif schedule_status == "morning":
            obj.is_active = True
            obj.morning_open = True
            obj.afternoon_open = False
        elif schedule_status == "afternoon":
            obj.is_active = True
            obj.morning_open = False
            obj.afternoon_open = True
        else:
            obj.is_active = True
            obj.morning_open = True
            obj.afternoon_open = True
        obj.save()

        return redirect(f"{request.path}?year={day_obj.year}&month={day_obj.month}")

    # =========================
    # CALENDAR BUILD
    # =========================
    num_days = monthrange(year, month)[1]
    month_days = []

    first_day = date(year, month, 1)
    start_weekday = first_day.weekday()

    last_day = date(year, month, num_days)
    end_weekday = last_day.weekday()

    empty_days_start = range(start_weekday)
    empty_days_end = range(6 - end_weekday)

    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)

        working_day = WorkingDay.objects.filter(date=day_date).first()
        appointments = Appointment.objects.filter(date=day_date).order_by('time')
        status = get_working_day_status(day_date, working_day)
        available_times = build_available_times(day_date, working_day)

        # FINAL OUTPUT
        month_days.append({
            "date": day_date,
            "appointments": appointments,
            "available_times": available_times,
            "status": status,
            "schedule_choice": get_schedule_choice(day_date, working_day),
            "is_sunday": day_date.weekday() == 6,
        })

    previous_month = date(year - 1, 12, 1) if month == 1 else date(year, month - 1, 1)
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    return render(request, "admin/vet_availability_admin.html", {
        "month_days": month_days,
        "current_month": current_month,
        "previous_month": previous_month,
        "next_month": next_month,
        "empty_days_start": empty_days_start,
        "empty_days_end": empty_days_end,
    })


def vet_availability_get(request, day_date):
    try:
        parsed_date = datetime.strptime(day_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date"}, status=400)

    working_day = WorkingDay.objects.filter(date=parsed_date).first()
    status = get_working_day_status(parsed_date, working_day)
    return JsonResponse({
        "status": status,
        "schedule_status": get_schedule_choice(parsed_date, working_day),
        "morning_open": bool(status in ["whole", "half"] and working_day and working_day.morning_open),
        "afternoon_open": bool(status in ["whole", "half"] and working_day and working_day.afternoon_open),
        "is_sunday": parsed_date.weekday() == 6,
    })

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



def service_list(request):
    services = Service.objects.all()

    return render(request, "admin/service_list.html", {
        "services": services
    })

def add_service(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        service = Service.objects.create(
            name=name,
            description=description,
            price=price
        )

        # SAVE IMAGE
        if image:
            ServiceImage.objects.create(
                service=service,
                image=image
            )

        return redirect("payments_admin")

    # IMPORTANT: handle GET request
    return redirect("payments_admin")

def add_service_legacy(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")

        Service.objects.create(name=name, price=price)

        return redirect("service_list")


def delete_service(request, service_id):
    service = Service.objects.get(id=service_id)
    service.delete()
    return redirect("payments_admin")

def update_services(request):
    if request.method == "POST":
        for service in Service.objects.all():
            service.name = request.POST.get(f"name_{service.id}")
            service.description = request.POST.get(f"description_{service.id}")
            service.price = request.POST.get(f"price_{service.id}")
            service.save()

    return redirect('payments_admin')

#-------------NOTIFICATIONS-----------------------





def payments_admin(request):
    payments = Payment.objects.all().order_by('-created_at')
    services = Service.objects.prefetch_related('images').all().order_by('name')
    qr = GcashQR.objects.first()

    if request.method == "POST":
        image = request.FILES.get("image")
        instructions = request.POST.get("instructions", "")

        if qr:
            if image:
                qr.image = image
            qr.instructions = instructions
            qr.save()
        elif image:
            qr = GcashQR.objects.create(image=image, instructions=instructions)

        return redirect("payments_admin")

    return render(request, "admin/payments_admin.html", {
        "payments": payments,
        "services": services,
        "qr": qr,
        "pending_payments": Payment.objects.filter(status="pending").count(),
        "paid_payments": Payment.objects.filter(status="verified").count(),
    })

def verify_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    payment.status = "verified"
    payment.save()

    appointment = payment.appointment
    appointment.payment_status = "Paid"
    appointment.save(update_fields=["payment_status"])

    return redirect("payments_admin")

def reject_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    payment.status = "rejected"
    payment.save()

    appointment = payment.appointment
    appointment.payment_status = "Unpaid"
    appointment.save(update_fields=["payment_status"])

    return redirect("payments_admin")

def gcash_qr(request):
    qr = GcashQR.objects.first()

    if request.method == "POST":
        image = request.FILES.get("image")
        instructions = request.POST.get("instructions")

        if qr:
            if image:
                qr.image = image
            qr.instructions = instructions
            qr.save()
        else:
            GcashQR.objects.create(image=image, instructions=instructions)

        return redirect("gcash_qr")

    return render(request, "admin/gcash_qr.html", {
        "qr": qr
    })

def email_notification(request):
    if request.method == "POST":
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        return redirect("email_notification")

    return render(request, "admin/email_notification.html")

def reports_admin(request):

    today = date.today()

    # 📌 Appointment Stats
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status="Pending").count()
    completed_appointments = Appointment.objects.filter(status="Approved").count()

    # 📌 Clients & Pets
    total_clients = User.objects.filter(is_staff=False).count()
    total_pets = Pet.objects.filter(is_active=True).count()

    context = {
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
        "total_clients": total_clients,
        "total_pets": total_pets,
    }

    return render(request, "admin/reports_admin.html", context)


def settings_admin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        messages.success(request, "Email notification sent.")
        return redirect("settings_admin")

    context = {
        "total_appointments": Appointment.objects.count(),
        "pending_appointments": Appointment.objects.filter(status="Pending").count(),
        "completed_appointments": Appointment.objects.filter(status="Approved").count(),
        "total_clients": User.objects.filter(is_staff=False).count(),
        "total_pets": Pet.objects.filter(is_active=True).count(),
    }

    return render(request, "admin/settings_admin.html", context)


@login_required(login_url='login')
def vaccination_reminders_admin(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access only.")

    today = timezone.localdate()
    reminder_days = 30
    due_until = today + timedelta(days=reminder_days)

    vaccines = list(
        Vaccine.objects.filter(
            next_due__isnull=False,
            pet__isnull=False,
            pet__owner__is_staff=False,
            next_due__lte=due_until,
        )
        .exclude(pet__owner__email="")
        .select_related('pet', 'pet__owner')
        .prefetch_related('reminder_logs')
        .order_by('next_due', 'pet__name')
    )

    overdue_count = 0
    due_today_count = 0
    due_soon_count = 0

    for vaccine in vaccines:
        reminder_logs = list(vaccine.reminder_logs.all())
        vaccine.days_until_due = (vaccine.next_due - today).days
        vaccine.last_reminder = reminder_logs[0] if reminder_logs else None

        if vaccine.days_until_due < 0:
            vaccine.due_label = "Overdue"
            vaccine.due_class = "overdue"
            overdue_count += 1
        elif vaccine.days_until_due == 0:
            vaccine.due_label = "Due today"
            vaccine.due_class = "today"
            due_today_count += 1
        else:
            vaccine.due_label = f"Due in {vaccine.days_until_due} day{'s' if vaccine.days_until_due != 1 else ''}"
            vaccine.due_class = "soon"
            due_soon_count += 1

    context = {
        "vaccines": vaccines,
        "reminder_days": reminder_days,
        "overdue_count": overdue_count,
        "due_today_count": due_today_count,
        "due_soon_count": due_soon_count,
        "smtp_ready": bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD),
    }
    return render(request, "admin/vaccination_reminders.html", context)


@require_POST
@login_required(login_url='login')
def send_vaccination_reminder(request, vaccine_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access only.")

    vaccine = get_object_or_404(
        Vaccine.objects.select_related('pet', 'pet__owner'),
        id=vaccine_id,
        pet__isnull=False,
    )
    owner = vaccine.pet.owner

    if not owner.email:
        messages.error(request, f"{owner.username} has no email address on file.")
        return redirect("vaccination_reminders_admin")

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        messages.error(request, "SMTP credentials are missing. Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD before sending reminders.")
        return redirect("vaccination_reminders_admin")

    subject = f"Vaccination Reminder for {vaccine.pet.name}"
    due_date = vaccine.next_due.strftime("%B %d, %Y") if vaccine.next_due else "soon"
    message = f"""Hi {owner.get_full_name() or owner.username},

This is a friendly reminder from MFC Pet Life Veterinary Clinic.

{vaccine.pet.name}'s {vaccine.vaccine_name} vaccination is due on {due_date}.

Please contact the clinic or log in to your account to arrange the next visit.

Thank you,
MFC Pet Life Veterinary Clinic
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [owner.email],
            fail_silently=False
        )
    except Exception as error:
        messages.error(request, f"Reminder could not be sent: {error}")
        return redirect("vaccination_reminders_admin")

    VaccinationReminderLog.objects.create(
        vaccine=vaccine,
        sent_to=owner.email,
        sent_by=request.user,
        subject=subject,
    )
    messages.success(request, f"Vaccination reminder sent to {owner.email}.")
    return redirect("vaccination_reminders_admin")
