from django.test import TestCase
from django.core.files import File

from models import TestModel

class ValidatedFileFieldTest(TestCase):

    def test_create_empty_instance(self):
        instance = TestModel.objects.create()
        instance.save()

    def test_create_instance_with_file(self):
        instance = TestModel.objects.create(
                the_file = File(open('validatedfile/tests/image2k.png'), 'the_file.png')
            )
        instance.save()

        self.assertEqual(instance.the_file.url, '/media/testfile/the_file.png')

        instance.the_file.delete()
        instance.delete()

