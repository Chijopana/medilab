from django import forms
from django.contrib.auth.models import User
from Perfiles.models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

