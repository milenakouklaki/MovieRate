from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'bio']


class RatingForm(forms.Form):
    rating = forms.DecimalField(min_value=1, max_value=5, decimal_places=1, required=True)