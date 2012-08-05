from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template import Context, loader
from lok.models import Scenario, Choice, Character, MoneyOutcome, StatOutcome, ScenarioStatPreReq, ChoiceStatPreReq, Result
import random

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
	skills = CharacterStats.objects.filter(character = current_character, type = Stat.TYPE_SKILL)
	fame = CharacterStats.objects.filter(character = current_character, type = Stat.TYPE_FAME)
	return render_to_response('lok/character.html', {'character': current_character, 'skills': skills, 'fame': fame})

@login_required
def story(request):
	if not Character.objects.filter(player=request.user.id):
		return HttpResponseRedirect('/lok/create/')
	current_character = Character.objects.get(player=request.user.id)
	scenarios = list(Scenario.objects.all())
	random.shuffle(scenarios)
	max_scenarios = 2
	out_scenarios = list()
	while (len(out_scenarios) < max_scenarios and scenarios):
		scenario = scenarios.pop(0)
		if (scenario.valid_for(current_character)):
			out_scenarios.append(scenario)
	return render_to_response('lok/story.html', {'scenarios': out_scenarios})

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
		if (not choice.valid_for(current_character) and not choice.visible):
			choices.remove(choice)
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
	choice = Choice.objects.get(pk=choice_id)
	# TODO: Just 1 now, but will have multiples in the next phase, and will need to pick outcome (success, failure, rare success)
	result = Result.objects.get(choice=choice.pk)
	response = HttpResponseRedirect(reverse('lok.views.result', args=(result.id,)))
	changes = current_character.update_with_result(result)
	request.session['changes'] = changes
	return response

