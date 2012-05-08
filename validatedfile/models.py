from django.db import models
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext as _

class ValidatedFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ValidatedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):        
        data = super(ValidatedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype %s not supported.') % (file.content_type))
        except AttributeError:
            pass        

        return data
