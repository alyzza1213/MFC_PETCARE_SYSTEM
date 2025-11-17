from django.contrib import admin
from .models import Pet, VaccineRecord, VetAvailability, Appointment
from django import forms
from django.forms import TimeInput

# 🕒 Custom form for VetAvailability to use HTML5 time input
class VetAvailabilityForm(forms.ModelForm):
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

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'owner', 'age', 'gender', 'color', 'weight')
    list_filter = ('species', 'gender')
    search_fields = ('name', 'owner__username')
    ordering = ('name',)
    fields = ('owner', 'name', 'species', 'breed', 'gender', 'color', 'birthday', 'weight', 'image')

@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'vaccine_name', 'date_given', 'next_due_date', 'remarks')
    search_fields = ('pet__name', 'vaccine_name')
    list_filter = ('date_given', 'next_due_date')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'user', 'date', 'time', 'status', 'notes')
    list_filter = ('date', 'status')
    search_fields = ('pet__name', 'user__username')
    ordering = ('-date', 'time')
    readonly_fields = ('date', 'time')

