docman README
=============

docman is a collaborative document management software, powered by Django. (http://djangoproject.org)

This software has been written to create a space for easy document management and sharing. You are able to create categories and assign them to a specific (or none) semester. Within this categories, there can be lectures or pseudo lectures where documents can be uploaded to. Documents can be commented, rated, tagged and of course be downloaded in original file format or zipped. You can follow a lecture or document and get notified if something changes. Also, a kind of revision management for each document. DocMan has a powerful rights management system.

Read more about DocMan on [get.docman.me](http://get.docman.me).

*Please note: This is the open source version of DocMan which is missing some features offered on [get.docman.me](http://get.docman.me).*

Learn more about our SaaS solution
----------------------------------

Interested in using DocMan but no idea what to do? We offer DocMan hosting on our infrastructure, directly offered by the developers of DocMan! [Read more](http://get.docman.me)

Requirements
------------

DocMan requires several modules to be installed:

* [python-django](http://djangoproject.org) -- at least Django 1.3
* [mysql-python](http://sourceforge.net/projects/mysql-python/) when using MySQL database backend
* [python-dateutil](http://labix.org/python-dateutil)
* [django-registration](http://code.google.com/p/django-registration/)
* [whoosh](https://bitbucket.org/mchaput/whoosh/wiki/Home)
* [django-ratings](https://github.com/dcramer/django-ratings)
* [django-tagging](http://code.google.com/p/django-tagging/)
* [pyPdf](http://pybrary.net/pyPdf/)
* [django-haystack](http://haystacksearch.org/)
* [py-bcrypt](http://code.playfire.com/django-bcrypt//)
* [PIL](http://www.pythonware.com/products/pil/)
* [django-facebook](https://github.com/tschellenbach/Django-facebook)

Also, your webserver needs needs to know about [X-SENDFILE](https://tn123.org/mod_xsendfile/).

Setup
-----

First, copy `settings_local.py-dist` to `settings_local.py` and edit the file to suit your needs.

Then, it is just a regular django application setup: `./manage.py syncdb`, `./manage.py runserver`, and you should be done with your testing environment.

Rebuild full text search index
------------------------------

To rebuild your search index, please run the following command:

	python manage.py rebuild_index --noinput 2>&1 >/dev/null &

The best idea is to run this via crond to rebuild the index once or twice per hour.

Contribute to the translation
-----------------------------

If you want to contribute to the translation, you can improve the current translations
or start a new translation into a different language. To do so, you need xgettext/gettext
which you can install using e.g. `sudo apt-get install gettext` on Ubuntu/Debian systems.
Then go to the DocMan folder and create/update the .po file for you language.
For German (`de`) the command would be:

    cd docman
    django-admin.py makemessages -l de

When you're done translating the strings in the file *locale/de/LC_MESSAGES/django.po*,
run `django-admin.py compilemessages` and test if everything works as expected.

Icon copyright
--------------

Icons powered by iconfinder.com, most of them free for commercial use.
