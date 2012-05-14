#!/bin/sh
cd validatedfile
django-admin.py makemessages -l en
django-admin.py makemessages -l es
django-admin.py compilemessages

