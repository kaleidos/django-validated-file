from django.db import models
from validatedfile.models import ValidatedFileField
from ..models import *

class TestModel(models.Model):
    the_file = ValidatedFileField(upload_to = 'testfile')

