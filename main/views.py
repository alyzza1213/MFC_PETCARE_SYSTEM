from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from .models import Pet, Owner, VaccineRecord, Appointment, VetAvailability


# --------------------------
# User Views
# --------------------------

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

# --------------------------
# User Views
# --------------------------

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Redirect admin/staff to admin dashboard
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            # Redirect normal users to homepage
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# --------------------------
# Pet Views
# --------------------------

def pet_profile(request):
    pets = Pet.objects.filter(owner=request.user)
    for pet in pets:
        pet.years = pet.age // 12
        pet.months = pet.age % 12
    return render(request, 'clients/pet_profile.html', {'pets': pets})

def add_or_edit_pet(request, pet_id=None):
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
        image = request.FILES.get('image')

        age_total_months = 0
        if birthday:
            try:
                bday = timezone.datetime.strptime(birthday, '%Y-%m-%d').date()
                today = timezone.now().date()
                delta_years = today.year - bday.year
                delta_months = today.month - bday.month
                age_total_months = delta_years * 12 + delta_months
            except ValueError:
                messages.error(request, "Invalid birthday format.")
                return redirect('add_pet')

        owner, created = Owner.objects.get_or_create(user=request.user)

        if pet:
            pet.name = name
            pet.species = species
            pet.breed = breed
            pet.gender = gender
            pet.color = color
            pet.birthday = birthday
            pet.age = age_total_months
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
                image=image
            )
            messages.success(request, "Pet added successfully!")

        return redirect('pet_detail', pet_id=pet.id)

    return render(request, "clients/add_edit_pet.html", {"pet": pet})

def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    pet.years = pet.age // 12
    pet.months = pet.age % 12
    vaccines = VaccineRecord.objects.filter(pet=pet)
    return render(request, 'clients/pet_detail.html', {'pet': pet, 'vaccines': vaccines})

def vaccine_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    vaccines = VaccineRecord.objects.filter(pet=pet)
    return render(request, 'clients/vaccine_detail.html', {'pet': pet, 'vaccines': vaccines})

# Client
def pet_records(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'clients/pet_records.html', {'pets': pets})

# Admin
def pet_records_admin(request):
    pets = Pet.objects.select_related('owner').all()
    return render(request, 'admin/pet_records.html', {'pets': pets})

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
    records = VaccineRecord.objects.filter(pet__owner=request.user)
    return render (request, 'clients/vaccine_records.html', {'records': records})


# --------------------------
# Vet & Appointment Views
# --------------------------

def vet_availability(request):
    today = date.today()
    week_slots = {}
    for i in range(7):
        day = today + timedelta(days=i)
        slots = VetAvailability.objects.filter(date=day).order_by('start_time')
        week_slots[day] = slots
    return render(request, 'clients/vet_availability.html', {'week_slots': week_slots, 'today': today})

def book_appointment(request):
    pets = Pet.objects.filter(owner=request.user)
    today = timezone.now().date()
    available_slots = VetAvailability.objects.filter(date__gte=today, available=True).order_by('date', 'start_time')

    if request.method == 'POST':
        pet_id = request.POST.get('pet')
        slot_id = request.POST.get('slot')
        notes = request.POST.get('notes')

        try:
            pet = Pet.objects.get(id=pet_id, owner=request.user)
            slot = VetAvailability.objects.get(id=slot_id, available=True)
        except (Pet.DoesNotExist, VetAvailability.DoesNotExist):
            messages.error(request, 'Invalid pet or slot selection.')
            return redirect('book_appointment')

        Appointment.objects.create(
            user=request.user,
            pet=pet,
            date=slot.date,
            time=slot.start_time,
            notes=notes,
            status='Pending'
        )
        slot.available = False
        slot.save()
        messages.success(request, f'Appointment booked with Dr. {slot.doctor.username} on {slot.date} at {slot.start_time}.')
        return redirect('my_appointments')

    return render(request, 'clients/book_appointment.html', {
        'pets': pets,
        'available_slots': available_slots,
        'today': today
    })

def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'clients/my_appointments.html', {'appointments': appointments})


# --------------------------
# Admin Views
# --------------------------

def is_admin(user):
    return user.is_staff

def admin_dashboard(request):
    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_pets': Pet.objects.count(),
        'total_vaccines': VaccineRecord.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_vets': VetAvailability.objects.count(),
    }
    return render(request, 'admin/admin_dashboard.html', context)

def user_registry(request):
    # Exclude staff/admin users
    users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    return render(request, 'admin/user_registry.html', {'users': users})

def pet_records_admin(request):
    pets = Pet.objects.select_related('owner').all()
    return render(request, 'admin/pet_records.html', {'pets': pets})

def vaccine_records_admin(request):
    return render(request, 'admin/vaccine_records_admin.html')

def appointment_hub(request):
    return render(request, 'admin/appointment_hub.html')

def vet_availability_admin(request):
    today = timezone.now().date()
    vets = VetAvailability.objects.filter(date__gte=today).order_by('date', 'start_time')
    return render(request, 'admin/vet_availability_admin.html', {'vets': vets})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_registry')
