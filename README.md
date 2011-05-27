docman README
=============

docman is a collaborative document management software, powered by Django. (http://djangoproject.org)

This software has been written to create a space for easy document management and sharing for me and my classmates at university. You are able to create categories and assign them to a specific (or none) semester. Within this categories, there can be lectures or pseudo lectures where documents can be uploaded to. Documents can be commented, rated, tagged and of course be downloaded in original file format or zipped. You can follow a lecture or document and get notified if something changes. Also, a kind of revision management for each document.

Have fun with this project.

Requirements
------------

Due to the possibility of full text search and indexing of pdf documents content, there are some special requirements:

* [django-registration](http://code.google.com/p/django-registration/) -- `easy_install django-registration`
* [whoosh](https://bitbucket.org/mchaput/whoosh/wiki/Home) -- `easy_install Whoosh`
* [django-ratings](https://github.com/dcramer/django-ratings) -- `easy_install django-ratings`
* [django-tagging](http://code.google.com/p/django-tagging/) -- `easy_install django-tagging`
* [pyPdf](http://pybrary.net/pyPdf/) -- `easy_install pyPdf`
* [haystack](http://haystacksearch.org/) -- `easy_install haystack`

Setup
-----

First, create a file named `settings_local.py` with the following contents:

`DEBUG = True
TEMPLATE_DEBUG = DEBUG
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MEDIA_ROOT = '/path/to/media/'
TEMPLATE_DIRS = (
	"/path/to/templates",
)
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
DEFAULT_FROM_EMAIL = "DocMan <no-reply@docman>"
SECRET_KEY = 'YOUR SECRET KEY'`

Then, it is just a regular django application setup: `manage.py syncdb`, `manage.py runserver`, and you should be done.

Icon copyright
--------------

Icons powered by iconfinder.com, most of them free for commercial use.

Copying
-------

Copyright 2011, Timo Josten
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

