from django import template

# this is LOL, but it finally works.

register = template.Library()

@register.filter 
def subtract(value, arg):
	if value and arg:
		return int(value) - int(arg) 
	else:
		return 0