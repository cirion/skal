from django import template
from lok import models

register = template.Library()

@register.filter(is_safe=True)
def macro(text, character):
	text = text.replace('#INFORMAL_NAME#', character.name)
	text = text.replace('#TITLE_NAME#', character.title_name())
	return text

register.filter('macro', macro)
