from django.test import TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

import os.path

from validatedfile.fields import FileQuota

from testing.models import TestModel, TestModelNoValidate, TestContainer, TestElement
from testing.forms import TestModelForm, TestModelNoValidateForm, TestElementForm

class ValidatedFileFieldTest(TestCase):

    SAMPLE_FILES_PATH = 'testing/sample_files'


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
        form = self._create_bound_test_model_form(form_class = TestModelForm,
                                                  orig_filename = 'image2k.png',
                                                  dest_filename = 'the_file.png',
                                                  content_type = 'image/png')
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()

    def test_form_invalid_size(self):
        form = self._create_bound_test_model_form(form_class = TestModelForm,
                                                  orig_filename = 'image15k.png',
                                                  dest_filename = 'the_file.png',
                                                  content_type = 'image/png')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0], u'Files of size greater than 10.0 KB are not allowed. Your file is 14.2 KB')


    def test_form_invalid_filetype(self):
        form = self._create_bound_test_model_form(form_class = TestModelForm,
                                                  orig_filename = 'document1k.pdf',
                                                  dest_filename = 'the_file.pdf',
                                                  content_type = 'application/pdf')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0], u'Files of type application/pdf are not supported.')


    def test_form_invalid_filetype_and_size(self):
        form = self._create_bound_test_model_form(form_class = TestModelForm,
                                                  orig_filename = 'document15k.pdf',
                                                  dest_filename = 'the_file.pdf',
                                                  content_type = 'application/pdf')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0], u'Files of type application/pdf are not supported.')


    def test_form_fake_filetype(self):
        form = self._create_bound_test_model_form(form_class = TestModelForm,
                                                  orig_filename = 'document1k.pdf',
                                                  dest_filename = 'the_file.pdf',
                                                  content_type = 'image/png')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0], u'Files of type application/pdf are not supported.')


    def test_form_no_validate(self):
        form = self._create_bound_test_model_form(form_class = TestModelNoValidateForm,
                                                  orig_filename = 'document15k.pdf',
                                                  dest_filename = 'the_file.pdf',
                                                  content_type = 'application/pdf')
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.pdf')

        instance.the_file.delete()
        instance.delete()


    def test_form_null_file(self):
        form = self._create_bound_test_model_form(form_class = TestModelNoValidateForm)
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertEqual(instance.the_file, None)

        instance.delete()


    def test_quota_empty(self):
        container = self._create_container(name = 'container1')

        quota = FileQuota()
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 0)
        self.assertFalse(quota.exceeds())

        container.delete()


    def test_quota_one_file(self):
        container = self._create_container(name = 'container')
        element = self._add_element(container = container,
                                    orig_filename = 'image2k.png',
                                    dest_filename = 'the_file.png')

        quota = FileQuota()
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 2120)
        self.assertFalse(quota.exceeds())

        element.the_file.delete()
        element.delete()
        container.delete()


    def test_quota_several_files_several_containers(self):
        container1 = self._create_container(name = 'container1')
        element1 = self._add_element(container = container1,
                                     orig_filename = 'image2k.png',
                                     dest_filename = 'the_file1.png')
        element2 = self._add_element(container = container1,
                                     orig_filename = 'image15k.png',
                                     dest_filename = 'the_file2.png')
        container2 = self._create_container(name = 'container2')
        element3 = self._add_element(container = container2,
                                     orig_filename = 'document15k.pdf',
                                     dest_filename = 'the_file3.pdf')

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

        container = self._create_container(name = 'container1')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 0)
        self.assertFalse(quota.exceeds())
        self.assertTrue(quota.exceeds(2120))

        element = self._add_element(container = container,
                                    orig_filename = 'image2k.png',
                                    dest_filename = 'the_file.png')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 2120)
        self.assertTrue(quota.exceeds())

        element.the_file.delete()
        element.delete()
        container.delete()


    def test_quota_near_limit(self):
        quota = FileQuota(max_usage = 6500)

        container = self._create_container(name = 'container1')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 0)
        self.assertFalse(quota.near_limit())

        element1 = self._add_element(container = container,
                                    orig_filename = 'image2k.png',
                                    dest_filename = 'the_file.png')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 2120)
        self.assertFalse(quota.near_limit())

        element2 = self._add_element(container = container,
                                    orig_filename = 'image2k.png',
                                    dest_filename = 'the_file.png')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 4240)
        self.assertFalse(quota.near_limit())

        element3 = self._add_element(container = container,
                                    orig_filename = 'image2k.png',
                                    dest_filename = 'the_file.png')
        quota.update(container.test_elements.all(), 'the_file')
        self.assertEqual(quota.current_usage, 6360)
        self.assertTrue(quota.near_limit())

        element1.the_file.delete()
        element2.the_file.delete()
        element3.the_file.delete()
        element1.delete()
        element2.delete()
        element3.delete()
        container.delete()


    def test_form_quota_check(self):
        container = self._create_container(name = 'container1')

        form1 = self._create_unbound_test_element_form(container = container)
        self.assertFalse(form1.exceeds_quota())

        element = self._add_element(container = container,
                                    orig_filename = 'image15k.png',
                                    dest_filename = 'the_file.png')

        form2 = self._create_unbound_test_element_form(container = container)
        self.assertTrue(form2.exceeds_quota())

        element.the_file.delete()
        element.delete()
        container.delete()


    def test_form_quota_ok(self):
        container = self._create_container(name = 'container1')

        form = self._create_bound_test_element_form(container = container,
                                                    orig_filename = 'image2k.png',
                                                    dest_filename = 'the_file.png',
                                                    content_type = 'image/png')
        self.assertTrue(form.is_valid())

        container.delete()


    def test_form_quota_exceeded(self):
        container = self._create_container(name = 'container1')
        element = self._add_element(container = container,
                                    orig_filename = 'image2k.png',
                                    dest_filename = 'the_file.png')

        form = self._create_bound_test_element_form(container = container,
                                                    orig_filename = 'image15k.png',
                                                    dest_filename = 'the_file.png',
                                                    content_type = 'image/png')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0],
                u'Please keep the total uploaded files under 9.8 KB. With this file, the total would be 16.3 KB.')

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


    def _create_bound_test_model_form(self, form_class, orig_filename = None,
                                      dest_filename = None, content_type = None):
        if orig_filename and dest_filename and content_type:
            uploaded_file = SimpleUploadedFile(
                    name = dest_filename,
                    content = self._get_sample_file(orig_filename).read(),
                    content_type = content_type,
                )
            files = {'the_file': uploaded_file}
        else:
            files = {}
        form = form_class(data = {}, files = files)
        return form


    def _create_container(self, name):
        return TestContainer.objects.create(name = name)


    def _add_element(self, container, orig_filename, dest_filename):
        return container.test_elements.create(
                the_file = File(self._get_sample_file(orig_filename), dest_filename)
            )


    def _create_unbound_test_element_form(self, container):
        return TestElementForm(container = container)


    def _create_bound_test_element_form(self, container, orig_filename = None,
                                        dest_filename = None, content_type = None):
        if orig_filename and dest_filename and content_type:
            uploaded_file = SimpleUploadedFile(
                    name = dest_filename,
                    content = self._get_sample_file(orig_filename).read(),
                    content_type = content_type,
                )
            files = {'the_file': uploaded_file}
        else:
            files = {}
        form = TestElementForm(container = container, data = {}, files = files)
        return form

