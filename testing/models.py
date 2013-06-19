from django.db import models
from validatedfile.fields import ValidatedFileField

class TestModel(models.Model):
    the_file = ValidatedFileField(
                    null = True,
                    blank = True,
                    upload_to = 'testfile',
                    content_types = ['image/png'],
                    max_upload_size = 10240)

class TestModelNoValidate(models.Model):
    the_file = ValidatedFileField(
                    null = True,
                    blank = True,
                    upload_to = 'testfile')


class TestContainer(models.Model):
    name = models.CharField(max_length = 100)


class TestElement(models.Model):
    container = models.ForeignKey(
                    TestContainer,
                    related_name = 'test_elements')
    the_file = ValidatedFileField(
                    null = True,
                    blank = True,
                    upload_to = 'testfile',
                    content_types = ['image/png', 'image/jpeg'])

