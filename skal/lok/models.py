from django.db import models
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.contrib.auth.models import User
from lok.utils import level_from_value as level_from_value
from lok.utils import value_from_level as value_from_level
import random
from random import Random
import logging
logger = logging.getLogger(__name__)

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
				if pre_req.value == 0 and ((CharacterPlot.objects.filter(character = character.pk, plot = pre_req.plot) and CharacterPlot.objects.get(character = character.pk, plot = pre_req.plot).value != 0)):
					return False
				elif pre_req.value > 0 and CharacterPlot.objects.get(character = character.pk, plot = pre_req.plot).value != pre_req.value:
					return False
		except CharacterPlot.DoesNotExist:
			return False
	return True

def valid_for_stat_pre_reqs(character, pre_reqs, enforceMax):
	if pre_reqs:
		try:
			for pre_req in pre_reqs:
				if pre_req.minimum > 0:
					character_stat = CharacterStat.objects.get(character=character.pk, stat=pre_req.stat)
					level = level_from_value(character_stat.value)
					level += character.stat_bonus(character_stat.stat)
					if level_from_value(level) < pre_req.minimum:
						return False
					elif enforceMax and level_from_value(character_stat.value) > pre_req.maximum:
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
			return False
	return True

def valid_for_level_pre_reqs(character, pre_reqs):
	if pre_reqs:
		if character.level() < pre_reqs[0].minimum:
			return False
	return True

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
		if not valid_for_stat_pre_reqs(character,pre_reqs, True):
			return False
		pre_reqs = ScenarioItemPreReq.objects.filter(scenario=self.pk)
		if not valid_for_item_pre_reqs(character,pre_reqs):
			return False
		pre_reqs = ScenarioPlotPreReq.objects.filter(scenario=self.pk)
		if not valid_for_plot_pre_reqs(character,pre_reqs):
			return False
		pre_reqs = ScenarioLevelPreReq.objects.filter(scenario=self.pk)
		if not valid_for_level_pre_reqs(character,pre_reqs):
			return False
		return True

class Battle(Scenario):
	ENEMY_SLASHING=1
	ENEMY_ARMORED=2
	ENEMY_RANGED=3
	TYPE_ENEMY = (
		(ENEMY_SLASHING, "Slashing"),
		(ENEMY_ARMORED, "Armored"),
		(ENEMY_RANGED, "Ranged"),
	)
	enemy = models.IntegerField(choices=TYPE_ENEMY)
	strength = models.IntegerField()

class Choice(models.Model):
	scenario = models.ForeignKey(Scenario)
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=1000)
	visible = models.BooleanField()
	def __unicode__(self):
		return self.title
	def valid_for(self, character):
		pre_reqs = ChoiceStatPreReq.objects.filter(choice=self.pk)
		if not valid_for_stat_pre_reqs(character,pre_reqs, False):
			return False
		pre_reqs = ChoiceItemPreReq.objects.filter(choice=self.pk)
		if not valid_for_item_pre_reqs(character,pre_reqs):
			return False
		pre_reqs = ChoicePlotPreReq.objects.filter(choice=self.pk)
		if not valid_for_plot_pre_reqs(character,pre_reqs):
			return False
		return True

class Plot(models.Model):
	MAX_LEVEL = 2
	name = models.CharField(max_length=100)
	visible = models.BooleanField(default=False)
	achievement = models.BooleanField(default = False)
	description = models.TextField(max_length=2000)
	def __unicode__(self):
		return self.name

class Item(models.Model):
	name = models.CharField(max_length=100)
	value = models.IntegerField(default=1)
	sellable = models.BooleanField(default=True)
	def __unicode__(self):
		return self.name

class Equipment(Item):
	TYPE_SWORD = 1
	TYPE_BASHING = 2
	TYPE_BOW = 3
	TYPE_FEET = 4
	TYPE_CLOAK = 5
	TYPE_CLOTHES = 6
	TYPE_GLOVES = 7
	TYPE_RING = 8
	TYPE_NECK = 9
	TYPE_ARMOR = 10
	TYPE_CHOICES = (
		(TYPE_SWORD, "Sword"),
		(TYPE_BASHING, "Bashing"),
		(TYPE_BOW, "Bow"),
		(TYPE_FEET, "Feet"),
		(TYPE_CLOAK, "Cloak"),
		(TYPE_CLOTHES, "Clothes"),
		(TYPE_GLOVES, "Gloves"),
		(TYPE_RING, "Ring"),
		(TYPE_NECK, "Neck"),
		(TYPE_ARMOR, "Armor")
	)
	type = models.IntegerField(choices=TYPE_CHOICES)
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

class EquipmentStat(models.Model):
	equipment = models.ForeignKey(Equipment)
	stat = models.ForeignKey(Stat)
	amount = models.IntegerField()
	def __unicode__(self):
		return str(self.amount) + " points of " + self.stat.name + " for " + self.equipment.name
	
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

class ScenarioLevelPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	minimum = models.IntegerField()
	maximum = models.IntegerField(default=1000)
	def __unicode__(self):
		return "Level " + str(self.minimum) + "-" + str(self.maximum)

class ChoicePlotPreReq(models.Model):
	choice = models.ForeignKey(Choice)
	plot = models.ForeignKey(Plot)
	value = models.IntegerField()
	def __unicode__(self):
		return self.plot.name + " " + str(self.value)

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
	def challenge(self, character):
		try:
			value = CharacterStat.objects.get(stat = self.stat).level()
		except CharacterStat.DoesNotExist:
			value = 0
		value += character.stat_bonus(self.stat)
		if value >= self.maximum:
			return True
		# Our odds of success are our progress between minimum and maximum.
		odds = float(value - self.minimum) / float(self.maximum - self.minimum)
		return random.random() < odds

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

def get_stat_bonus(item, stat):
	stats = EquipmentStat.objects.filter(equipment=item, stat=stat)
	bonus = 0
	for estat in stats:
		bonus += estat.amount
	return bonus

class Character(models.Model):
	MAX_ACTIONS = 20
	#ACTION_RECHARGE_TIME_SECS = 900
	ACTION_RECHARGE_TIME_SECS = 30
	player = models.ForeignKey(User)
	name = models.CharField(max_length=20,unique=True)
	created = models.DateTimeField(auto_now_add=True)
	money = models.IntegerField(default=0)
	gender = models.IntegerField(choices=GENDER_CHOICES)
	current_health = models.IntegerField()
	total_choices = models.IntegerField(default=0)
	actions = models.IntegerField(default=20)
	refill_time = models.DateTimeField()
	sword = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_SWORD}, null=True, blank=True, related_name='+')
	bashing = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_BASHING}, null=True, blank=True, related_name='+')
	bow = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_BOW}, null=True, blank=True, related_name='+')
	feet = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_FEET}, null=True, blank=True, related_name='+')
	cloak= models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_CLOAK}, null=True, blank=True, related_name='+')
	clothing= models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_CLOTHES}, null=True, blank=True, related_name='+')
	gloves = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_GLOVES}, null=True, blank=True, related_name='+')
	ring = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_RING}, null=True, blank=True, related_name='+')
	neck = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_NECK}, null=True, blank=True, related_name='+')
	armor = models.ForeignKey('Equipment', limit_choices_to={'type': Equipment.TYPE_ARMOR}, null=True, blank=True, related_name='+')
	def __unicode__(self):
		return self.name
	def stat_bonus(self, stat):
		bonus = 0
		bonus += get_stat_bonus(self.sword, stat)
		bonus += get_stat_bonus(self.bashing, stat)
		bonus += get_stat_bonus(self.bow, stat)
		bonus += get_stat_bonus(self.feet, stat)
		bonus += get_stat_bonus(self.cloak, stat)
		bonus += get_stat_bonus(self.clothing, stat)
		bonus += get_stat_bonus(self.gloves, stat)
		bonus += get_stat_bonus(self.ring, stat)
		bonus += get_stat_bonus(self.neck, stat)
		bonus += get_stat_bonus(self.armor, stat)
		return bonus
	def update_actions(self):
		while datetime.utcnow().replace(tzinfo=utc) > self.refill_time and self.actions < Character.MAX_ACTIONS:
			self.actions = self.actions + 1
			self.refill_time = self.refill_time + timedelta(0, Character.ACTION_RECHARGE_TIME_SECS)
		self.save()
	def odds_against(self, battle):
		sword_strength = 0
		bow_strength = 0
		bashing_strength=0
		if self.sword:
			sword_strength=self.stat_bonus(Stat.objects.get(name="Swordfighting"))
			if CharacterStat.objects.filter(character=self, stat__name="Swordfighting"):
				sword_strength += level_from_value(CharacterStat.objects.get(character=self, stat__name="Swordfighting").value)
		if self.bow:
			bow_strength=self.stat_bonus(Stat.objects.get(name="Archery"))
			
			if CharacterStat.objects.filter(character=self, stat__name="Archery"):
				bow_strength += level_from_value(CharacterStat.objects.get(character=self, stat__name="Archery").value)
		# Unlike bows and swords, we can use bashing even without an item equipped.
		if self.bashing:
			bashing_strength += self.bashing.amount
		if CharacterStat.objects.filter(character=self, stat__name="Bashing"):
			bashing_strength += level_from_value(CharacterStat.objects.get(character=self, stat__name="Bashing").value)
		best_strength = 0
		weapon = None
		if bow_strength >= sword_strength and bow_strength >= bashing_strength:
			best_strength = bow_strength
			weapon = self.bow
		elif sword_strength >= bow_strength and sword_strength >= bashing_strength:
			best_strength = bow_strength
			weapon = self.sword
		else:
			best_strength = bashing_strength
			weapon = self.bashing
		# Phew! Now, calculate the delta!
		odds = .5 + 0.05 * (best_strength - battle.strength)
		# Can play around with this, but I think there's always a 5% chance of success or failure. (Nice D20 odds.)
		if odds < .05:
			odds = .05
		elif odds > .95:
			odds = .95
		return {'odds': odds, 'weapon': weapon}
	def max_health(self):
		# Need to figure out how to grow this...
		best_stat = CharacterStat.objects.all().order_by('-value')[0]
		return level_from_value(best_stat.value)
	def level(self):
		best_stat = CharacterStat.objects.all().order_by('-value')[0]
		return level_from_value(best_stat.value)
	def update_with_result(self, result, pre_reqs):
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
				oldvalue = stat.value
				change.name = stat.stat.name
				# If we succeeded using a maxed stat, it can only increase by 1 point.
				if (pre_reqs.filter(stat=outcome.stat) and pre_reqs.get(stat=outcome.stat).maximum <= oldlevel):
					stat.value += 1
				else:
					stat.value += outcome.amount
				change.amount = stat.value - oldvalue
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
