from django.db import models
from datetime import datetime, timedelta
from django.utils.timezone import utc
from django.contrib.auth.models import User
from lok.utils import level_from_value as level_from_value
from lok.utils import value_from_level as value_from_level
import random
from random import Random
import logging
from imagekit.models import ImageSpecField 
from imagekit.processors import ResizeToFill, Adjust, ResizeToFit, AddBorder

logger = logging.getLogger(__name__)

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

def valid_for_money_pre_req(character, pre_reqs):
	if pre_reqs:
		if pre_reqs[0].amount > character.money:
			return False
	return True

def valid_for_location_known_pre_reqs(character, pre_reqs):
	if pre_reqs:
		try:
			for pre_req in pre_reqs:
				if (CharacterLocationAvailable.objects.get(character=character.pk, location=pre_req.location) and not pre_req.known):
					return False
		except CharacterLocationAvailable.DoesNotExist:
			if pre_req.known:
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
					#print "For stat " + character_stat.stat.name + " comparing " + str(level) + ":" + str(level_from_value(level)) + " to " + str(pre_req.minimum)
					if level < pre_req.minimum:
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

class Image(models.Model):
	title = models.CharField(max_length=100)
	alt = models.CharField(max_length=500)
	contributor = models.CharField(max_length=100,blank=True,null=True)
	contributor_link = models.CharField(max_length=200,blank=True,null=True)
	image = models.ImageField(upload_to='images')
	thumbnail = ImageSpecField([ResizeToFill(50, 50)], image_field='image', format='JPEG', options={'quality': 90})
	# Hrm... I wanted to add a colored border around this, but I can't seem to make it show as any color other than white. Can revisit later.
	scaled = ImageSpecField([ResizeToFit(400, 1000), AddBorder(0)], image_field='image', format='JPEG', options={'quality': 90})
	def __unicode__(self):
		return self.title

class Scenario(models.Model):
	title = models.CharField(max_length=100)
	portrait = models.ForeignKey(Image, null=True, blank=True)
	description = models.TextField(max_length=2000)
	weight = models.IntegerField(default=10000)
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
		# Special case, for my own sanity/convenience: if you're in a special location, you only get the scenarios specific to that place.
		if character.location.type == Location.TYPE_NONE and not ScenarioLocationPreReq.objects.filter(scenario=self.pk):
			return False
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
		if ScenarioLocationPreReq.objects.filter(scenario=self.pk) and ScenarioLocationPreReq.objects.get(scenario=self.pk).location != character.location:
			return False
		if ScenarioLocationTypePreReq.objects.filter(scenario=self.pk):
			if ScenarioLocationTypePreReq.objects.get(scenario=self.pk).type != character.location.type:
				return False
		pre_reqs = ScenarioLocationKnownPreReq.objects.filter(scenario=self.pk)
		if not valid_for_location_known_pre_reqs(character, pre_reqs):
			return False
		if ScenarioHealthPreReq.objects.filter(scenario=self.pk):
			health = ScenarioHealthPreReq.objects.get(scenario=self.pk)
			if health.full and character.current_health < character.max_health():
				return False
			elif not health.full and character.current_health == character.max_health():
				return False
		return True

class Battle(Scenario):
	ENEMY_SLASHING=1
	ENEMY_BASHING=2
	ENEMY_RANGED=3
	TYPE_ENEMY = (
		(ENEMY_SLASHING, "Slashing"),
		(ENEMY_BASHING, "Bashing"),
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
		pre_reqs = ChoiceMoneyPreReq.objects.filter(choice=self.pk)
		if not valid_for_money_pre_req(character, pre_reqs):
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
	class Meta:
		ordering = ['-id']

class PlotDescription(models.Model):
	plot = models.ForeignKey(Plot)
	value = models.IntegerField()
	description = models.TextField(max_length=2000)
	def __unicode__(self):
		return self.plot.name + ": " + self.description

class Item(models.Model):
	name = models.CharField(max_length=100)
	value = models.IntegerField(default=1)
	sellable = models.BooleanField(default=True)
	multiple = models.BooleanField(default=True)
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
	def __init__(self, *args, **kwargs):
    		if 'multiple' not in kwargs:
        		kwargs['multiple'] = False
    		super(Item, self).__init__(*args, **kwargs)
	type = models.IntegerField(choices=TYPE_CHOICES)
	def __unicode__(self):
		return self.name

class Stat(models.Model):
	TYPE_SKILL = 1
	TYPE_FAME = 2
	TYPE_ESTEEM = 3
	TYPE_CHARACTERISTIC = 4
	TYPE_PROGRESS = 5
	TYPE_CHOICES = (
		(TYPE_SKILL, "Skill"),
		(TYPE_FAME, "Fame"),
		(TYPE_ESTEEM, "Esteem"),
		(TYPE_CHARACTERISTIC, "Characteristic"),
		(TYPE_PROGRESS, "Progress"),
	)
	type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_PROGRESS)
	name = models.CharField(max_length=50)
	def __unicode__(self):
		return self.name

class EquipmentStat(models.Model):
	equipment = models.ForeignKey(Equipment)
	stat = models.ForeignKey(Stat)
	amount = models.IntegerField()
	def __unicode__(self):
		return str(self.amount) + " points of " + self.stat.name + " for " + self.equipment.name

class Location(models.Model):
	TYPE_CITY = 1
	TYPE_COUNTRY = 2
	TYPE_CAVE = 3
	TYPE_NONE = 4
	TYPE_CHOICES = (
		(TYPE_CITY, "City"),
		(TYPE_COUNTRY, "Country"),
		(TYPE_CAVE, "Cave"),
		(TYPE_NONE, "None"),
	)
	name = models.CharField(max_length=100, unique=True)
	type = models.IntegerField(choices=TYPE_CHOICES)
	def __unicode__(self):
		return self.name

class ScenarioLocationPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	location = models.ForeignKey(Location)
	def __unicode__(self):
		return self.location.name

class ScenarioLocationTypePreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	type = models.IntegerField(choices=Location.TYPE_CHOICES)
	def __unicode__(self):
		return Location.TYPE_CHOICES[self.type-1][1]

class ScenarioLocationKnownPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	location = models.ForeignKey(Location)
	known = models.BooleanField()
	def __unicode__(self):
		return self.location.name + " " + str(self.known)
	
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

class ScenarioHealthPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	full = models.BooleanField(default=False)
	def __unicode__(self):
		return "Full health: " + str(self.full)

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
	def odds(self, character):
		try:
			value = CharacterStat.objects.get(character=character, stat = self.stat).level()
		except CharacterStat.DoesNotExist:
			value = 0
		value += character.stat_bonus(self.stat)
		#print "Have " + str(value) + ", need " + str(self.maximum)
		if value >= self.maximum:
			return 1
		# Our odds of success are our progress between minimum and maximum.
		odds = float(value - self.minimum + 1) / float(self.maximum - self.minimum + 1)
		return odds
	def challenge(self, character):
		return random.random() < self.odds(character)

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
	portrait = models.ForeignKey(Image, null=True, blank=True)
	weight = models.IntegerField(default=1)
	choice = models.ForeignKey(Choice)
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=4000)
	
	def __unicode__(self):
		return self.title

class SetLocationOutcome(models.Model):
	choice = models.ForeignKey(Result)
	location = models.ForeignKey(Location)
	def __unicode__(self):
		return self.location.name

class LearnLocationOutcome(models.Model):
	choice = models.ForeignKey(Result)
	location = models.ForeignKey(Location)
	def __unicode__(self):
		return self.location.name

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

	
class LocationRoute(models.Model):
	origin = models.ForeignKey(Location, related_name='+')
	destination = models.ForeignKey(Location, related_name='+')
	def __unicode__(self):
		return self.origin.name + " -> " + self.destination.name

class RouteOption(models.Model):
	route = models.ForeignKey(LocationRoute)
	description = models.CharField(max_length=1000)
	def __unicode__(self):
		return self.route.__unicode__()
	def summary(self):
		return self.description

class RouteFree(RouteOption):
	def __unicode__(self):
		return self.route.__unicode__()

class RouteItemFree(RouteOption):
	item = models.ForeignKey(Item)
	def __unicode__(self):
		return self.route.__unicode__() + " : " + self.item.name
	def summary(self):
		return self.description + " This uses your " + self.item.name + "."

class RouteItemCost(RouteOption):
	item = models.ForeignKey(Item)
	amount = models.IntegerField()
	def __unicode__(self):
		return self.route.__unicode__() + " : " + str(self.amount) + " " + self.item.name
	def summary(self):
		return self.description + " This requires using " + str(self.amount) + " " + self.item.name + "s."

class RouteToll(RouteOption):
	amount = models.IntegerField()
	def __unicode__(self):
		return self.route.__unicode__() + " : " + str(self.amount) + " royals"
	def summary(self):
		return self.description + " The fee is " + str(self.amount) + " royals."

class Title(models.Model):
	raw_title_male = models.CharField(max_length=100)
	raw_title_female = models.CharField(max_length=100)
	def __unicode__(self):
		return self.raw_title_male + "/" + self.raw_title_female
	def title(self, character):
		if character.gender == Character.GENDER_FEMALE:
			return self.raw_title_female.replace("#NAME#", character.name)
		else:
			return self.raw_title_male.replace("#NAME#", character.name)

class Party(models.Model):
	def leader(self):
		members = sorted(Character.objects.filter(party=self), key=lambda a: a.max_party_size)
		if not members:
			return None
		return members[0]
	def member(self, character):
		return Character.objects.filter(party=self,pk=character.id).exists()
	def members(self):
		return Character.objects.filter(party=self)
	def odds_against(self, battle):
		odds_result = None
		for member in self.members():
			result = member.odds_against(battle)
			if not odds_result or result['odds'] > odds_result['odds']:
				result['character'] = member
				odds_result = result
		return odds_result
	def size(self):
		return self.members().count()
	def max_size(self):
		size = 1
		for member in self.members():
			member_size = member.max_party_size()
			if member_size > size:
				size = member_size
		return size
	def __unicode__(self):
		if not self.leader():
			return "Empty party"
		return self.leader().title_name() + "'s party"

class Character(models.Model):
	GENDER_FEMALE = 1
	GENDER_MALE = 2
	GENDER_CHOICES = (
		(GENDER_FEMALE, "Female"),
		(GENDER_MALE, "Male"),
	)
	CONTACT_YES = 2
	CONTACT_NO = 1
	CONTACT_CHOICES = (
		(CONTACT_YES, "Yes"),
		(CONTACT_NO, "No"),
	)
	MAX_ACTIONS = 20
	ACTION_RECHARGE_TIME_SECS = 900
	player = models.ForeignKey(User)
	party = models.ForeignKey(Party)
	contact = models.IntegerField(choices=CONTACT_CHOICES, default=CONTACT_YES)
	name = models.CharField(max_length=20,unique=True)
	created = models.DateTimeField(auto_now_add=True)
	money = models.IntegerField(default=0)
	gender = models.IntegerField(choices=GENDER_CHOICES)
	current_health = models.IntegerField()
	total_choices = models.IntegerField(default=0)
	actions = models.IntegerField(default=20)
	refill_time = models.DateTimeField()
	recharge_delay_secs = models.IntegerField(default=900)
	location = models.ForeignKey(Location)
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
	active_title = models.ForeignKey(Title, null=True, blank=True)
	def __unicode__(self):
		return self.name
	def title_name(self):
		if self.active_title:
			return self.active_title.title(self)
		else:
			return self.name
	def max_party_size(self):
		# I'm gonna play around with this... may also expand based on land ownership, renown, etc.
		size = 1
		try:
			skill_value = CharacterStat.objects.get(character=self, stat__name="Persuasion").level()
		except CharacterStat.DoesNotExist:
			skill_value = 0
		skill_value+= self.stat_bonus(Stat.objects.get(name="Persuasion"))
		if skill_value > 20:
			size += 1
		if skill_value > 40:
			size += 1
		if skill_value > 60:
			size += 1
		try:
			renown_value = CharacterStat.objects.get(character=self, stat__name="Renown").level()
		except CharacterStat.DoesNotExist:
			renown_value = 0
		if renown_value > 10:
			size += 1
		return size
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
	def rest(self):
		self.update_actions()
		if self.actions == Character.MAX_ACTIONS:
			self.refill_time = datetime.utcnow().replace(tzinfo=utc) + timedelta(0, self.recharge_delay_secs)
		if self.actions > 0:
			self.actions -= 1
			self.save()
			self.total_choices += 1
			self.save()
	def update_actions(self):
		while datetime.utcnow().replace(tzinfo=utc) > self.refill_time and self.actions < Character.MAX_ACTIONS:
			self.actions = self.actions + 1
			self.refill_time = self.refill_time + timedelta(0, self.recharge_delay_secs)
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
		if battle.enemy == Battle.ENEMY_RANGED:
			sword_strength = sword_strength - (5 + .1 * sword_strength)
			bashing_strength = bashing_strength + (5 + .1 * bashing_strength)
		elif battle.enemy == Battle.ENEMY_BASHING:
			sword_strength = sword_strength + (5 + .1 * sword_strength)
			bow_strength = bow_strength - (5 + .1 * bow_strength)
		else:
			bow_strength = bow_strength + (5 + .1 * bow_strength)
			bashing_strength = bashing_strength - (5 + .1 * bashing_strength)
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
		amount = 0
		stats = CharacterStat.objects.filter(character=self, stat__type=Stat.TYPE_SKILL).order_by('-value')
		if stats:
			best_stat = stats[0]
			amount = level_from_value(best_stat.value)
		if amount < 10:
			amount = 10
		return amount
	def level(self):
		best_stat = CharacterStat.objects.filter(character=self, stat__type=Stat.TYPE_SKILL).order_by('-value')[0]
		return level_from_value(best_stat.value)
	def update_with_result(self, result, pre_reqs, battle, block_death):
		changes = list()
		if self.actions == Character.MAX_ACTIONS:
			self.refill_time = datetime.utcnow().replace(tzinfo=utc) + timedelta(0, self.recharge_delay_secs)
		self.actions = self.actions - 1

		if battle:
			# Increment the appropriate weapon skills. Always get 2pts in current weapon if it's a challenge, 1pt if it's easy (or someone else is fighting for us)
			odds = self.party.odds_against(battle)
			if odds['odds'] > 1 or odds['character'] != self:
				amount = 1
			else:
				amount = 2
			if odds['weapon'] == self.sword:
				stat = Stat.objects.get(name="Swordfighting")
			elif odds['weapon'] == self.bow:
				stat = Stat.objects.get(name="Archery")
			else:
				stat = Stat.objects.get(name="Bashing")
			if (not CharacterStat.objects.filter(character=self,stat=stat)):
				charstat = CharacterStat(character=self, stat=stat, value=0)
			else:
				charstat = CharacterStat.objects.get(character=self, stat=stat)
			change = Change(type=Change.TYPE_INCREMENT)
			change.name = stat.name
			change.old = charstat.value
			change.amount = amount
			charstat.value += amount
			change.new = charstat.value
			charstat.save()
			changes.append(change)

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
				if stat.value < 0:
					stat.value = 0
				change.amount = stat.value - oldvalue
				newlevel = level_from_value(stat.value)
				stat.save()
				if oldlevel != newlevel:
					change.type = Change.TYPE_LEVEL
					change.old = oldlevel
					change.new = newlevel
					change.amount = newlevel - oldlevel
					# ... and give them a free health point if they can use it. Note that we [currently] don't refill all health.
					if self.current_health < self.max_health():
						self.current_health += 1
						self.save()
				else:
					change.old = value_from_level(oldlevel + 1) - stat.value
					change.new = oldlevel + 1
				changes.append(change)

		money_outcomes = MoneyOutcome.objects.filter(choice = result.pk)
		for outcome in money_outcomes:
			share = outcome.amount
			if battle and self.party.size() > 1:
				# Divide money among the team.
				share = (int)((outcome.amount * 1.25) / self.party.size())
				for player in self.party.members():
					if player != self:
						player.money += share
						player.save()
						notice = SocialMessage(to_character=player, description = "You received " + str(share) + " royals from " + self.title_name() + "'s battle with " + battle.title + ".")
						notice.save()
			change = Change(type = Change.TYPE_MONEY)
			change.old = self.money
			self.money += share
			if outcome.amount == 1:
				change.name = "royal"
			else:
				change.name = "royals"
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
			item.quantity += outcome.amount
			if item.quantity < 0:
				item.quantity = 0
			change.new = item.quantity
			change.amount = change.new - change.old
			item.save()
			changes.append(change)

		health_outcomes = HealthOutcome.objects.filter(result = result.pk)
		for outcome in health_outcomes:
			change = Change(type = Change.TYPE_HEALTH)
			change.name = "health"
			change.old = self.current_health

			# If this was a fight, we have two chances to mitigate damage done. First dodge, then absorb.
			if battle:
				dodge_chance = self.stat_bonus(Stat.objects.get(name="Dodging"))
				if CharacterStat.objects.filter(character=self, stat__name="Dodging"):
					dodge_chance += level_from_value(CharacterStat.objects.get(character=self, stat__name="Dodging").value)
			# Hard cap at 80% dodge rate. Should probably eventually turn this to a soft cap that kicks in much earlier. We also check on stat increase, but need to keep a check here as well to prevent someone reaching 100% through use of equipment.
				if dodge_chance > 80:
					dodge_chance = 80
				if random.random() * 100 < dodge_chance:
						# They dodged it! No damage done. Let them know how lucky they are.
						changes.append(Change(type=Change.TYPE_DODGE))
						outcome.amount = 0
	
				# Next, let them absorb the blow if they have armor.
				armor_rating = self.stat_bonus(Stat.objects.get(name="Armor"))
				if (armor_rating > 40):
					armor_rating = 40
				old_outcome = outcome.amount
				outcome.amount = int(outcome.amount * (1.0 - float(armor_rating) * 2))
				if old_outcome != outcome.amount:
					changes.append(Change(type=Change.TYPE_ABSORBED, amount=old_outcome - outcome.amount))
	
				# See if they lucked out and gained an increase in dodge rating.
				if dodge_chance < self.level():
					# Definitely play around with this! Right now I'm thinking the odds of a dodge increase will range between 1-5%, depending on the ratio between the character's stealth, deviousness and their level.
					max_dodgy = 0
					if (CharacterStat.objects.filter(character=self, stat__name="Deviousness")):
						max_dodgy=level_from_value(CharacterStat.objects.get(character=self,stat__name="Deviousness").value)
					if (CharacterStat.objects.filter(character=self, stat__name="Stealth")):
						stealthy=level_from_value(CharacterStat.objects.get(character=self,stat__name="Stealth").value)
						if stealthy > max_dodgy:
							max_dodgy = stealthy
					odds = 0.01 + (0.04 * (max_dodgy/self.level()))
					if random.random() < odds:
						# Congrats! You just got better at dodging!
						dodgechange = Change(type=Change.TYPE_INCREMENT)
						dodgechange.name = "Dodging"
						if not CharacterStat.objects.filter(character=self, stat__name="Dodging"):
							dodgechange.old = 0
							stat = CharacterStat(character=self, stat=Stat.objects.get(name="Dodging"), value=10)
							stat.save()
						else:
							stat = CharacterStat.objects.get(character=self, stat__name="Dodging")
							dodgechange.old = stat.value
							stat.value += 10
							stat.save()
						dodgechange.amount = 10
						dodgechange.new = stat.value
						changes.append(dodgechange)
					
			self.current_health += outcome.amount
			if (self.current_health < 1 and block_death):
				self.current_health = 1
			elif (self.current_health < 0):
				self.current_health = 0
			elif (self.current_health > self.max_health()):
				self.current_health = self.max_health()
			if (self.current_health != change.old):
				change.new = self.current_health
				change.amount = change.new - change.old
				changes.append(change)

		plot_outcomes = PlotOutcome.objects.filter(result = result.pk)
		for outcome in plot_outcomes:
			change = Change(type = Change.TYPE_PLOT)
			change.name = outcome.plot.description
			plot, created = CharacterPlot.objects.get_or_create(character = self, plot = outcome.plot)
			change.new = outcome.value
			plot.value = outcome.value
			plot.save()
			if plot.plot.achievement:
				changes.append(change)

		location_learn_outcomes = LearnLocationOutcome.objects.filter(choice = result.pk)
		for outcome in location_learn_outcomes:
			change = Change(type = Change.TYPE_LOCATION_LEARNED)
			change.name = outcome.location.name
			location, created = CharacterLocationAvailable.objects.get_or_create(character = self, location = outcome.location)
			location.save()
			changes.append(change)

		if SetLocationOutcome.objects.filter(choice=result.pk):
			outcome = SetLocationOutcome.objects.get(choice=result.pk)
			change = Change(type = Change.TYPE_LOCATION_CHANGED)
			change.name = outcome.location.name
			self.location = outcome.location
			changes.append(change)

		self.total_choices = self.total_choices + 1
		self.save()
		return changes

class PartyInvite(models.Model):
	from_character = models.ForeignKey(Character, related_name="party_invite_from")
	to_character = models.ForeignKey(Character, related_name="party_invite_to")
	party = models.ForeignKey(Party)
	def __unicode__(self):
		return "Invite from " + self.from_character.name + " to " + self.to_character.name

class CharacterLocationAvailable(models.Model):
	character = models.ForeignKey(Character)
	location = models.ForeignKey(Location)
	def __unicode__(self):
		return self.location.name

class CharacterTitle(models.Model):
	character = models.ForeignKey(Character)
	title = models.ForeignKey(Title)
	def __unicode__(self):
		return self.title.title(self.character)

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
	TYPE_OUTCOME = 8
	TYPE_DODGE = 9
	TYPE_ABSORBED = 10
	TYPE_WEAPON = 11
	TYPE_ENEMY = 12
	TYPE_LOCATION_LEARNED = 13
	TYPE_LOCATION_CHANGED = 14
	TYPE_ALLY = 15
	TYPE_CHOICES = (
		(TYPE_INCREMENT, "Increment"),
		(TYPE_LEVEL, "Level"),
		(TYPE_MONEY, "Money"),
		(TYPE_PLOT, "Plot"),
		(TYPE_ITEM, "Item"),
		(TYPE_HEALTH, "Health"),
		(TYPE_NO_ACTIONS, "Insufficient Actions"),
		(TYPE_OUTCOME, "Outcome"),
		(TYPE_DODGE, "Dodge"),
		(TYPE_ABSORBED, "Absorbed"),
		(TYPE_WEAPON, "Weapon Used"),
		(TYPE_ENEMY, "Enemy"),
		(TYPE_LOCATION_LEARNED, "Learned Location"),
		(TYPE_LOCATION_CHANGED, "Moved To Location"),
		(TYPE_ALLY, "Ally"),
	)
	type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_INCREMENT)
	old = models.IntegerField()
	new = models.IntegerField()
	amount = models.IntegerField()
	name = models.CharField(max_length=100)
	def __unicode__(self):
		return self.name + " has changed from " + self.old + " to " + self.new + "."

class ItemLocation(models.Model):
	item = models.ForeignKey(Item)
	location = models.ForeignKey(Location)
	def __unicode__(self):
		return self.item.name + " in " + self.location.name

class SocialMessage(models.Model):
	to_character = models.ForeignKey(Character)
	created = models.DateTimeField(auto_now_add=True)
	description = models.CharField(max_length=1000)
	def __unicode__(self):
		return "To " + to_character.name + ": " + description
