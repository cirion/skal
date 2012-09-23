from django import template

register = template.Library()

@register.filter(is_safe=True)
def macro(text, character):
	from lok import models
	from lok.models import Character
	text = text.replace('#INFORMAL_NAME#', character.name)
	text = text.replace('#TITLE_NAME#', character.title_name())
	if (character.gender == Character.GENDER_MALE):
		text = text.replace('#MAN_WOMAN_CAPITAL#', 'Man')
		text = text.replace('#MAN_WOMAN#', 'man')
		text = text.replace('#HIS_HER#', 'his')
		text = text.replace('#HE_SHE#', 'he')
		text = text.replace('#HE_SHE_CAPITAL#', 'He')
	else:
		text = text.replace('#MAN_WOMAN_CAPITAL#', 'Woman')
		text = text.replace('#MAN_WOMAN#', 'woman')
		text = text.replace('#HIS_HER#', 'her')
		text = text.replace('#HE_SHE#', 'she')
		text = text.replace('#HE_SHE_CAPITAL#', 'She')
	return text

register.filter('macro', macro)
