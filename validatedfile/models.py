from django.db import models
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext as _

import magic

class ValidatedFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 0)
        super(ValidatedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):        
        data = super(ValidatedFileField, self).clean(*args, **kwargs)

        if self.content_types:
            file = data.file
            content_type_headers = getattr(file, 'content_type', '')

            mg = magic.Magic(mime = True)
            content_type_magic = mg.from_buffer(file.read(1024))
            file.seek(0)

            if not content_type_headers in self.content_types or not content_type_magic in self.content_types:
                raise forms.ValidationError(_('Filetype %s not supported.') % (file.content_type))

        if self.max_upload_size:
            if file._size > self.max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') %
                                            (filesizeformat(self.max_upload_size), filesizeformat(file._size)))

        return data

