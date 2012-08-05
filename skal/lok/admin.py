from lok.models import Scenario, Choice, MoneyOutcome, StatOutcome, Result, ChoiceStatPreReq, ScenarioStatPreReq, Character, CharacterStat, Stat, CharacterPlot, Plot, Item, CharacterItem, PlotOutcome, ItemOutcome, ScenarioItemPreReq, ChoiceItemPreReq, ScenarioPlotPreReq

from django.contrib import admin

class MoneyOutcomeInline(admin.TabularInline):
	model = MoneyOutcome

class StatOutcomeInline(admin.TabularInline):
	model = StatOutcome

class PlotOutcomeInline(admin.TabularInline):
	model = PlotOutcome

class ItemOutcomeInline(admin.TabularInline):
	model = ItemOutcome

class ResultInline(admin.StackedInline):
	model = Result

class ChoiceStatPreReqInline(admin.TabularInline):
	model = ChoiceStatPreReq

class ScenarioStatPreReqInline(admin.TabularInline):
	model = ScenarioStatPreReq

class ChoiceItemPreReqInline(admin.TabularInline):
	model = ChoiceItemPreReq

class ScenarioItemPreReqInline(admin.TabularInline):
	model = ScenarioItemPreReq

class ScenarioPlotPreReqInline(admin.TabularInline):
	model = ScenarioPlotPreReq

class ChoiceInline(admin.StackedInline):
	model = Choice

class ScenarioAdmin(admin.ModelAdmin):
	inlines = [ScenarioStatPreReqInline,ScenarioItemPreReqInline,ScenarioPlotPreReqInline,ChoiceInline]
	search_fields = ['title', 'description']

class ChoiceAdmin(admin.ModelAdmin):
	model = Choice
	inlines = [ChoiceStatPreReqInline,ResultInline]
	search_fields = ['title', 'description']

class ResultAdmin(admin.ModelAdmin):
	model = Result
	inlines = [MoneyOutcomeInline, StatOutcomeInline,PlotOutcomeInline,ItemOutcomeInline]
	search_fields = ['title', 'description']


class CharacterStatInline(admin.TabularInline):
	model = CharacterStat

class CharacterPlotInline(admin.TabularInline):
	model = CharacterPlot

class CharacterItemInline(admin.TabularInline):
	model = CharacterItem

class CharacterAdmin(admin.ModelAdmin):
	model = Character
	inlines = [CharacterStatInline, CharacterPlotInline, CharacterItemInline]

class StatAdmin(admin.ModelAdmin):
	model = Stat

class ItemAdmin(admin.ModelAdmin):
	model = Item

class PlotAdmin(admin.ModelAdmin):
	model = Plot

admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Stat, StatAdmin)
admin.site.register(Plot, PlotAdmin)
admin.site.register(Item, ItemAdmin)
