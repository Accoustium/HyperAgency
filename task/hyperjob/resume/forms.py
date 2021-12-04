from django import forms
from django.contrib.auth.models import User


class resumeForm(forms.Form):
    description = forms.CharField(max_length=1024)
