from django import forms
from models import TestModel, TestModelNoValidate, TestContainer, TestElement
from validatedfile.models import QuotaValidator

class TestModelForm(forms.ModelForm):
    
    class Meta:
        model = TestModel


class TestModelNoValidateForm(forms.ModelForm):
    
    class Meta:
        model = TestModelNoValidate


class TestElementForm(forms.ModelForm):

    the_file = forms.FileField(required = False,
                    validators = [QuotaValidator(max_usage = 10000)])

    class Meta:
        model = TestElement
        fields = ['the_file']

    def __init__(self, container, quota, *args, **kwargs):
        super(TestElementForm, self).__init__(*args, **kwargs)
        self.container = container
        self.fields['the_file'].validators[0].set_quota(quota)

    def save(self, *args, **kwargs):
        element = super(TestElementForm, self).save(commit = False)
        element.container = self.container
        element.save()

