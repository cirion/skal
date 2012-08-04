from django.db import models

STAT_HUNTING = 1
STAT_STEALTH = 2
STAT_SWORDFIGHTING = 3
STAT_SAILING = 4
STAT_NAVIGATION = 5
STAT_CHOICES = (
		(STAT_HUNTING, "Hunting"),
		(STAT_STEALTH, "Stealth"),
		(STAT_SWORDFIGHTING, "Swordfighting"),
		(STAT_SAILING, "Sailing"),
		(STAT_NAVIGATION, "Navigation")
)

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
		if not pre_reqs:
			return True
		try:
			for pre_req in pre_reqs:
				character_stat = CharacterStat.objects.get(character=character.pk, stat=pre_req.stat)
				if character_stat.value < pre_req.minimum or character_stat.value > pre_req.maximum:
					return False
		except CharacterStat.DoesNotExist:
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
		if not pre_reqs:
			return True
		try:
			for pre_req in pre_reqs:
				character_stat = CharacterStat.objects.get(character=character.pk, stat=pre_req.stat)
				if character_stat.value < pre_req.minimum or character_stat.value > pre_req.maximum:
					return False
		except CharacterStat.DoesNotExist:
			return False
		return True
	
class ScenarioStatPreReq(models.Model):
	scenario = models.ForeignKey(Scenario)
	stat = models.IntegerField(choices=STAT_CHOICES)
	minimum = models.IntegerField(default=0)
	maximum = models.IntegerField(default=100)
	visible = models.BooleanField(default=True)
	def __unicode__(self):
		return str(self.stat)

class ChoiceStatPreReq(models.Model):
	choice = models.ForeignKey(Choice)
	stat = models.IntegerField(choices=STAT_CHOICES)
	minimum = models.IntegerField(default=0)
	maximum = models.IntegerField(default=100)
	visible = models.BooleanField(default=True)
	def __unicode__(self):
		return str(self.stat)
	
class Result(models.Model):
	choice = models.ForeignKey(Choice)
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=4000)
	def __unicode__(self):
		return self.title

class MoneyOutcome(models.Model):
	choice = models.ForeignKey(Result)
	amount = models.IntegerField()
	def __unicode__(self):
		return self.amount
	
class StatOutcome(models.Model):
	choice = models.ForeignKey(Result)
	stat = models.IntegerField(choices=STAT_CHOICES, default=STAT_SWORDFIGHTING)
	amount = models.IntegerField()
	def __unicode__(self):
		return str(self.stat)


class Player(models.Model):
	email = models.EmailField()
	created = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.email

class Character(models.Model):
	player = models.ForeignKey(Player)
	name = models.CharField(max_length=20)
	created = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.name

class CharacterStat(models.Model):
	character = models.ForeignKey(Character)
	stat = models.IntegerField(choices=STAT_CHOICES)
	value = models.IntegerField()
	def level(self):
		if self.value < 110:
			return self.value / 10;
		elif self.value > 5105:
			return 100 + (self.value - 5105) / 100;
		else:
			temp = self.value - 100
			level = 10
			while (temp > 0):
				++level
				temp -= level
			return level;
	def __unicode__(self):
		return str(self.stat) + ":" + str(self.value) + ":" + str(self.level())
