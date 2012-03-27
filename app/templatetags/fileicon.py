from django import template
from settings import FILEICONS, MEDIA_URL, FILEICONS_LARGE

register = template.Library()

@register.filter
def fileicon(image, large=False):
	if large:
		if image not in FILEICONS_LARGE:
			image = 'default'
		return '%simg/fileicons_large/%s' % (MEDIA_URL, image)
	else:
		if image not in FILEICONS:
			image = 'file'
		return '%simg/fileicons/%s' % (MEDIA_URL, image)	
fileicon.is_safe = True