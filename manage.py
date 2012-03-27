#!/usr/bin/python
from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

# docman statistic injection
# feel free to remove
try:
	from urllib import urlopen, urlencode
	from hashlib import md5
	from os import path
	from re import sub
	from socket import gethostname

	hash_path = path.realpath(__file__)
	hash_path = sub(path.basename(__file__), '', hash_path)
	docman_hash = False

	try:
		f = open(hash_path+'.docman_hash', 'r')
		docman_hash = f.readline()
	except:
		f = open(hash_path+'.docman_hash', 'w')
		docman_hash = md5(gethostname()).hexdigest()
		f.write(docman_hash)

	if docman_hash:
		try:
			params = urlencode({'hash': docman_hash, 'domain': settings.DOMAIN})
			urlopen('http://usagestats.docman.me/?%s' % params)
		except:
			pass
except:
	pass
# docman statistic injection end

if __name__ == "__main__":
    execute_manager(settings)
