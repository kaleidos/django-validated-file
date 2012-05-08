from django import forms
from models import TestModel

class TestModelForm(forms.ModelForm):
    
    class Meta:
        model = TestModel

