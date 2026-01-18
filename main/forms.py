from django import forms
from .models import Vaccination, Pet



class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['pet', 'vaccine_name', 'date_given', 'next_due', 'weight', 'manufacturer', 'veterinarian']
        widgets = {
            'date_given': forms.DateInput(attrs={'type': 'date'}),
            'next_due': forms.DateInput(attrs={'type': 'date'}),
        }

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species', 'breed', 'gender', 'birthday', 'weight', 'owner', 'image']

class VaccineForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = [
            'pet',
            'date_given',
            'next_due',
            'weight',
            'vaccine_name',
            'manufacturer',
            'veterinarian'
        ]
        widgets = {
            'date_given': forms.DateInput(attrs={'type': 'date'}),
            'next_due': forms.DateInput(attrs={'type': 'date'}),
        }
