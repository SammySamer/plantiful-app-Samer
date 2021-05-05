from django.forms import ModelForm
from django import forms
from .models import settings

#class settingsForm(ModelForm):
#    class Meta:
#        model = settings
#        fields = '__all__'

Sensors= [
    ('Temperature', 'Temperature'),
    ('Soil Moisture', 'Soil Moisture'),
    ('Humidity', 'Humidity'),
    ('pH', 'pH'),
 ]

class CHOICES(forms.Form):
    Sensors = forms.CharField(widget=forms.RadioSelect(choices=Sensors))

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['name'].queryset = settings.objects.none()