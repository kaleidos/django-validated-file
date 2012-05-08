from django import forms
from models import TestModel, TestModelNoValidate

class TestModelForm(forms.ModelForm):
    
    class Meta:
        model = TestModel

class TestModelNoValidateForm(forms.ModelForm):
    
    class Meta:
        model = TestModelNoValidate

