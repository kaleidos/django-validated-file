from django.test import TestCase

from models import TestModel

class ValidatedFileFieldTest(TestCase):

    def test_create_instance(self):
        instance = TestModel()
        instance.save()

