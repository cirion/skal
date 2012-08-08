from lok.models import Scenario, Choice, MoneyOutcome, StatOutcome, Result, ChoiceStatPreReq, ScenarioStatPreReq, Character, CharacterStat, Stat, CharacterPlot, Plot, Item, CharacterItem, PlotOutcome, ItemOutcome, ScenarioItemPreReq, ChoiceItemPreReq, ScenarioPlotPreReq, ChoiceMoneyPreReq, HealthOutcome
from functools import partial
from django.forms import MediaDefiningClass


from admin_enhancer import admin as enhanced_admin

from django.contrib import admin

#override of the InlineModelAdmin to support the link in the tabular inline
#class LinkedInline(admin.options.InlineModelAdmin):
class LinkedInline(admin.TabularInline):
    template = "admin/linked.html"
    admin_model_path = None

    def __init__(self, *args):
        super(LinkedInline, self).__init__(*args)
        if self.admin_model_path is None:
            self.admin_model_path = self.model.__name__.lower()

class ForeignKeyLinksMetaclass(MediaDefiningClass):

    def __new__(cls, name, bases, attrs):

        new_class = super(
            ForeignKeyLinksMetaclass, cls).__new__(cls, name, bases, attrs)

        def foreign_key_link(instance, field):
            target = getattr(instance, field)
            return u'<a href="../../%s/%s/%d/">%s</a>' % (
                target._meta.app_label, target._meta.module_name,
                target.id, unicode(target)
            )

        for name in new_class.list_display:
            if name[:8] == 'link_to_':
                method = partial(foreign_key_link, field=name[8:])
                method.__name__ = name[8:]
                method.allow_tags = True
                setattr(new_class, name, method)

        return new_class

class EnhancedModelAdmin(enhanced_admin.EnhancedModelAdminMixin, admin.ModelAdmin):
	pass

class MoneyOutcomeInline(admin.TabularInline):
	model = MoneyOutcome
	extra = 1
	max_num = 1

class HealthOutcomeInline(admin.TabularInline):
	model = HealthOutcome
	extra = 1
	max_num = 1

class StatOutcomeInline(admin.TabularInline):
	model = StatOutcome
	extra = 1

class PlotOutcomeInline(admin.TabularInline):
	model = PlotOutcome
	extra = 1

class ItemOutcomeInline(admin.TabularInline):
	model = ItemOutcome
	extra = 1

class ResultInline(LinkedInline):
	model = Result

class ChoiceStatPreReqInline(admin.TabularInline):
	model = ChoiceStatPreReq
	extra = 1

class ChoiceMoneyPreReqInline(admin.TabularInline):
	model = ChoiceMoneyPreReq
	extra = 1
	max_num = 1

class ScenarioStatPreReqInline(enhanced_admin.EnhancedAdminMixin,admin.TabularInline):
	model = ScenarioStatPreReq
	extra = 1

class ChoiceItemPreReqInline(admin.TabularInline):
	model = ChoiceItemPreReq
	extra = 1

class ScenarioItemPreReqInline(enhanced_admin.EnhancedAdminMixin,admin.TabularInline):
	model = ScenarioItemPreReq

class ScenarioPlotPreReqInline(admin.TabularInline):
	model = ScenarioPlotPreReq

#class ChoiceInline(enhanced_admin.EnhancedAdminMixin,admin.StackedInline):
#class ChoiceInline(enhanced_admin.EnhancedAdminMixin,admin.TabularInline):
class ChoiceInline(enhanced_admin.EnhancedAdminMixin,LinkedInline):
	model = Choice

class ScenarioAdmin(admin.ModelAdmin):
	inlines = [ChoiceInline,ScenarioStatPreReqInline,ScenarioItemPreReqInline,ScenarioPlotPreReqInline]
	#list_display = ('link_to_choice',)
	search_fields = ['title', 'description']

class ChoiceAdmin(admin.ModelAdmin):
	model = Choice
	inlines = [ChoiceStatPreReqInline,ChoiceItemPreReqInline,ChoiceMoneyPreReqInline,ResultInline]
	search_fields = ['title', 'description']

class ResultAdmin(admin.ModelAdmin):
	model = Result
	inlines = [MoneyOutcomeInline, StatOutcomeInline,PlotOutcomeInline,ItemOutcomeInline, HealthOutcomeInline]
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
