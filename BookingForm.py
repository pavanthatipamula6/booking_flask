from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['parking_slot']  # Add other fields as needed for booking

    def clean(self):
        cleaned_data = super().clean()
        # Add validation or custom logic if needed for the booking form
        return cleaned_data
