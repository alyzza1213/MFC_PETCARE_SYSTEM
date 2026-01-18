from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta



# 👤 OWNER INFO
class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or self.user.username


# 🐶 PET MODEL
class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10)
    color = models.CharField(max_length=50, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Soft-delete flag

    def __str__(self):
        return self.name

    def calculate_age(self):
        if self.birthday:
            today = date.today()
            years = today.year - self.birthday.year
            if (today.month, today.day) < (self.birthday.month, self.birthday.day):
                years -= 1
            return years
        return self.age

# 💉 VACCINE RECORD
class Vaccination(models.Model):
    pet = models.ForeignKey(
        'Pet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vaccinations'
    )
    date_given = models.DateField()
    next_due = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    vaccine_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    veterinarian = models.CharField(max_length=100)


class Vaccine(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vaccine_records'
    )
    date_given = models.DateField()
    next_due = models.DateField(null=True, blank=True)
    weight = models.FloatField()
    vaccine_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    veterinarian = models.CharField(max_length=100, blank=True)

class VaccineRecord(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    vaccine_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    date_given = models.DateField()
    next_due = models.DateField()
    veterinarian = models.CharField(max_length=100)

# 🩺 VET AVAILABILITY
class VetAvailability(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_staff': True},
        related_name='availabilities'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = "Vet Availability"
        verbose_name_plural = "Vet Availabilities"

    def __str__(self):
        status = "Available" if self.available else "Not Available"
        return f"{self.doctor.username} - {self.date} ({self.start_time}–{self.end_time}) [{status}]"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")


class Service(models.Model):
    name = models.CharField(max_length=100)  # "Vaccination", "Grooming", etc.
    duration = models.DurationField()  # e.g., 15 mins, 1 hour
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

 
# 📅 APPOINTMENT
class Appointment(models.Model):
    APPOINTMENT_TYPES = [
        ('Vaccination', 'Vaccination'),
        ('Grooming', 'Grooming'),
        ('Check-up', 'Check-up'),
        ('Consultation', 'Consultation'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_STATUS = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # appointments remain even if pet is deleted
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )

    date = models.DateField()
    time = models.TimeField()

    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPES
    )

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # 💰 PAYMENT FIELD (THIS IS WHAT YOU NEED)
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='Unpaid'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    @property
    def duration(self):
        return timedelta(minutes=60 if self.appointment_type == 'Grooming' else 30)

    def __str__(self):
        if self.pet:
            return f"{self.pet.name} ({self.appointment_type}) - {self.date} {self.time}"
        return f"Deleted Pet ({self.appointment_type}) - {self.date} {self.time}"
    
class WorkingDay(models.Model):
    date = models.DateField(unique=True)
    is_active = models.BooleanField(default=True)   # ✅ Make sure this exists
    morning_open = models.BooleanField(default=True)
    afternoon_open = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date} ({'Active' if self.is_active else 'Inactive'})"


class History(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.pet.name if self.pet else 'Deleted Pet'}"


# 🩺 COMBINE ANG CHECKUP AND CONNSULTATION
class MedicalRecord(models.Model):
    RECORD_REASON_CHOICES = [
        ('Check-Up', 'Check-Up'),
        ('Consultation', 'Consultation'),
        ('Vaccination', 'Vaccination'),
        ('Follow-Up', 'Follow-Up'),
        ('Emergency', 'Emergency'),
    ]
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    findings = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    reason_for_visit = models.CharField(max_length=20, choices=RECORD_REASON_CHOICES)
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    



# ✂️ GROOMING RECORD
class Grooming(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.SET_NULL, null=True, blank=True, related_name='grooming_records')
    date = models.DateField()
    service_type = models.CharField(max_length=100)  # e.g., "Bath", "Haircut"
    notes = models.TextField(blank=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': True})

    def __str__(self):
        return f"{self.pet.name if self.pet else 'Deleted Pet'} - {self.service_type} on {self.date}"
