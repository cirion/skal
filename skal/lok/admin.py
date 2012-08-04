from lok.models import Scenario, Choice, MoneyOutcome, StatOutcome, Result, ChoiceStatPreReq, ScenarioStatPreReq

from django.contrib import admin

class MoneyOutcomeInline(admin.TabularInline):
	model = MoneyOutcome

class StatOutcomeInline(admin.TabularInline):
	model = StatOutcome

class ResultInline(admin.StackedInline):
	model = Result

class ChoiceStatPreReqInline(admin.TabularInline):
	model = ChoiceStatPreReq

class ScenarioStatPreReqInline(admin.TabularInline):
	model = ScenarioStatPreReq

class ChoiceInline(admin.StackedInline):
	model = Choice

class ScenarioAdmin(admin.ModelAdmin):
	inlines = [ScenarioStatPreReqInline,ChoiceInline]
	search_fields = ['title', 'description']

class ChoiceAdmin(admin.ModelAdmin):
	model = Choice
	inlines = [ChoiceStatPreReqInline,ResultInline]

class ResultAdmin(admin.ModelAdmin):
	model = Result
	inlines = [MoneyOutcomeInline, StatOutcomeInline]

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Result, ResultAdmin)
