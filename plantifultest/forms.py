from django.forms import ModelForm
from django import forms
from .models import *

# class settingsForm(forms.Form):
#     class Meta:
#         model = settings
#         fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['name'].queryset = settings.objects.none()