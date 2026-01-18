from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import VaccinationForm
from django.contrib import messages
from calendar import monthrange
from django.utils import timezone
from collections import defaultdict
from django.http import JsonResponse
from datetime import date, datetime, time, timedelta
from django.contrib.auth.models import User
from .models import Pet, Owner, Vaccination, Service, WorkingDay, Appointment, VetAvailability, History, VaccineRecord, Vaccine
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PetForm, VaccinationForm, VaccineForm
from django.contrib.admin.views.decorators import staff_member_required
import calendar
from decimal import Decimal




# USER VIEWS NI SIYA HA

def landing_page(request):
    return render(request, 'main/homepage.html') 

def homepage(request):
    return render(request, 'main/homepage.html')

def index(request):
    return render(request, 'main/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    return render(request, 'main/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard' if user.is_staff else 'homepage')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# USER PET VIEWS

def pet_profile(request):
    pets = Pet.objects.filter(owner=request.user)
    for pet in pets:
        pet.years = pet.age // 12
        pet.months = pet.age % 12
    return render(request, 'clients/pet_profile.html', {'pets': pets})


def add_or_edit_pet_user(request, pet_id=None):
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

def vet_availability(request):
    today = date.today()
    year = today.year
    month = today.month
    num_days = monthrange(year, month)[1]

    month_days = []

    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)
        working_day, _ = WorkingDay.objects.get_or_create(date=day_date)

        available_times = []

        # Determine if morning/afternoon are open
        sessions = []
        if working_day.morning_open:
            sessions.append((time(7, 30), time(11, 30)))
        if working_day.afternoon_open:
            sessions.append((time(13, 0), time(17, 0)))

        # Generate available slots
        for start, end in sessions:
            slot_time = datetime.combine(day_date, start)
            end_dt = datetime.combine(day_date, end)
            while slot_time < end_dt:
                if not Appointment.objects.filter(date=day_date, time=slot_time.time()).exists():
                    available_times.append(slot_time.time())
                slot_time += timedelta(minutes=30)

        # Determine status for display
        if working_day.morning_open and working_day.afternoon_open:
            status = 'Whole Day'
        elif working_day.morning_open or working_day.afternoon_open:
            status = 'Half Day'
        else:
            status = 'Closed'

        month_days.append({
            'date': day_date,
            'is_working': bool(sessions),
            'available_times': available_times,
            'status': status,
        })

    # Calculate empty days at the start for weekday alignment (Mon=0)
    first_weekday = date(year, month, 1).weekday()  # 0=Monday
    empty_days_start = range(first_weekday)

    context = {
        'month_days': month_days,
        'current_month': today,
        'empty_days_start': empty_days_start,
    }

    return render(request, 'clients/vet_availability.html', context)


def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet.years = pet.age // 12
    pet.months = pet.age % 12
    vaccines = Vaccination.objects.filter(pet=pet)
    return render(request, 'clients/pet_detail.html', {'pet': pet, 'vaccines': vaccines})

def pet_records_user(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'clients/pet_records.html', {'pets': pets})


def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet.delete()
    messages.success(request, f"{pet.name} has been deleted.")
    return redirect('pet_profile')

def update_pet_image(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST' and request.FILES.get('image'):
        pet.image = request.FILES['image']
        pet.save()
        return JsonResponse({'status': 'success', 'image_url': pet.image.url})
    return JsonResponse({'status': 'error'}, status=400)



def vaccine_records(request):
    records = Vaccination.objects.filter(pet__owner=request.user)
    return render(request, 'clients/vaccine_records.html', {'records': records})

def vaccine_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    vaccines = Vaccination.objects.filter(pet=pet)
    return render(request, 'clients/vaccine_detail.html', {'pet': pet, 'vaccines': vaccines})

SERVICE_DURATION = {
    "Consultation": 30,
    "Check-up": 30,
    "Vaccination": 30,
    "Grooming": 60,
}

def book_appointment(request):
    user = request.user
    pets = Pet.objects.filter(owner=user)
    qr_code_url = None

    # Clinic hours
    morning_start = time(7, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(17, 0)

    # Get today's appointments
    today = datetime.today().date()
    todays_appts = Appointment.objects.filter(date=today).order_by('time')

    # Track next available time
    next_time = morning_start
    if todays_appts.exists():
        last_appt = todays_appts.last()
        if last_appt.time < morning_end:
            next_time_dt = datetime.combine(today, last_appt.time) + last_appt.duration
            next_time = next_time_dt.time()
            if next_time >= morning_end:
                next_time = afternoon_start
        else:
            next_time = afternoon_start

    # Ensure we don't exceed afternoon_end
    if next_time >= afternoon_end:
        next_time = None  # no slots available today

    if request.method == "POST":
        selected_pets = request.POST.getlist("selected_pets")
        notes = request.POST.get("notes", "")

        for pet_id in selected_pets:
            pet = Pet.objects.get(id=pet_id)
            service_type = request.POST.get(f"service_{pet_id}", "Check-up")
            service_duration = timedelta(minutes=60 if service_type=="Grooming" else 30)

            # Save appointment
            if next_time:
                Appointment.objects.create(
                    user=user,
                    pet=pet,
                    date=today,
                    time=next_time,
                    appointment_type=service_type,
                    notes=notes,
                    status="Pending"
                )
                # increment next available time
                next_dt = datetime.combine(today, next_time) + service_duration
                if next_dt.time() < morning_end:
                    next_time = next_dt.time()
                elif next_dt.time() >= morning_end and next_dt.time() < afternoon_end:
                    next_time = max(afternoon_start, next_dt.time())
                else:
                    next_time = None

        # Show success message and redirect to home
        messages.success(request, "Your appointment has been successfully booked!")
        return redirect("homepage")  # <-- make sure this matches your home URL name

    context = {
        "pets": pets,
        "available_slots": [next_time] if next_time else [],
        "qr_code_url": qr_code_url,
    }
    return render(request, "clients/book_appointment.html", context)


def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'clients/my_appointments.html', {'appointments': appointments})

def add_pet(request):
    if request.method == "POST":
        name = request.POST.get("name")
        species = request.POST.get("species")
        breed = request.POST.get("breed")
        gender = request.POST.get("gender")
        color = request.POST.get("color")
        birthday = request.POST.get("birthday")  # format: 'YYYY-MM-DD'
        weight = request.POST.get("weight")
        # optional: convert weight to Decimal if not empty
        weight = Decimal(weight) if weight else None

        Pet.objects.create(
            name=name,
            species=species,
            breed=breed,
            gender=gender,
            color=color,
            birthday=birthday if birthday else None,
            weight=weight,
            owner=request.user
        )
        return redirect('pet_profile')  # adjust as needed

    return render(request, 'clients/add_edit_pet.html')


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

def update_pet_image(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == "POST" and request.FILES.get("image"):
        pet.image = request.FILES["image"]
        pet.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})










# --------------------------
# ADMIN PET VIEWS
# --------------------------



def add_or_edit_pet_admin(request, pet_id=None):
    pet = None
    if pet_id:
        pet = get_object_or_404(Pet, id=pet_id)
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

        age_total_months = 0
        if birthday:
            try:
                bday = timezone.datetime.strptime(birthday, '%Y-%m-%d').date()
                today = timezone.now().date()
                age_total_months = (today.year - bday.year) * 12 + (today.month - bday.month)
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
            pet.birthday = birthday
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
                birthday=birthday,
                age=age_total_months,
                weight=weight if weight else None,
                image=image
            )
            messages.success(request, "Pet added successfully!")

        return redirect('pet_records_admin')

    owners = User.objects.filter(is_staff=False)
    return render(request, "admin/add_edit_pet_admin.html", {"pet": pet, "owners": owners})

def admin_calendar(request):
    # Get current month (you can change this to dynamic month switching later)
    today = date.today()
    current_month = date(today.year, today.month, 1)

    year = current_month.year
    month = current_month.month

    # Get first weekday and number of days in the month
    # first_weekday: Monday = 0, Sunday = 6
    first_weekday, total_days = calendar.monthrange(year, month)

    # List of all days in month
    month_days = []
    for day in range(1, total_days + 1):
        d = date(year, month, day)

        working_day = WorkingDay.objects.filter(date=d).first()

        month_days.append({
            "date": d,
            "status": working_day.status if working_day else None,
            "is_working": False if (working_day and working_day.status == "closed") else True
        })

    # EMPTY CELLS BEFORE THE 1ST
    empty_days_start = list(range(first_weekday))

    # EMPTY CELLS AFTER LAST DAY (to complete final row)
    total_cells = first_weekday + total_days
    remainder = total_cells % 7
    empty_days_end = [] if remainder == 0 else list(range(7 - remainder))

    context = {
        "current_month": current_month,
        "month_days": month_days,
        "empty_days_start": empty_days_start,
        "empty_days_end": empty_days_end,
    }

    return render(request, "admin_calendar.html", context)


def admin_dashboard(request):
    # Registered Clients
    total_users = Owner.objects.count()

    # Total pets (only active ones if you want)
    total_pets = Pet.objects.filter(is_active=True).count()

    # Vaccine records: include all pets, even restored
    total_vaccines = Vaccination.objects.count()

    # Appointments: include all, even restored or soft-deleted pets
    total_appointments = Appointment.objects.count()

    # Vet schedules
    total_vets = VetAvailability.objects.count()

    context = {
        'total_users': total_users,
        'total_pets': total_pets,
        'total_vaccines': total_vaccines,
        'total_appointments': total_appointments,
        'total_vets': total_vets,
    }

    return render(request, 'admin/dashboard.html', context)

def clients_list(request):
    clients = User.objects.filter(is_staff=False)
    return render(request, 'admin/clients_list.html', {'clients': clients})

def client_detail(request, client_id):
    client = get_object_or_404(User, id=client_id)
    pets = Pet.objects.filter(owner=client, is_active=True)
    return render(request, "admin/client_detail.html", {"client": client, "pets": pets})

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

def pet_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    context = {
        'pet': pet
    }
    return render(request, 'admin/pet_detail_admin.html', context)

def clients_pets(request):
    # Only regular users (clients)
    clients = User.objects.filter(is_staff=False)
    
    # Prefetch pets to reduce DB hits
    for client in clients:
        client.pets = Pet.objects.filter(owner=client)
        for pet in client.pets:
            pet.years = pet.age // 12
            pet.months = pet.age % 12

    return render(request, 'admin/clients_pets.html', {'clients': clients})

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

def view_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, 'clients/view_pet.html', {'pet': pet})


# Soft-delete / remove pet
@staff_member_required(login_url='login')
def remove_pet_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.is_active = False
    pet.save()
    return redirect('removed_pets_admin')

# Removed pets list
@staff_member_required(login_url='login')
def removed_pets_admin(request):
    removed_pets = Pet.objects.filter(is_active=False)
    return render(request, 'admin/removed_pets_admin.html', {'removed_pets': removed_pets})

@staff_member_required(login_url='login')
def restore_pet_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.is_active = True
    pet.save()
    return redirect('removed_pets_admin')


# Permanently delete pet
@staff_member_required(login_url='login')
def delete_pet_permanent(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.delete()
    return redirect('removed_pets_admin')

def delete_pet(request, pet_id):
    # Include all pets, even soft-deleted
    pet = get_object_or_404(Pet.objects.all(), id=pet_id)
    pet.delete()  # permanently deletes
    return redirect('removed_pets_admin')




def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()  # permanently deletes user
    return redirect('clients_pets') 

# List all pets (no pet_id)
def pet_records_admin(request):
    pets = Pet.objects.select_related('owner').all()
    return render(request, 'admin/pet_records_admin.html', {'pets': pets})

# View single pet record (requires pet_id)
def pet_record_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, 'admin/pet_record_detail_admin.html', {'pet': pet})

def vaccine_records_admin(request):
    pets = Pet.objects.all()  # fetch fresh data
    return render(request, 'admin/vaccine_records_admin.html', {'pets': pets})

def add_vaccine(request, pet_id):
    if request.method == "POST":
        pet = get_object_or_404(Pet, id=pet_id)
        Vaccine.objects.create(
            pet=pet,
            date_given=request.POST['date_given'],
            next_due=request.POST.get('next_due'),
            weight=request.POST['weight'],
            vaccine_name=request.POST['vaccine_name'],
            manufacturer=request.POST.get('manufacturer', ''),
            veterinarian=request.POST.get('veterinarian', '')
        )
    return redirect('vaccine_records_admin')

    
def vaccine_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    records = Vaccination.objects.filter(pet=pet).order_by('date_given')
    return render(request, 'admin/vaccine_detail_admin.html', {'pet': pet, 'records': records})

def appointment_list(request):
    # Clinic hours
    MORNING_START = time(7, 30)
    MORNING_END = time(11, 30)
    AFTERNOON_START = time(13, 0)
    AFTERNOON_END = time(17, 0)

    # Fetch all appointments ordered by date, id
    appointments = Appointment.objects.all().order_by('date', 'id')

    day_appointments = defaultdict(list)
    next_time_per_day = {}

    for appt in appointments:
        # Ensure duration is a timedelta
        service_duration = getattr(appt, 'duration', timedelta(minutes=30))
        if not isinstance(service_duration, timedelta):
            service_duration = timedelta(minutes=30)

        appt_date = appt.date

        # Initialize next available time for the day
        if appt_date not in next_time_per_day:
            next_time_per_day[appt_date] = MORNING_START

        current_time = next_time_per_day[appt_date]

        # Move to afternoon if morning exceeded
        if current_time >= MORNING_END:
            current_time = AFTERNOON_START

        # Skip if afternoon exceeded
        if current_time >= AFTERNOON_END:
            appt.time = None
            day_appointments[appt_date].append(appt)
            continue

        # Assign time if not already set
        if not appt.time:
            appt.time = current_time
            appt.save()

        day_appointments[appt_date].append(appt)

        # Increment next available time for the day
        next_dt = datetime.combine(appt_date, current_time) + service_duration
        next_time_per_day[appt_date] = next_dt.time()

    # Sort days
    sorted_day_appointments = dict(sorted(day_appointments.items()))

    context = {
        'day_appointments': sorted_day_appointments
    }
    return render(request, "admin/appointment_list.html", context)

def appointment_update_status(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Approved", "Rejected"]:
            appt.status = new_status
            appt.save()

    return redirect('appointment_list')


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




def vet_availability_admin(request):
    today = date.today()
    year = today.year
    month = today.month

    # Number of days in the month
    num_days = monthrange(year, month)[1]

    month_days = []
    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)

        # Get or create working day
        working_day, created = WorkingDay.objects.get_or_create(date=day_date)

        # Get appointments
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

def admin_dashboard(request):
    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_pets': Pet.objects.count(),
        'total_vaccines': Vaccination.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_vets': User.objects.filter(is_staff=True).count(),
    }
    return render(request, 'admin/admin_dashboard.html', context)


def pet_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    vaccinations = pet.vaccinerecord_set.all()
    appointments = pet.appointment_set.all()
    context = {
        'pet': pet,
        'vaccinations': vaccinations,
        'appointments': appointments
    }
    return render(request, 'admin/pet_detail_admin.html', context)

def pet_records_admin(request):
    pets = Pet.objects.select_related('owner').all()  # ensures owner info is loaded
    return render(request, 'admin/pet_records_admin.html', {'pets': pets})

def pet_detail_admin(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == "POST":
        # Update fields safely
        pet.name = request.POST.get("name", pet.name).strip()
        pet.species = request.POST.get("species", pet.species).strip()
        pet.breed = request.POST.get("breed", pet.breed).strip()
        pet.gender = request.POST.get("gender", pet.gender)
        pet.birthday = request.POST.get("birthday") or pet.birthday

        # Handle weight safely
        weight = request.POST.get("weight")
        if weight:  
            try:
                pet.weight = float(weight)
            except ValueError:
                messages.error(request, "Weight must be a valid number.")
                return render(request, 'admin/pet_detail_admin.html', {'pet': pet})
        else:
            pet.weight = None  # Optional: leave unchanged if needed

        try:
            pet.save()
            messages.success(request, "Pet info updated successfully!")
        except Exception as e:
            messages.error(request, f"Error saving pet: {e}")
            return render(request, 'admin/pet_detail_admin.html', {'pet': pet})

        # Redirect back to a specific page (e.g., pet list or admin dashboard)
        return redirect('pet_records_admin')  # change to your list/admin URL name

    return render(request, 'admin/pet_detail_admin.html', {'pet': pet})


def find_next_available_time(day_date, total_duration):
    sessions = [
        (time(7,30), time(11,30)),  # Morning
        (time(13,0), time(17,0))    # Afternoon
    ]

    # Existing appointments
    appointments = Appointment.objects.filter(
        date=day_date,
        status__in=['Pending','Approved']
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
            overlaps = any(current < b_end and slot_end > b_start for b_start, b_end in blocked)
            if not overlaps:
                return current.time()  # earliest available start time
            current += timedelta(minutes=5)

    return None  # no available slot


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

def edit_working_day(request, date):
    day_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get or create the working day entry
    working_day, created = WorkingDay.objects.get_or_create(date=day_date)
    
    if request.method == 'POST':
        working_day.morning_open = 'morning_open' in request.POST
        working_day.afternoon_open = 'afternoon_open' in request.POST
        working_day.save()  # ✅ Save changes to DB so client side sees it
        return redirect('vet_availability_admin')
    
    context = {
        'day_date': day_date,
        'morning_open': working_day.morning_open,
        'afternoon_open': working_day.afternoon_open,
    }
    return render(request, 'admin/edit_working_day.html', context)

# --------------------------
# OTHER ADMIN AND USER VIEWS
# --------------------------

# ... keep all your previous functions (dashboard, delete_user, vaccine_records_admin, etc.)
