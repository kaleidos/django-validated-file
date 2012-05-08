from django.test import TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

import os.path

from models import TestModel
from forms import TestModelForm

class ValidatedFileFieldTest(TestCase):

    SAMPLE_FILES_PATH = 'validatedfile/tests/sample_files'


    def _get_sample_file(self, filename):
        path = os.path.join(self.SAMPLE_FILES_PATH, filename)
        return open(path)


    def _check_file_url(self, filefield, filename):
        url = os.path.join(settings.MEDIA_URL, filefield.field.upload_to, filename)
        self.assertEqual(filefield.url, url)

        
    def _get_file_url(self, filename):
        return os.path.join(MEDIA_ROOT, prefix, filename)


    def test_create_empty_instance(self):
        instance = TestModel.objects.create()
        instance.save()


    def test_create_instance_with_file(self):
        instance = TestModel.objects.create(
                the_file = File(self._get_sample_file('image2k.png'), 'the_file.png')
            )
        instance.save()

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()


    def test_form(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.png',
                content = self._get_sample_file('image2k.png').read(),
                content_type = 'image/png',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()


    def test_form_invalid_filetype(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.pdf',
                content = self._get_sample_file('document.pdf').read(),
                content_type = 'apllication/pdf',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)


    def test_form_invalid_size(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.pdf',
                content = self._get_sample_file('image15k.png').read(),
                content_type = 'image/png',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)

