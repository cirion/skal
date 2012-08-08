from django.db import models
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.contrib.auth.models import User
from lok.utils import level_from_value as level_from_value
from lok.utils import value_from_level as value_from_level

GENDER_FEMALE = 1
GENDER_MALE = 2
GENDER_CHOICES = (
	(GENDER_FEMALE, "Female"),
	(GENDER_MALE, "Male"),
)

def valid_for_plot_pre_reqs(character, pre_reqs):
	if pre_reqs:
		try:
			for pre_req in pre_reqs:
				if pre_req.value == 0 and CharacterPlot.objects.filter(character = character.pk, plot = pre_req.plot):
					return False
				elif pre_req.value > 0 and CharacterPlot.objects.get(character = character.pk, plot = pre_req.plot).value != pre_req.value:
					return False
		except CharacterStat.DoesNotExist:
			return False
		except CharacterPlot.DoesNotExist:
			return False
	return True

def valid_for_stat_pre_reqs(character, pre_reqs):
	if pre_reqs:
		try:
			for pre_req in pre_reqs:
				character_stat = CharacterStat.objects.get(character=character.pk, stat=pre_req.stat)
				if level_from_value(character_stat.value) < pre_req.minimum or level_from_value(character_stat.value) > pre_req.maximum:
					return False
		except CharacterStat.DoesNotExist:
			return False
	return True

def valid_for_item_pre_reqs(character, pre_reqs):
	if pre_reqs:
		try:
			for pre_req in pre_reqs:
				character_item = CharacterItem.objects.get(character=character.pk, item=pre_req.item)
				if character_item.quantity < pre_req.minimum:
					return False
		except CharacterItem.DoesNotExist:
			return False;
	return True;

def valid_for_plot_pre_req(character, pre_reqs):
	if pre_reqs:
		try:
			for pre_req in pre_req:
				character_plot = CharacterPlot.objects.get(character=character.pk, plot=pre_req.plot)
				if character_plot.value != pre_req.value:
					return False
		except CharacterPlot.DoesNotExist:
			return False;
	return True;

class Scenario(models.Model):
	title = models.CharField(max_length=100)
	image = models.ImageField(blank=True,null=True,upload_to="/home/chris/django/skal/pics")
	description = models.TextField(max_length=2000)
	TYPE_QUEST = 1
	TYPE_ENCOUNTER = 2
	TYPE_CHOICES = (
		(TYPE_QUEST, "Quest"),
		(TYPE_ENCOUNTER, "Encounter"),
	)
	type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_ENCOUNTER)
	def __unicode__(self):
		return self.title
	def valid_for(self, character):
		pre_reqs = ScenarioStatPreReq.objects.filter(scenario=self.pk)
		if not valid_for_stat_pre_reqs(character,pre_reqs):
			return False
		pre_reqs = ScenarioItemPreReq.objects.filter(scenario=self.pk)
		if not valid_for_item_pre_reqs(character,pre_reqs):
			return False
		pre_reqs = ScenarioPlotPreReq.objects.filter(scenario=self.pk)
		if not valid_for_plot_pre_reqs(character,pre_reqs):
			return False
		return True

class Choice(models.Model):
	scenario = models.ForeignKey(Scenario)
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=1000)
	visible = models.BooleanField()
	def __unicode__(self):
		return self.title
	def valid_for(self, character):
		pre_reqs = ChoiceStatPreReq.objects.filter(choice=self.pk)
		if not valid_for_stat_pre_reqs(character,pre_reqs):
			return False
		pre_reqs = ChoiceItemPreReq.objects.filter(choice=self.pk)
		if not valid_for_item_pre_reqs(character,pre_reqs):
			return False
		return True

class Plot(models.Model):
	name = models.CharField(max_length=100)
	visible = models.BooleanField(default=False)
	description = models.TextField(max_length=2000)
	def __unicode__(self):
		return self.name

class Item(models.Model):
	name = models.CharField(max_length=100)
	value = models.IntegerField(default=1)
	def __unicode__(self):
		return self.name

class Stat(models.Model):
	TYPE_SKILL = 1
	TYPE_FAME = 2
	TYPE_ESTEEM = 3
	TYPE_CHARACTERISTIC = 4
	TYPE_CHOICES = (
		(TYPE_SKILL, "Skill"),
		(TYPE_FAME, "Fame"),
		(TYPE_ESTEEM, "Esteem"),
		(TYPE_CHARACTERISTIC, "Characteristic"),
	)
	type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_SKILL)
	name = models.CharField(max_length=50)
	def __unicode__(self):
		return self.name
	
	
class ScenarioStatPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	stat = models.ForeignKey(Stat)
	minimum = models.IntegerField(default=0)
	maximum = models.IntegerField(default=100)
	visible = models.BooleanField(default=True)
	def __unicode__(self):
		return str(self.stat)

class ScenarioItemPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	item = models.ForeignKey(Item)
	minimum = models.IntegerField(default=1)
	visible = models.BooleanField(default=True)
	def __unicode__(self):
		return str(self.minimum) + " " + self.item.name

class ScenarioPlotPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	plot = models.ForeignKey(Plot)
	value = models.IntegerField()
	def __unicode__(self):
		return self.plot.name + " " + str(self.value)

class ChoiceStatPreReq(models.Model):
	choice = models.ForeignKey(Choice)
	stat = models.ForeignKey(Stat)
	minimum = models.IntegerField(default=0)
	maximum = models.IntegerField(default=100)
	visible = models.BooleanField(default=True)
	def __unicode__(self):
		return str(self.stat)

class ChoiceItemPreReq(models.Model):
	choice = models.ForeignKey(Choice)
	item = models.ForeignKey(Item)
	minimum = models.IntegerField(default=1)
	def __unicode__(self):
		return str(self.minimum) + " " + self.item.name

class ChoiceMoneyPreReq(models.Model):
	choice = models.ForeignKey(Choice)
	amount = models.IntegerField()
	def __unicode__(self):
		return str(self.amount)

class Result(models.Model):
	SUCCESS = 1
	FAILURE = 2
	CHOICES = (
		(SUCCESS, "Success"),
		(FAILURE, "Failure"),
	)
	type = models.IntegerField(choices=CHOICES, default=SUCCESS)
	weight = models.IntegerField(default=1)
	choice = models.ForeignKey(Choice)
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=4000)
	
	def __unicode__(self):
		return self.title

class MoneyOutcome(models.Model):
	choice = models.ForeignKey(Result)
	amount = models.IntegerField()
	def __unicode__(self):
		return str(self.amount)
	
class StatOutcome(models.Model):
	choice = models.ForeignKey(Result)
	stat = models.ForeignKey(Stat)
	amount = models.IntegerField()
	maximum = models.IntegerField(default=100000)
	def __unicode__(self):
		return str(self.stat)

class ItemOutcome(models.Model):
	result = models.ForeignKey(Result)
	item = models.ForeignKey(Item)
	amount = models.IntegerField(default=1)
	def __unicode__(self):
		return str(self.amount) + " " + self.item.name

class PlotOutcome(models.Model):
	result = models.ForeignKey(Result)
	plot = models.ForeignKey(Plot)
	value = models.IntegerField()
	def __unicode__(self):
		return str(self.value) + " " + self.plot.name

class HealthOutcome(models.Model):
	result = models.ForeignKey(Result)
	amount = models.IntegerField()
	def __unicode__(self):
		return str(self.amount) + " health"

class Character(models.Model):
	MAX_ACTIONS = 20
	#ACTION_RECHARGE_TIME_SECS = 900
	ACTION_RECHARGE_TIME_SECS = 30
	player = models.ForeignKey(User)
	name = models.CharField(max_length=20)
	created = models.DateTimeField(auto_now_add=True)
	money = models.IntegerField(default=0)
	gender = models.IntegerField(choices=GENDER_CHOICES)
	current_health = models.IntegerField()
	total_choices = models.IntegerField(default=0)
	actions = models.IntegerField(default=20)
	refill_time = models.DateTimeField()
	def __unicode__(self):
		return self.name
	def update_actions(self):
		while datetime.utcnow().replace(tzinfo=utc) > self.refill_time and self.actions < Character.MAX_ACTIONS:
			self.actions = self.actions + 1
			self.refill_time = self.refill_time + timedelta(0, Character.ACTION_RECHARGE_TIME_SECS)
	def max_health(self):
		# Need to figure out how to grow this...
		best_stat = CharacterStat.objects.all().order_by('-value')[0]
		return level_from_value(best_stat.value)
	def update_with_result(self, result):
		changes = list()
		if self.actions == Character.MAX_ACTIONS:
			self.refill_time = datetime.utcnow().replace(tzinfo=utc) + timedelta(0, Character.ACTION_RECHARGE_TIME_SECS)
		self.actions = self.actions - 1
		stat_outcomes = StatOutcome.objects.filter(choice = result.pk)
		for outcome in stat_outcomes:
			stat, created = CharacterStat.objects.get_or_create(character=self, stat=outcome.stat)
			if (level_from_value(stat.value) < outcome.maximum):
				change = Change(type=Change.TYPE_INCREMENT)
				change.old = stat.value
				oldlevel = level_from_value(stat.value)
				change.name = stat.stat.name
				stat.value += outcome.amount
				change.amount = outcome.amount
				change.new = stat.value
				newlevel = level_from_value(stat.value)
				if oldlevel != newlevel:
					change.type = Change.TYPE_LEVEL
					change.old = oldlevel
					change.new = newlevel
					change.amount = newlevel - oldlevel
				changes.append(change)
				stat.save()

		money_outcomes = MoneyOutcome.objects.filter(choice = result.pk)
		for outcome in money_outcomes:
			change = Change(type = Change.TYPE_MONEY)
			change.name = "Royals"
			change.old = self.money
			self.money += outcome.amount
			# If we hit this test, we probably accidentally made the result amount bigger than the choice amount.
			if (self.money < 0):
				self.money = 0
			change.new = self.money
			change.amount = change.new - change.old
			changes.append(change)

		item_outcomes = ItemOutcome.objects.filter(result = result.pk)
		for outcome in item_outcomes:
			change = Change(type = Change.TYPE_ITEM)
			change.name = outcome.item.name
			item, created = CharacterItem.objects.get_or_create(character=self, item=outcome.item)
			change.old = item.quantity
			change.amount = outcome.amount
			item.quantity += outcome.amount
			change.new = item.quantity
			item.save()
			changes.append(change)

		health_outcomes = HealthOutcome.objects.filter(result = result.pk)
		for outcome in health_outcomes:
			change = Change(type = Change.TYPE_HEALTH)
			change.name = "health"
			change.old = self.current_health
			self.current_health += outcome.amount
			if (self.current_health < 0):
				self.current_health = 0
			if (self.current_health > self.max_health()):
				self.current_health = self.max_health()
			else:
				change.new = self.current_health
				change.amount = change.new - change.old
				changes.append(change)

		plot_outcomes = PlotOutcome.objects.filter(result = result.pk)
		for outcome in plot_outcomes:
			change = Change(type = Change.TYPE_PLOT)
			change.name = outcome.plot.name
			plot, created = CharacterPlot.objects.get_or_create(character = self, plot = outcome.plot)
			change.new = outcome.value
			plot.value = outcome.value
			plot.save()
			changes.append(change)

		self.total_choices = self.total_choices + 1
		self.save()
		return changes

class CharacterStat(models.Model):
	character = models.ForeignKey(Character)
	stat = models.ForeignKey(Stat)
	value = models.IntegerField(default=0)
	def level(self):
		return level_from_value(self.value)
	def __unicode__(self):
		return str(self.stat) + ":" + str(self.value) + ":" + str(self.level())

class CharacterPlot(models.Model):
	character = models.ForeignKey(Character)
	plot = models.ForeignKey(Plot)
	value = models.IntegerField(default=0)
	def __unicode__(self):
		return self.character.name + ":" + self.plot.name + ":" + str(self.value)

class CharacterItem(models.Model):
	character = models.ForeignKey(Character)
	item = models.ForeignKey(Item)
	quantity = models.IntegerField(default = 0)
	def __unicode__(self):
		return str(self.quantity) + " " + self.item.name

class Change(models.Model):
	TYPE_INCREMENT = 1
	TYPE_LEVEL = 2
	TYPE_MONEY = 3
	TYPE_PLOT = 4
	TYPE_ITEM = 5
	TYPE_HEALTH = 6
	TYPE_NO_ACTIONS = 7
	TYPE_CHOICES = (
		(TYPE_INCREMENT, "Increment"),
		(TYPE_LEVEL, "Level"),
		(TYPE_MONEY, "Money"),
		(TYPE_PLOT, "Plot"),
		(TYPE_ITEM, "Item"),
		(TYPE_HEALTH, "Health"),
		(TYPE_NO_ACTIONS, "Insufficient Actions"),
	)
	type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_INCREMENT)
	old = models.IntegerField()
	new = models.IntegerField()
	amount = models.IntegerField()
	name = models.CharField(max_length=100)
	def __unicode__(self):
		return self.name + " has changed from " + self.old + " to " + self.new + "."
