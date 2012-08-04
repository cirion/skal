from lok.models import Scenario, Choice, MoneyOutcome, StatOutcome, Result
from django.contrib import admin

class MoneyOutcomeInline(admin.TabularInline):
	model = MoneyOutcome

class StatOutcomeInline(admin.TabularInline):
	model = StatOutcome

class ResultInline(admin.StackedInline):
	model = Result

class ChoiceInline(admin.StackedInline):
	model = Choice
	inlines = [ResultInline]

class ScenarioAdmin(admin.ModelAdmin):
	inlines = [ChoiceInline]
	search_fields = ['title', 'description']

class ChoiceAdmin(admin.ModelAdmin):
	model = Choice
	inlines = [ResultInline]

class ResultAdmin(admin.ModelAdmin):
	model = Result
	inlines = [MoneyOutcomeInline, StatOutcomeInline]

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Result, ResultAdmin)
