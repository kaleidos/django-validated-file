django-validated-file
=====================

.. image:: https://travis-ci.org/kaleidos/django-validated-file.png?branch=master
    :target: https://travis-ci.org/kaleidos/django-validated-file

.. image:: https://coveralls.io/repos/kaleidos/django-validated-file/badge.png?branch=master
    :target: https://coveralls.io/r/kaleidos/django-validated-file?branch=master

.. image:: https://pypip.in/v/django-validated-file/badge.png
    :target: https://crate.io/packages/django-validated-file

.. image:: https://pypip.in/d/django-validated-file/badge.png
    :target: https://crate.io/packages/django-validated-file


This Django app adds a new field type, ValidatedFileField, that add the
capability of checking the document size and types the user may send.

Installation
------------

 * Download and install package with python setup.py install.
 * Note that this package depends on python-magic (to check field types).
 * Add 'validatedfile' to your INSTALLED_APPS in settings.py.

Validate single file
--------------------

Create a model and add a field of type ValidatedFileField. You can add a maximum size in bytes
and a list of valid mime types that will be allowed. The list of all mime types is available
here: http://www.iana.org/assignments/media-types/index.html::

    from django.db import models
    from validatedfile.fields import ValidatedFileField

    class TestModel(models.Model):
        the_file = ValidatedFileField(
                        null = True,
                        blank = True,
                        upload_to = 'testfile',
                        max_upload_size = 10240,
                        content_types = ['image/png'])

The model can be used in forms or model forms like a normal FileField. If a user tries to upload
a file with too much size or without a valid type, a form validation error will occur.


Validate quota usage
--------------------

This example also checks the total size of all files uploaded by one user::

    (in models.py)

    from django.contrib.auth.models import User
    from django.db import models
    from validatedfile.fields import ValidatedFileField

    class TestModel(models.Model):
        user = models.ForeignKey(
                        User,
                        null = False,
                        blank = False,
                        related_name = 'test_models')
        the_file = ValidatedFileField(
                        null = True,
                        blank = True,
                        upload_to = 'testfile',
                        max_upload_size = 10240,
                        content_types = ['image/png'])

    (in forms.py)

    from django import forms
    from validatedfile.fields import QuotaValidator
    from models.py import TestModel

    class TestModelForm(models.ModelForm):
        the_file = forms.FileField(
                        required = True,
                        validators = [QuotaValidator(max_usage = 102400)])

        class Meta:
            model = TestModel
            fields = ['the_file']

        def __init__(self, user, *args, **kwargs):
            super(TestModelForm, self).__init__(*args, **kwargs)
            self.user = user
            self.fields['the_file'].validators[0].update_quota(
                    items = self.user.test_models.all(),
                    attr_name = 'the_file',
                )

        def exceeds_quota(self):
            return self.fields['the_file'].validators[0].quota.exceeds()

        def save(self, *args, **kwargs):
            model = super(TestModelForm, self).save(commit = False)
            model.user = self.user
            model.save()


Note on DOS attacks
-------------------

Important note: the check of the file size is made by Django once the whole file has been uploaded
to the server and stored in a temp directory (or in memory if the file is small). Thus, this is
useful to guarantee the quota of the users, for example, but will not stop an attacking user that
wants to block the server by sending huge files (e. g. of several Gb).

To avoid this, you need to configure your front end to limit the size of uploaded files. How to do
it depends on the software you are using. For example, if you use apache, you should use
**LimitRequestBody** directive (http://httpd.apache.org/docs/2.2/mod/core.html#limitrequestbody).

This is a complementary measure, because you'll usually want normal users that exceed the size by a
reasonable amount to get a friendly form validation message, while attacking users will see how their
connection is abruptly cut before the file finishes uploading. So the recommended setting is to give
`max_upload_size` a small value (e.g. 5Mb) and `LimitRequestBody` a higher one (e.g. 100Mb).

