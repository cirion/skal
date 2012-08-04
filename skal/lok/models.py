from django.db import models

class Scenario(models.Model):
	title = models.CharField(max_length=100)
	image = models.CharField(max_length=200)
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

class MoneyOutcome(models.Model):
	choice = models.ForeignKey(Choice)
	amount = models.IntegerField()
	def __unicode__(self):
		return self.amount;
	
class StatOutcome(models.Model):
	choice = models.ForeignKey(Choice)
	stat = models.CharField(max_length=50)
	amount = models.IntegerField()
	def __unicode__(self):
		return self.stat


