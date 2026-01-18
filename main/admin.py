from django.contrib import admin
from .models import Pet, Owner, Vaccination, Appointment, VetAvailability
from django.forms import ModelForm, TimeInput
from django.forms import TimeInput

# 🕒 Custom form for VetAvailability to use HTML5 time input
# Vet Availability Admin
# -------------------------------
class VetAvailabilityForm(ModelForm):
    class Meta:
        model = VetAvailability
        fields = '__all__'
        widgets = {
            'start_time': TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

@admin.register(VetAvailability)
class VetAvailabilityAdmin(admin.ModelAdmin):
    form = VetAvailabilityForm
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'available')
    list_filter = ('doctor', 'date', 'available')
    search_fields = ('doctor__username',)
    ordering = ('date', 'start_time')
    list_editable = ('available',)

# -------------------------------
# Pet Admin
# -------------------------------
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'owner', 'age', 'gender', 'color', 'weight')
    list_filter = ('species', 'gender')
    search_fields = ('name', 'owner__username')
    ordering = ('name',)
    fields = ('owner', 'name', 'species', 'breed', 'gender', 'color', 'birthday', 'weight', 'image', 'is_active')

# -------------------------------
# Vaccination Admin
# -------------------------------
@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ('pet', 'vaccine_name', 'date_given', 'next_due', 'weight', 'manufacturer', 'veterinarian')
    search_fields = ('pet__name', 'vaccine_name', 'manufacturer', 'veterinarian')
    list_filter = ('date_given', 'next_due')

# -------------------------------
# Appointment Admin
# -------------------------------

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'user', 'appointment_type', 'date', 'time', 'status', 'notes')
    list_filter = ('date', 'status', 'appointment_type')
    search_fields = ('pet__name', 'user__username')
    ordering = ('-date', 'time')
    readonly_fields = ('date', 'time')
