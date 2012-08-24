from django import template
from lok import models

register = template.Library()

@register.filter(is_safe=True)
def macro(text, character):
	text = text.replace('#INFORMAL_NAME#', character.name)
	text = text.replace('#TITLE_NAME#', character.title_name())
	if (character.gender == Character.MALE):
		text = text.replace('#MAN_WOMAN_CAPITAL#', 'Man')
		text = text.replace('#MAN_WOMAN#', 'man')
	else:
		text = text.replace('#MAN_WOMAN_CAPITAL#', 'Woman')
		text = text.replace('#MAN_WOMAN#', 'woman')
	return text

register.filter('macro', macro)
