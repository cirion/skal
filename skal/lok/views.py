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
from lok.models import Scenario, Choice, Character, MoneyOutcome, StatOutcome, ScenarioStatPreReq, ChoiceStatPreReq, Result, CharacterStat, CharacterItem, Stat, ChoiceItemPreReq, ChoiceMoneyPreReq, ChoicePlotPreReq, CharacterPlot, Plot, Equipment, EquipmentStat, Battle, Change, RouteFree, RouteToll, RouteItemCost, RouteItemFree, LocationRoute, CharacterLocationAvailable, RouteOption
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
		skill.value = level_from_value(skill.value) + current_character.stat_bonus(skill.stat)
	plots = CharacterPlot.objects.filter(character = current_character, plot__visible = True, plot__achievement = False, value__lt = Plot.MAX_LEVEL)
	achievements = CharacterPlot.objects.filter(character = current_character, plot__achievement = True)
	items = CharacterItem.objects.filter(character = current_character)
	fame = level_from_value(CharacterStat.objects.filter(character = current_character, stat__type= Stat.TYPE_FAME)[0].value)
	esteems = CharacterStat.objects.filter(character = current_character, stat__type = Stat.TYPE_ESTEEM)
	for esteem in esteems:
		esteem.value = level_from_value(esteem.value)
	if current_character.gender == GENDER_MALE:
		title = "Mr."
	else:
		title = "Ms."
	swords = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_SWORD)
	bashing = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_BASHING)
	bows = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_BOW)
	feet = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_FEET)
	cloaks = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_CLOAK)
	clothes = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_CLOTHES)
	gloves = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_GLOVES)
	rings = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_RING)
	neck = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_NECK)
	armors = CharacterItem.objects.filter(character = current_character, item__equipment__type = Equipment.TYPE_ARMOR)
	return render_to_response('lok/character.html', {'character': current_character, 'skills': skills, 'fame': fame, 'items': items, 'plots': plots, 'achievements': achievements, 'title': title, 'swords': swords, 'bashing': bashing, 'bows': bows, 'feet': feet, 'cloaks': cloaks, 'clothes': clothes, 'gloves': gloves, 'rings': rings, 'neck': neck, 'armors': armors})

@login_required
def story(request):
	if not Character.objects.filter(player=request.user.id):
		return HttpResponseRedirect('/lok/create/')
	current_character = Character.objects.get(player=request.user.id)
	current_character.update_actions()
	scenarios = list(Scenario.objects.all())

	max_scenarios = 5
	out_scenarios = list()
	pseudo = Random()
	pseudo.seed(current_character.total_choices)
	for scenario in random_weighted_sample_no_replacement(scenarios, pseudo, len(scenarios)):
		if (scenario.valid_for(current_character)):
			out_scenarios.append(scenario)
		if len(out_scenarios) >= max_scenarios:
			break

	"""
	pseudo.shuffle(scenarios)"""

	#while (len(out_scenarios) < max_scenarios and scenarios):
	#	scenario = scenarios.pop(0)
	routes = get_routes(current_character)
	return render_to_response('lok/story.html', {'routes': routes, 'scenarios': out_scenarios, 'actions': current_character.actions, 'character': current_character})

def get_routes(current_character):
	routes = list(LocationRoute.objects.filter(origin = current_character.location))
	approved_routes = list()
	for route in routes:
		print "Looking at " + route.__unicode__()
		route_found = False
		if CharacterLocationAvailable.objects.filter(character=current_character,location=route.destination):
				if RouteFree.objects.filter(route=route):
					approved_routes.append(RouteFree.objects.get(route=route))
					route_found = True
				else:
					print "Not free."
					if (RouteItemFree.objects.filter(route=route)):
						item = RouteItemFree.objects.get(route=route)
						print "Found item " + item.item.name
						if CharacterItem.objects.filter(character=current_character,item=item.item):
							approved_routes.append(RouteItemFree.objects.get(route=route))
							route_found = True
				if not route_found:
					# If there wasn't a free option, list any available pay options.
					if RouteToll.objects.filter(route=route):
						if (RouteToll.objects.get(route=route).amount <= current_character.money):
							approved_routes.append(RouteToll.objects.get(route=route))
					for cost in RouteItemCost.objects.filter(route=route):
							item = cost.item
							amount = cost.amount
							try:
								if CharacterItem.objects.get(character=current_character,item=item).quantity >= amount:
									approved_routes.append(cost)
							except Exception:
								pass
	return approved_routes

@login_required
def travel(request):
	current_character = Character.objects.get(player=request.user.id)
	approved_routes = get_routes(current_character)
	return render_to_response('lok/travel.html', {'character': current_character, 'routes': approved_routes}, context_instance=RequestContext(request))

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
def battle(request, battle_id):
	battle = Battle.objects.get(pk=battle_id)
	current_character = Character.objects.get(player=request.user.id)
	odds_result = current_character.odds_against(battle)
	odds = odds_result['odds']
	weapon = odds_result['weapon']
	choice = Choice.objects.get(scenario=battle)
	successes = Result.objects.filter(choice=choice.pk, type=Result.SUCCESS)
	failures = Result.objects.filter(choice=choice.pk, type=Result.FAILURE)
	success = False
	results = failures
	# First, check to see if they succeeded or not.
    	if random.random() < odds:
		success = True
		results = successes
	if len(results) == 1:
		result = results[0]
	elif len(results) > 1:
		result = results[weighted_choice(results)]
	changes = current_character.update_with_result(result,None, battle, success)
	outcome_change = Change(type=Change.TYPE_OUTCOME)
	if success:
		outcome_change.name = "Victory!"
	else:
		outcome_change.name = "Defeat!"
	changes.insert(0,Change(type=Change.TYPE_WEAPON,name=weapon))
	changes.insert(0,Change(type=Change.TYPE_ENEMY,name=battle.title))
	changes.insert(0,outcome_change)
	response = HttpResponseRedirect(reverse('lok.views.battle_result', args=(result.id,)))
	request.session['changes'] = changes
	return response

@login_required
def scenario(request, scenario_id):
	scenario = Scenario.objects.get(pk=scenario_id)
	current_character = Character.objects.get(player=request.user.id)
	try:
		battle = scenario.battle
		result = current_character.odds_against(battle)
		odds = result['odds']
		weapon = result['weapon']
		return render_to_response('lok/battle.html', {'battle': battle, 'choice': Choice.objects.get(scenario=scenario_id), 'odds': int(odds * 100), 'weapon': weapon}, context_instance=RequestContext(request))
	except Exception:
		choices = list(Choice.objects.filter(scenario=scenario_id))
		final_choices = list()
		for choice in choices:
			if choice.valid_for(current_character) or choice.visible:
				if not choice.valid_for(current_character):
					choice.invalid = True
				choice.required_items = ChoiceItemPreReq.objects.filter(choice=choice.pk)
				choice.required_stats = ChoiceStatPreReq.objects.filter(choice=choice.pk,minimum__gt=0)
				if (ChoiceMoneyPreReq.objects.filter(choice=choice.pk)):
					choice.required_money = ChoiceMoneyPreReq.objects.get(choice=choice.pk)
				final_choices.append(choice)
		return render_to_response('lok/scenario.html', {'scenario': scenario, 'choices': final_choices}, context_instance=RequestContext(request))
	

@login_required
def result(request, result_id):
	result = Result.objects.get(pk=result_id)
	# Storing changes in the session so we can report on what happened after we're redirected from the POST. This basically lets us (a) protect against multiple submissions, and (b) give useful feedback even if the page load was interrupted. In a production environment, we'd need to more carefully monitor what data we're keeping in session and clear it out after they move on to another page.
	changes = request.session.get('changes')
	return render_to_response('lok/result.html', {'result': result, 'changes': changes})

@login_required
def battle_result(request, result_id):
	result = Result.objects.get(pk=result_id)
	changes = request.session.get('changes')
	return render_to_response('lok/battle_result.html', {'result': result, 'changes': changes})

@login_required
def equip(request, fieldname, equip_id):
	current_character = Character.objects.get(player=request.user.id)
	if (not CharacterItem.objects.filter(character=current_character,item__id=equip_id)):
		return HttpResponseRedirect('/lok/character/')
	#fieldname = "sword"
	setattr(current_character, fieldname, Equipment.objects.get(id=equip_id))
	#current_character.sword = Equipment.objects.get(id=equip_id)
	current_character.save()
	return HttpResponseRedirect('/lok/character/')

@login_required
def travel_to(request, route_id):
	current_character = Character.objects.get(player=request.user.id)
	route = RouteOption.objects.get(pk=route_id)
	# If this route costs money, take it now.
	try:
		current_character.money -= route.routetoll.amount
	except Exception:
		pass
	try:
		item = route.routeitemcost.item
		charitem = CharacterItem.objects.get(character=current_character, item=item)
		charitem.quantity -= route.routeitemcost.amount
		charitem.save()
	except Exception:
		pass
	# Either they've paid, or it's free. Either way, we're done!
	current_character.location = route.route.destination
	current_character.save()
	return HttpResponseRedirect('/lok/story/')
		
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
	changes = current_character.update_with_result(result,stat_pre_reqs,False,False)
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

# Thanks to http://stackoverflow.com/questions/2140787/select-random-k-elements-from-a-list-whose-elements-have-weights?lq=1 for this code!
class Node:
    # Each node in the heap has a weight, value, and total weight.
    # The total weight, self.tw, is self.w plus the weight of any children.
    __slots__ = ['w', 'v', 'tw']
    def __init__(self, w, v, tw):
        self.w, self.v, self.tw = w, v, tw

def rws_heap(items):
    # h is the heap. It's like a binary tree that lives in an array.
    # It has a Node for each pair in `items`. h[1] is the root. Each
    # other Node h[i] has a parent at h[i>>1]. Each node has up to 2
    # children, h[i<<1] and h[(i<<1)+1].  To get this nice simple
    # arithmetic, we have to leave h[0] vacant.
    h = [None]                          # leave h[0] vacant
    #for w, v in items:
    for item in items:
        h.append(Node(item.weight, item, item.weight))
    for i in range(len(h) - 1, 1, -1):  # total up the tws
        h[i>>1].tw += h[i].tw           # add h[i]'s total to its parent
    return h

def rws_heap_pop(h, random):
    gas = h[1].tw * random.random()     # start with a random amount of gas

    i = 1                     # start driving at the root
    while gas > h[i].w:       # while we have enough gas to get past node i:
        gas -= h[i].w         #   drive past node i
        i <<= 1               #   move to first child
        if gas > h[i].tw:     #   if we have enough gas:
            gas -= h[i].tw    #     drive past first child and descendants
            i += 1            #     move to second child
    w = h[i].w                # out of gas! h[i] is the selected node.
    v = h[i].v

    h[i].w = 0                # make sure this node isn't chosen again
    while i:                  # fix up total weights
        h[i].tw -= w
        i >>= 1
    return v

def random_weighted_sample_no_replacement(items, random, n):
    heap = rws_heap(items)              # just make a heap...
    for i in range(n):
        yield rws_heap_pop(heap, random)        # and pop n items off it.
