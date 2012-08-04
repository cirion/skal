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

class Choice(models.Model):
	scenario = models.ForeignKey(Scenario)
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=1000)
	def __unicode__(self):
		return self.title

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


