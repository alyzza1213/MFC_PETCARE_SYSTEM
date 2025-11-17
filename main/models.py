from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # or link to Owner if you prefer
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10)
    color = models.CharField(max_length=50, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='pets/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def calculate_age(self):
        """Automatically calculate age from birthday if available"""
        if self.birthday:
            today = date.today()
            years = today.year - self.birthday.year
            if today.month < self.birthday.month or (today.month == self.birthday.month and today.day < self.birthday.day):
                years -= 1
            return years
        return self.age


# 💉 VACCINE RECORD
class VaccineRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    date_given = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vaccine_name} - {self.pet.name}"


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


# 📅 APPOINTMENT
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.pet.name} with {self.user.username} on {self.date} at {self.time}"
