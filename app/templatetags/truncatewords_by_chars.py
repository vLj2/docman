from django import template

register = template.Library()

@register.filter
def truncatewords_by_chars(value, limit):
    """
    Truncates a string after a given number of chars keeping whole words.
    
    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """
    
    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value[:-1]
    
    # Make sure it's unicode
    #value = unicode(value)
    
    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value
    
    # ending
    ending = value.split('.')[len(value.split('.'))-1]
    
    if len(value[:limit]) + len(ending) + 1 > len(value):
    	return value
    
    # Cut the string
    value = value[:limit]
    
    # Break into words and remove the last
    #words = value.split(' ')[:-1]
    
    # Join the words and return
    #return ' '.join(words) + '...'
    return value + "(..)." + ending
