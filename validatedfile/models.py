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
        file = data.file

        if self.content_types:
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


class FileQuota(object):

    def __init__(self, max_usage = -1):
        self.current_usage = 0
        self.max_usage = max_usage

    def update(self, items, attr_name):
        self.current_usage = 0
        for item in items:
            the_file = getattr(item, attr_name, None)
            if the_file:
                self.current_usage += the_file.size

    def exceeds(self, size = 0):
        if self.max_usage >= 0:
            return (self.current_usage + size > self.max_usage)
        else:
            return False


class QuotaValidator(object):

    def __init__(self, max_usage):
        self.quota = FileQuota(max_usage)

    def update_quota(self, items, attr_name):
        self.quota.update(items, attr_name)

    def __call__(self, file):
        file_size = file.size
        if self.quota.exceeds(file_size):
            raise forms.ValidationError(_('Please keep the total uploaded files under %s. With this file, the total would be %s' %
                                   (filesizeformat(self.quota.max_usage),
                                    filesizeformat(self.quota.current_usage + file_size))))
 

#
#
#    def __init__(self, items = [], file_attr_name = None):
#        self.items = items
#        self.file_attr_name = file_attr_name
#
#    def current_usage(self):
#        usage = 0
#        for item in self.items:
#            the_file = getattr(item, self.file_attr_name, None)
#            if the_file:
#                usage += the_file.size
#        return usage
#
#class QuotaValidator(object):
#    def __init__(self, max_usage):
#        self.quota = FileQuota()
#        self.max_usage = max_usage
#
#    def set_quota(self, quota):
#        self.quota = quota
#
#    def __call__(self, file):
#        tried_usage = self.quota.current_usage() + file.size
#        if tried_usage > self.max_usage:
#            raise forms.ValidationError(_('Please keep the total uploaded files under %s. With this file, the total would be %s' %
#                                   (filesizeformat(self.max_usage), filesizeformat(tried_usage))))
#        
