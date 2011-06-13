docman README
=============

docman is a collaborative document management software, powered by Django. (http://djangoproject.org)

This software has been written to create a space for easy document management and sharing for me and my classmates at university. You are able to create categories and assign them to a specific (or none) semester. Within this categories, there can be lectures or pseudo lectures where documents can be uploaded to. Documents can be commented, rated, tagged and of course be downloaded in original file format or zipped. You can follow a lecture or document and get notified if something changes. Also, a kind of revision management for each document.

Have fun with this project.

Requirements
------------

Due to the possibility of full text search and indexing of pdf documents content, there are some special requirements:

* [python-django](http://djangoproject.org) -- at least Django 1.3
* [mysql-python](http://sourceforge.net/projects/mysql-python/) -- `easy_install mysql-python`
* [python-dateutil](http://labix.org/python-dateutil) -- `easy_install python-dateutil`
* [django-registration](http://code.google.com/p/django-registration/) -- `easy_install django-registration`
* [whoosh](https://bitbucket.org/mchaput/whoosh/wiki/Home) -- `easy_install Whoosh`
* [django-ratings](https://github.com/dcramer/django-ratings) -- `easy_install django-ratings`
* [django-tagging](http://code.google.com/p/django-tagging/) -- `easy_install django-tagging`
* [pyPdf](http://pybrary.net/pyPdf/) -- `easy_install pyPdf`
* [django-haystack](http://haystacksearch.org/) -- `easy_install django-haystack`

Setup
-----

First, create a file named `settings_local.py` with the following contents:

	DEBUG = True
	TEMPLATE_DEBUG = DEBUG

	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

	### The domain will be used mainly in emails to the users:
	DOMAIN = 'http://docman.me'

	### Adjust this path to the absolute path of the docman media directory:
	MEDIA_ROOT = '/path/to/docman/media/'
	### Adjust this path to the docman templates directory:
	TEMPLATE_DIRS = ( "path/to/docman/templates", )

	### Where will the Whoosh search indexes be stored?
	### This should be an empty directory with write access (not the document root):
	### cf. <http://docs.haystacksearch.org/dev/settings.html>
	HAYSTACK_WHOOSH_PATH = '/path/to/whoosh_index'

	DATABASES = {
		'default': {
	    	'NAME': 'database',
	        'ENGINE': 'django.db.backends.mysql',
	        'USER': 'user',
	        'PASSWORD': 'password',
	        'HOST': '',
		}
	}

	### Languages you want DocMan to display its messages in:
	LANGUAGES = (
	    ('de', 'German'),
	    ('en', 'English'),
	)

	### Information for the Imprint of DocMan ( /about site)
	IMPRINT = { 'name': 'John Doe',
	        'address1': '1600 Pennsylvania Avenue NW',
	        'address2': 'Washington, DC 20500',
	        'phone': '202-456-1414',
	        'email': 'your.name@example.com'
	}

	DEFAULT_FROM_EMAIL = "DocMan <no-reply@docman>"

	### Seed in hashing algorithms. Set this to a random string - the longer, the better
	### cf. <https://docs.djangoproject.com/en/dev/ref/settings/#secret-key>
	SECRET_KEY = 'YOUR SECRET KEY'

Then, it is just a regular django application setup: `manage.py syncdb`, `manage.py runserver`, and you should be done.

Rebuild full text search index
------------------------------

To rebuild your search index, please run the following command:

	python manage.py rebuild_index --noinput 2>&1 >/dev/null &

The best idea is to run this via crond to rebuild the index once or twice per hour.

Contribute to the translation
_____________________________

If you want to contribute to the translation, you can improve the current translations
or start a new translation into a different language. For this, you need xgettext/gettext
which you can install using `sudo apt-get install gettext` on Ubuntu/Debian systems.  
Then go the DocMan folder and (re)create the .po file for you language.
In this example the language code is German (`de`):

    cd docman
    django-admin.py makemessages -l de

When you're done translating the strings in the file **locale/*de*/LC_MESSAGES/django.po**,
run `django-admin.py compilemessages` and test if everythign works as expected.

Icon copyright
--------------

Icons powered by iconfinder.com, most of them free for commercial use.
