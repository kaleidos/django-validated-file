django-validated-file
=====================

This Django app adds two field types, ValidatedFileField and ValidatedImageField, that add the
capability of checking the document size and types the user may send.

Installation
------------

 * Download and install package with python setup.py install.
 * Note that this package depends on python-magic (to check field types).
 * Add 'validatedfile' to your INSTALLED_APPS in settings.py.

Usage
-----

Create a model and add a field of type ValidatedFileField. You can add a maximum size in bytes
and a list of valid mime types that will be allowed. The list of all mime types is available
here: http://www.iana.org/assignments/media-types/index.html. If a user tries to upload a file
with too much size or without a valid type, a form validation error will occur::

    class TestModel(models.Model):
        the_file = ValidatedFileField(
                        null = True,
                        blank = True,
                        upload_to = 'testfile',
                        max_upload_size = 10240,
                        content_types = ['image/png'])

