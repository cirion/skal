from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from lok.models import Scenario, Choice, Character, Player, MoneyOutcome, StatOutcome, ScenarioStatPreReq, ChoiceStatPreReq
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
