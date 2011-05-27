from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from docman.settings import DEFAULT_FROM_EMAIL

def docmail(to, subject, template, data):
	plaintext = get_template('email/%s.txt' % template)
	htmly = get_template('email/%s.html'% template) 
	
	text_content = plaintext.render(data)	
	html_content = htmly.render(data)
	
	msg = EmailMultiAlternatives(subject, text_content, DEFAULT_FROM_EMAIL, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()
 