from datetime import datetime, timedelta
import bisect
from django.utils.timezone import utc
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template import Context, loader
from lok.models import Scenario, Choice, Character, MoneyOutcome, StatOutcome, ScenarioStatPreReq, ChoiceStatPreReq, Result, CharacterStat, CharacterItem, Stat, ChoiceItemPreReq, ChoiceMoneyPreReq
import random
from random import Random
from lok.models import GENDER_MALE as GENDER_MALE
from lok.utils import level_from_value as level_from_value

@login_required
def create_character(request):
	if (request.POST):
		name = request.POST['name']
		if Character.objects.filter(name=name).exists():
			return render_to_responds('lok/create_character.html', {'error': "Sorry, that name is already taken."})
		character = Character()
		character.name = name
		character.player = request.user
		character.money = 0
		character.gender = request.POST['gender']
		character.save()
		return HttpResponseRedirect('/lok/story/')
	return render_to_response('lok/create_character.html', {}, context_instance=RequestContext(request))

@login_required
def character(request):
	current_character = Character.objects.get(player=request.user.id)
	skills = list(CharacterStat.objects.filter(character = current_character, stat__type= Stat.TYPE_SKILL))
	for skill in skills:
		skill.value = level_from_value(skill.value)
	items = CharacterItem.objects.all()
	fame = level_from_value(CharacterStat.objects.filter(character = current_character, stat__type= Stat.TYPE_FAME)[0].value)
	esteems = CharacterStat.objects.filter(character = current_character, stat__type = Stat.TYPE_ESTEEM)
	for esteem in esteems:
		esteem.value = level_from_value(esteem.value)
	if current_character.gender == GENDER_MALE:
		title = "Mr."
	else:
		title = "Ms."
	return render_to_response('lok/character.html', {'character': current_character, 'skills': skills, 'fame': fame, 'items': items, 'title': title})

@login_required
def story(request):
	if not Character.objects.filter(player=request.user.id):
		return HttpResponseRedirect('/lok/create/')
	current_character = Character.objects.get(player=request.user.id)
	current_character.update_actions()
	scenarios = list(Scenario.objects.all())
	pseudo = Random()
	pseudo.seed(current_character.total_choices)
	pseudo.shuffle(scenarios)
	max_scenarios = 10
	out_scenarios = list()
	while (len(out_scenarios) < max_scenarios and scenarios):
		scenario = scenarios.pop(0)
		if (scenario.valid_for(current_character)):
			out_scenarios.append(scenario)
	return render_to_response('lok/story.html', {'scenarios': out_scenarios, 'actions': current_character.actions})

def check_auth(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
    	if user is not None:
        	if user.is_active:
            		login(request, user)
			return HttpResponseRedirect('/lok/story/')
        	else:
			return HttpResponseRedirect('/lok/disabled.html')
    	else:
		return render_to_response('lok/login.html', {'failure': True})

@login_required
def scenario(request, scenario_id):
	scenario = Scenario.objects.get(pk=scenario_id)
	current_character = Character.objects.get(player=request.user.id)
	choices = list(Choice.objects.filter(scenario=scenario_id))
	for choice in choices:
		if not choice.valid_for(current_character) and not choice.visible:
			choices.remove(choice)
		else:
			if not choice.valid_for(current_character):
				choice.invalid = True
			choice.required_items = ChoiceItemPreReq.objects.filter(choice=choice.pk)
			choice.required_stats = ChoiceStatPreReq.objects.filter(choice=choice.pk,minimum__gt=0)
			if (ChoiceMoneyPreReq.objects.filter(choice=choice.pk)):
				choice.required_money = ChoiceMoneyPreReq.objects.get(choice=choice.pk)
	return render_to_response('lok/scenario.html', {'scenario': scenario, 'choices': choices}, context_instance=RequestContext(request))
	

@login_required
def result(request, result_id):
	result = Result.objects.get(pk=result_id)
	# Storing changes in the session so we can report on what happened after we're redirected from the POST. This basically lets us (a) protect against multiple submissions, and (b) give useful feedback even if the page load was interrupted. In a production environment, we'd need to more carefully monitor what data we're keeping in session and clear it out after they move on to another page.
	changes = request.session.get('changes')
	return render_to_response('lok/result.html', {'result': result, 'changes': changes})

@login_required
def choice(request, choice_id):
	current_character = Character.objects.get(player=request.user.id)
	current_character.update_actions()
	if current_character.actions < 1:
		return render_to_response('lok/wait.html', {'time': (current_character.refill_time - datetime.utcnow().replace(tzinfo=utc)).seconds})
	choice = Choice.objects.get(pk=choice_id)
	# TODO: Just 1 now, but will have multiples in the next phase, and will need to pick outcome (success, failure, rare success)
	successes = Result.objects.filter(choice=choice.pk, type=Result.SUCCESS)
	failures = Result.objects.filter(choice=choice.pk, type=Result.FAILURE)
	# Check to see if this is a challenge, and if so, if there are any failures.
	stat_pre_reqs = ChoiceStatPreReq.objects.filter(choice=choice.pk)
	failed = False
	if (stat_pre_reqs and failures):
		for stat_pre_req in stat_pre_reqs:
			if not stat_pre_req.challenge(current_character):
				failed = True
	if failed:
		results = failures
	else:
		results = successes
	# If there are multiple successes/failures, choose the appropriate one based on its weight.
	if len(results) == 1:
		result = results[0]
	elif len(results) > 1:
		result = results[weighted_choice(results)]
	response = HttpResponseRedirect(reverse('lok.views.result', args=(result.id,)))
	changes = current_character.update_with_result(result,stat_pre_reqs)
	request.session['changes'] = changes
	return response

def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w.weight
        totals.append(running_total)

    rnd = random.random() * running_total
    return bisect.bisect_right(totals, rnd)
