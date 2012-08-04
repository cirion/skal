from lok.models import Scenario, Choice
from django.contrib import admin

class ChoiceInline(admin.StackedInline):
	model = Choice
	extra = 3

class ScenarioAdmin(admin.ModelAdmin):
	inlines = [ChoiceInline]
	search_fields = ['title', 'description']

admin.site.register(Scenario, ScenarioAdmin)
