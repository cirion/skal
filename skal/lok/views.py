from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from lok.models import Scenario, Choice, Character, Player, MoneyOutcome, StatOutcome, ScenarioStatPreReq, ChoiceStatPreReq, Result
import random

def story(request):
	current_character = Character.objects.get(name="Cirion")
	scenarios = list(Scenario.objects.all())
	random.shuffle(scenarios)
	max_scenarios = 2
	out_scenarios = list()
	while (len(out_scenarios) < max_scenarios and scenarios):
		scenario = scenarios.pop(0)
		if (scenario.valid_for(current_character)):
			out_scenarios.append(scenario)
	return render_to_response('lok/story.html', {'scenarios': out_scenarios})

def scenario(request, scenario_id):
	scenario = Scenario.objects.get(pk=scenario_id)
	current_character = Character.objects.get(name="Cirion")
	choices = list(Choice.objects.filter(scenario=scenario_id))
	for choice in choices:
		if (not choice.valid_for(current_character) and not choice.visible):
			choices.remove(choice)
	return render_to_response('lok/scenario.html', {'scenario': scenario, 'choices': choices})
	

def choice(request, choice_id):
	current_character = Character.objects.get(name="Cirion")
	choice = Choice.objects.get(pk=choice_id)
	# TODO: Just 1 now, but will have multiples in the next phase, and will need to pick outcome (success, failure, rare success)
	result = Result.objects.get(choice=choice.pk)
	changes = current_character.update_with_result(result)
	return render_to_response('lok/result.html', {'result': result, 'changes': changes})

