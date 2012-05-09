from django.test import TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

import os.path

from validatedfile.models import FileQuota

from models import TestModel, TestModelNoValidate, TestContainer, TestElement
from forms import TestModelForm, TestModelNoValidateForm, TestElementForm

class ValidatedFileFieldTest(TestCase):

    SAMPLE_FILES_PATH = 'validatedfile/tests/sample_files'


    def test_create_empty_instance(self):
        instance = TestModel.objects.create()


    def test_create_instance_with_file(self):
        instance = TestModel.objects.create(
                the_file = File(self._get_sample_file('image2k.png'), 'the_file.png')
            )

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()


    def test_form_ok(self):
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


    def test_form_invalid_size(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.png',
                content = self._get_sample_file('image15k.png').read(),
                content_type = 'image/png',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)


    def test_form_invalid_filetype(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.pdf',
                content = self._get_sample_file('document1k.pdf').read(),
                content_type = 'application/pdf',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)


    def test_form_invalid_filetype_and_size(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.pdf',
                content = self._get_sample_file('document15k.pdf').read(),
                content_type = 'application/pdf',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)


    def test_form_fake_filetype(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.png',
                content = self._get_sample_file('document1k.pdf').read(),
                content_type = 'image/png',
            )
        form = TestModelForm(data = {}, files = {'the_file': uploaded_file})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)


    def test_form_no_validate(self):
        uploaded_file = SimpleUploadedFile(
                name = 'the_file.pdf',
                content = self._get_sample_file('document15k.pdf').read(),
                content_type = 'application/pdf',
            )
        form = TestModelNoValidateForm(data = {}, files = {'the_file': uploaded_file})
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.pdf')

        instance.the_file.delete()
        instance.delete()


    def test_form_null_file(self):
        form = TestModelNoValidateForm(data = {}, files = {})
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertEqual(instance.the_file, None)

        instance.delete()


    def test_quota_empty(self):
        container = TestContainer.objects.create(name = 'container1')

        quota = FileQuota()
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 0)
        self.assertFalse(quota.exceeds())

        container.delete()


    def test_quota_one_file(self):
        container = TestContainer.objects.create(name = 'container1')
        element = TestElement.objects.create(
                container = container,
                the_file = File(self._get_sample_file('image2k.png'), 'the_file.png')
            )

        quota = FileQuota()
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 2120)
        self.assertFalse(quota.exceeds())

        element.the_file.delete()
        element.delete()
        container.delete()


    def test_quota_several_files_several_containers(self):
        container1 = TestContainer.objects.create(name = 'container1')
        element1 = TestElement.objects.create(
                container = container1,
                the_file = File(self._get_sample_file('image2k.png'), 'the_file1.png')
            )
        element2 = TestElement.objects.create(
                container = container1,
                the_file = File(self._get_sample_file('image15k.png'), 'the_file2.png')
            )
        container2 = TestContainer.objects.create(name = 'container2')
        element3 = TestElement.objects.create(
                container = container2,
                the_file = File(self._get_sample_file('document15k.pdf'), 'the_file3.pdf')
            )

        quota = FileQuota(max_usage = 20000)
        quota.update(container1.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 16706)
        self.assertFalse(quota.exceeds())

        element1.the_file.delete()
        element2.the_file.delete()
        element3.the_file.delete()
        element1.delete()
        element2.delete()
        element3.delete()
        container1.delete()
        container2.delete()


    def test_quota_exceeds(self):
        quota = FileQuota(max_usage = 1000)

        container = TestContainer.objects.create(name = 'container1')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 0)
        self.assertFalse(quota.exceeds())
        self.assertTrue(quota.exceeds(2120))

        element = TestElement.objects.create(
                container = container,
                the_file = File(self._get_sample_file('image2k.png'), 'the_file.png')
            )
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 2120)
        self.assertTrue(quota.exceeds())

        element.the_file.delete()
        element.delete()
        container.delete()


    def test_form_quota_check(self):
        container = TestContainer.objects.create(name = 'container1')

        form1 = TestElementForm(container = container)
        self.assertFalse(form1.exceeds_quota())

        element = TestElement.objects.create(
                container = container,
                the_file = File(self._get_sample_file('image15k.png'), 'the_file.png')
            )

        form2 = TestElementForm(container = container)
        self.assertTrue(form2.exceeds_quota())

        element.the_file.delete()
        element.delete()
        container.delete()


    def test_form_quota_ok(self):
        container = TestContainer.objects.create(name = 'container1')

        uploaded_file = SimpleUploadedFile(
                name = 'the_file.png',
                content = self._get_sample_file('image2k.png').read(),
                content_type = 'image/png',
            )
        form = TestElementForm(
                container = container,
                data = {},
                files = {'the_file': uploaded_file}
            )

        self.assertTrue(form.is_valid())

        container.delete()


    def test_form_quota_exceeded(self):
        container = TestContainer.objects.create(name = 'container1')
        element = TestElement.objects.create(
                container = container,
                the_file = File(self._get_sample_file('image2k.png'), 'the_file.png')
            )

        uploaded_file = SimpleUploadedFile(
                name = 'the_file.png',
                content = self._get_sample_file('image15k.png').read(),
                content_type = 'image/png',
            )
        form = TestElementForm(
                container = container,
                data = {},
                files = {'the_file': uploaded_file}
            )

        self.assertFalse(form.is_valid())

        element.the_file.delete()
        element.delete()
        container.delete()


    # Utilities

    def _get_sample_file(self, filename):
        path = os.path.join(self.SAMPLE_FILES_PATH, filename)
        return open(path)


    def _check_file_url(self, filefield, filename):
        url = os.path.join(settings.MEDIA_URL, filefield.field.upload_to, filename)
        self.assertEqual(filefield.url, url)

        
    def _get_file_url(self, filename):
        return os.path.join(MEDIA_ROOT, prefix, filename)

