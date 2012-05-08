from django.db import models
from validatedfile.models import ValidatedFileField
from ..models import *

class TestModel(models.Model):
    the_file = ValidatedFileField(
                    null = True,
                    blank = True,
                    upload_to = 'testfile',
                    content_types = ['image/png'],
                    max_upload_size = 10240)

