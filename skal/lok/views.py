from datetime import datetime, timedelta
from string import capwords
import friends
from friends.models import FriendshipRequest, Friendship
import re
import bisect
from django.utils.timezone import utc
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.core.mail import send_mail, EmailMessage
from lok.models import Scenario, Choice, Character, MoneyOutcome, StatOutcome, ScenarioStatPreReq, ChoiceStatPreReq, Result, CharacterStat, CharacterItem, Stat, ChoiceItemPreReq, ChoiceMoneyPreReq, ChoicePlotPreReq, CharacterPlot, Plot, Equipment, EquipmentStat, Battle, Change, RouteFree, RouteToll, RouteItemCost, RouteItemFree, LocationRoute, CharacterLocationAvailable, RouteOption, ItemLocation, Item, Location, PlotDescription, Title, CharacterTitle, Party, PartyInvite, SocialMessage
import random
from random import Random
from lok.utils import level_from_value as level_from_value
from lok.forms import ContactForm
from django.contrib.auth import logout
from django.contrib.auth.models import User

@login_required
def create_character(request):
	if (request.POST):
		name = request.POST['name']
		name = name.capitalize()
		if Character.objects.filter(name = name):
			return render_to_response('lok/create_character.html', {'error': "Sorry, that name is already taken."}, context_instance=RequestContext(request))
		if not re.match("[a-zA-Z]+$", name):
			return render_to_response('lok/create_character.html', {'error': "Please choose a name without any spaces, numbers, or special characters."}, context_instance=RequestContext(request))
		party = Party()
		party.save()
		character = Character()
		character.party = party
		character.name = name
		character.player = request.user
		character.money = 0
		character.gender = request.POST['gender']
		character.contact = request.POST['contact']
		character.location = Location.objects.get(name="your childhood home")
		character.refill_time = datetime.utcnow().replace(tzinfo=utc)
		character.current_health = character.max_health()
		character.save()
		return HttpResponseRedirect('/lok/story/')
	return render_to_response('lok/create_character.html', {}, context_instance=RequestContext(request))

@login_required
def dead(request):
	return render_to_response('lok/dead.html', {}, context_instance=RequestContext(request))

@login_required
def character(request):
	current_character = Character.objects.get(player=request.user.id)
	titles = CharacterTitle.objects.filter(character = current_character)
	skills = CharacterStat.objects.filter(character = current_character, stat__type= Stat.TYPE_SKILL, value__gte = 10)
	for skill in skills:
		skill.value = level_from_value(skill.value) + current_character.stat_bonus(skill.stat)
	plots = CharacterPlot.objects.filter(character = current_character, plot__visible = True, plot__achievement = False )
	plot_descriptions = list()
	for plot in plots:
		#print "Looking at " + plot.__unicode__() + "  " + str(plot.pk) + " value = " + str(plot.value)
		#for arg in PlotDescription.objects.filter(plot = plot.plot.pk):
		#	print "Candidate " + " " + str(arg.pk) + ":" + arg.__unicode__() + ": " + str(arg.value)
		if PlotDescription.objects.filter(plot = plot.plot.pk, value = plot.value):
			#print "Got a match."
			plot_descriptions.append(PlotDescription.objects.get(plot=plot.plot, value=plot.value))
	achievements = list(CharacterPlot.objects.filter(character = current_character, plot__achievement = True))
	achievements.reverse()
	items = CharacterItem.objects.filter(character = current_character, quantity__gt = 0)
	fame = 0
	if CharacterStat.objects.filter(character = current_character, stat__type= Stat.TYPE_FAME):
		fame = level_from_value(CharacterStat.objects.filter(character = current_character, stat__type= Stat.TYPE_FAME)[0].value)
	esteems = CharacterStat.objects.filter(character = current_character, stat__type = Stat.TYPE_ESTEEM)
	for esteem in esteems:
		esteem.value = level_from_value(esteem.value)
	if current_character.gender == Character.GENDER_MALE:
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
	return render_to_response('lok/character.html', {'character': current_character, 'skills': skills, 'fame': fame, 'items': items, 'plots': plot_descriptions, 'achievements': achievements, 'title': title, 'swords': swords, 'bashing': bashing, 'bows': bows, 'feet': feet, 'cloaks': cloaks, 'clothes': clothes, 'gloves': gloves, 'rings': rings, 'neck': neck, 'armors': armors, 'esteems': esteems, 'titles': titles})

@login_required
def story(request):
	if not Character.objects.filter(player=request.user.id):
		return HttpResponseRedirect('/lok/create/')
	current_character = Character.objects.get(player=request.user.id)
	if current_character.current_health < 1 and not current_character.location.name == "Mercy Home":
		current_character.location = Location.objects.get(name="Mercy Home")
		current_character.save()
		return HttpResponseRedirect('/lok/dead/')
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

	routes = get_routes(current_character)
	next_page_time_string = ""
	if current_character.actions < 20:
		next_page_time = current_character.refill_time - datetime.utcnow().replace(tzinfo=utc)
		minutes, seconds = divmod(next_page_time.seconds, 60)
		if minutes == 1:
			next_page_time_string = "1 minute " 
		elif minutes > 1:
			next_page_time_string = "%s minutes " % (minutes)
		if seconds == 1:
			next_page_time_string = next_page_time_string +  "1 second"
		elif seconds > 1:
			next_page_time_string = next_page_time_string +  "%s seconds" % (seconds)
	party_notifications = SocialMessage.objects.filter(to_character=current_character).exists()
	print "Party notifications: " + str(party_notifications)
	return render_to_response('lok/story.html', {'routes': routes, 'next_page_time': next_page_time_string, 'scenarios': out_scenarios, 'actions': current_character.actions, 'character': current_character, "party_notification": party_notifications})

@login_required
def party(request):
	current_character = Character.objects.get(player=request.user.id)
	friend_users = Friendship.objects.friends_of(request.user)
	msg = message = None
	if request.GET:
		msg = request.GET['msg']
	friends = list()
	for friend in friend_users:
		if friend != request.user:
			friends.append(Character.objects.get(player=friend))
	sent_invites_users = FriendshipRequest.objects.filter(from_user=current_character.player)
	sent_invites = list()
	for sent_invite in sent_invites_users:
		sent_invites.append(Character.objects.get(player = sent_invite.to_user))
	received_invites_users = FriendshipRequest.objects.filter(to_user=current_character.player)
	received_invites = list()
	for received_invite in received_invites_users:
		received_invites.append(Character.objects.get(player=received_invite.from_user))
	if msg == 'notfound':
		message = "Sorry, we couldn't find anyone by that name. Please try again with their character's name, username, or an email address."
	elif msg == 'pending':
		message = "You have already sent them an invitation. Let's hope they accept soon!"
	elif msg == 'sent':
		message = "Your invitation has been sent. Please await a reply."
	if current_character.party and current_character.party.size() < current_character.party.max_size():
		party_room = current_character.party.max_size() - current_character.party.size()
	elif not current_character.party:
		party_room = current_character.max_party_size()
	else:
		party_room = 0
	party_invites = PartyInvite.objects.filter(to_character=current_character)
	party_invites_sent = PartyInvite.objects.filter(from_character=current_character)
	party_room -= party_invites_sent.count()
	if party_room < 0:
		party_room = 0
	notifications = SocialMessage.objects.filter(to_character=current_character)
	return render_to_response('lok/party.html', {'party_room': party_room, 'message': message, 'character': current_character, 'party_invites': party_invites, 'party_invites_sent': party_invites_sent, 'friends': friends, 'sent_invites': sent_invites, 'received_invites': received_invites, 'notifications': notifications}, context_instance=RequestContext(request))

@login_required
def dismiss_message(request, message_id):
	message = SocialMessage.objects.get(pk=message_id)
	message.delete()
	return HttpResponseRedirect('/lok/party/')

@login_required
def dismiss_all_messages(request):
	current_character = Character.objects.get(player=request.user.id)
	SocialMessage.objects.filter(to_character=current_character).delete()
	return HttpResponseRedirect('/lok/party/')

@login_required
def invite_party(request, character_id):
	current_character = Character.objects.get(player=request.user.id)
	invited = Character.objects.get(pk=character_id)
	if not PartyInvite.objects.filter(from_character=current_character, to_character=invited):
		invite = PartyInvite(from_character=current_character, to_character=invited,party=current_character.party)
		invite.save()
	return HttpResponseRedirect('/lok/party/')

@login_required
def leave_party(request):
	current_character = Character.objects.get(player=request.user.id)
	party = Party()
	party.save()
	current_character.party = party
	current_character.save()
	return HttpResponseRedirect('/lok/party/')

@login_required
def cancel_invite_party(request, invite_id):
	PartyInvite.objects.get(pk=invite_id).delete()
	return HttpResponseRedirect('/lok/party/')
	
@login_required
def accept_party(request, invite_id):
	current_character = Character.objects.get(player=request.user.id)
	party = PartyInvite.objects.get(pk=invite_id).party
	accept = request.GET['accept']
	if accept == "true" and party.size() < party.max_size():
		old_party = current_character.party
		current_character.party = party
		current_character.save()
		if old_party.size() == 0:
			old_party.delete()
		# Erase any competing invitations received.
		invites = PartyInvite.objects.filter(to_character=current_character).exclude(id=invite_id)
		for invite in invites:
			invite.delete()
	PartyInvite.objects.get(pk=invite_id).delete()
	return HttpResponseRedirect('/lok/party/')

@login_required
def invite_friend(request):
	name = request.POST['name']
	current_character = Character.objects.get(player=request.user.id)
	match = Character.objects.filter(name__iexact=name)
	if match:
		match = match[0].player
	if not match:
		match = User.objects.filter(username__iexact=name)
	if not match:
		match = User.objects.filter(email__iexact=name)
	if not match:
		return HttpResponseRedirect('/lok/party?msg=notfound')
	if FriendshipRequest.objects.filter(from_user=request.user, to_user=match):
		return HttpResponseRedirect('/lok/party?msg=pending')
	FriendshipRequest.objects.create(from_user=request.user, to_user=match, message='Care to join?')
	return HttpResponseRedirect('/lok/party?msg=sent')

@login_required
def accept_friend(request, user_id):
	current_character = Character.objects.get(player=request.user.id)
	accept = request.GET['accept']
	ask = FriendshipRequest.objects.get(to_user=request.user.id, from_user__pk=user_id)
	if (accept == "true"):
		ask.accept()
	else:
		ask.decline()
	ask.delete()
	return HttpResponseRedirect('/lok/party')

@login_required
def market(request):
	current_character = Character.objects.get(player=request.user.id)
	sellable_items = CharacterItem.objects.filter(character=current_character, item__sellable=True, quantity__gt = 0)
	sale_items = list()
	for item in sellable_items:
		sale_items.append({'id': item.item.id, 'name': item.item.name, 'price': item.item.value / 2, 'quantity': item.quantity, 'stats': EquipmentStat.objects.filter(equipment=item.item)})
	items_check = ItemLocation.objects.filter(location=current_character.location)
	buyable_items = list()
	for item in items_check:
		if item.item.multiple or (not CharacterItem.objects.filter(character=current_character, item = item.item)) or (CharacterItem.objects.get(character=current_character, item = item.item).quantity == 0):
		#if not CharacterItem.objects.filter(character=current_character, item = item.item) or CharacterItem.objects.get(character=current_character
#			buyable_items.append(item)
			details = ({'name': item.item.name, 'id': item.item.pk, 'price': item.item.value, 'stats': EquipmentStat.objects.filter(equipment=item.item)})
			if (CharacterItem.objects.filter(character=current_character, item=item.item)):
				details['quantity'] = CharacterItem.objects.get(character=current_character, item=item.item).quantity
			buyable_items.append(details)
	return render_to_response('lok/market.html', {'character': current_character, 'royals': current_character.money, 'sellable_items': sale_items, 'buyable_items': buyable_items }, context_instance=RequestContext(request))

def get_routes(current_character):
	routes = list(LocationRoute.objects.filter(origin = current_character.location))
	approved_routes = list()
	for route in routes:
		route_found = False
		if CharacterLocationAvailable.objects.filter(character=current_character,location=route.destination):
				if RouteFree.objects.filter(route=route):
					approved_routes.append(RouteFree.objects.get(route=route))
					route_found = True
				else:
					if (RouteItemFree.objects.filter(route=route)):
						item = RouteItemFree.objects.get(route=route)
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
	if current_character.actions < 1:
		return render_to_response('lok/wait.html', {'time': (current_character.refill_time - datetime.utcnow().replace(tzinfo=utc)).seconds})
	odds_result = current_character.party.odds_against(battle)
	odds = odds_result['odds']
	weapon = odds_result['weapon']
	fighter = odds_result['character']
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
	changes.insert(0,Change(type=Change.TYPE_ALLY,name=fighter))
	changes.insert(0,Change(type=Change.TYPE_WEAPON,name=weapon))
	changes.insert(0,Change(type=Change.TYPE_ENEMY,name=battle.name))
	changes.insert(0,outcome_change)
	response = HttpResponseRedirect(reverse('lok.views.battle_result', args=(result.id,)))
	request.session['changes'] = changes
	return response

@login_required
def scenario(request, scenario_id):
	scenario = Scenario.objects.get(pk=scenario_id)
	current_character = Character.objects.get(player=request.user.id)
	if not scenario.valid_for(current_character):
		return HttpResponseRedirect('/lok/story/')
	try:
		battle = scenario.battle
		result = current_character.party.odds_against(battle)
		odds = result['odds']
		weapon = result['weapon']
		ally = result['character']
		return render_to_response('lok/battle.html', {'battle': battle, 'choice': Choice.objects.get(scenario=scenario_id), 'odds': int(odds * 100), 'ally': ally, 'weapon': weapon, 'character': current_character}, context_instance=RequestContext(request))
	except Exception:
		choices = list(Choice.objects.filter(scenario=scenario_id))
		final_choices = list()
		for choice in choices:
			if choice.valid_for(current_character) or choice.visible:
				if not choice.valid_for(current_character):
					choice.invalid = True
				choice.required_items = ChoiceItemPreReq.objects.filter(choice=choice.pk)
				choice.required_stats = ChoiceStatPreReq.objects.filter(choice=choice.pk,minimum__gt=0)
				challenges = ChoiceStatPreReq.objects.filter(choice=choice.pk)
				if Result.objects.filter(type=Result.FAILURE, choice=choice):
					for stat in challenges:
						odds = int(stat.odds(current_character) * 100)
						if odds < 100:
							if not hasattr(choice, 'odds_pct') or odds < choice.odds_pct:
								choice.odds_pct = odds
				if (ChoiceMoneyPreReq.objects.filter(choice=choice.pk)):
					choice.required_money = ChoiceMoneyPreReq.objects.get(choice=choice.pk)
				final_choices.append(choice)
		return render_to_response('lok/scenario.html', {'scenario': scenario, 'choices': final_choices, 'character': current_character}, context_instance=RequestContext(request))
	

@login_required
def result(request, result_id):
	result = Result.objects.get(pk=result_id)
	current_character = Character.objects.get(player=request.user.id)
	# Storing changes in the session so we can report on what happened after we're redirected from the POST. This basically lets us (a) protect against multiple submissions, and (b) give useful feedback even if the page load was interrupted. In a production environment, we'd need to more carefully monitor what data we're keeping in session and clear it out after they move on to another page.
	changes = request.session.get('changes')
	return render_to_response('lok/result.html', {'result': result, 'character': current_character, 'changes': changes})

@login_required
def battle_result(request, result_id):
	result = Result.objects.get(pk=result_id)
	changes = request.session.get('changes')
	current_character = Character.objects.get(player=request.user.id)
	return render_to_response('lok/battle_result.html', {'result': result, 'character': current_character, 'changes': changes})

@login_required
def buy(request, item_id, quantity):
	current_character = Character.objects.get(player=request.user.id)
	item = Item.objects.get(pk=item_id)
	cost = item.value * int(quantity)
	if (cost > current_character.money):
		return HttpResponseRedirect('/lok/market/')
	item, created = CharacterItem.objects.get_or_create(character=current_character, item=item)
	item.quantity = item.quantity + int(quantity)
	item.save()
	current_character.money -= cost
	current_character.save()
	return HttpResponseRedirect('/lok/market/')

@login_required
def sell(request, item_id, quantity):
	current_character = Character.objects.get(player=request.user.id)
	item = CharacterItem.objects.get(item__pk=item_id, character=current_character)
	amount = 0
	if (quantity == 'all'):
		amount = item.quantity
	else:
		amount = int(quantity)
	if amount > item.quantity:
		return HttpResponseRedirect('/lok/market/')
	earnings = (item.item.value / 2) * amount
	current_character.money += earnings
	item.quantity -= amount
	current_character.save()
	item.save()
	return HttpResponseRedirect('/lok/market/')

@login_required
def title(request, title_id):
	#print "Using ID " + str(title_id)
	current_character = Character.objects.get(player=request.user.id)
	if not CharacterTitle.objects.filter(character=current_character,title__id=title_id):
		current_character.active_title=None
	else:
		current_character.active_title = Title.objects.get(id=CharacterTitle.objects.get(title__id=title_id).title.id)
	current_character.save()
	return HttpResponseRedirect('/lok/character/')

@login_required
def equip(request, fieldname, equip_id):
	current_character = Character.objects.get(player=request.user.id)
	if (not CharacterItem.objects.filter(character=current_character,item__id=equip_id)):
		setattr(current_character, fieldname, None)
	else:
		setattr(current_character, fieldname, Equipment.objects.get(id=equip_id))
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

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST, request.FILES)
		if form.is_valid():
				cd = form.cleaned_data
				mail = EmailMessage("SKAL: " + cd['type'],
                                	cd['email'] + ":" + cd['message'],
                                	cd.get('email', 'noreply@example.com'),
                                	['cirion@gmail.com'])
				attachment = request.FILES['attachment']
				mail.attach(attachment.name, attachment.read(), attachment.content_type)
				mail.send()
				return HttpResponseRedirect('/lok/thanks/')
	else:
		form = ContactForm()
	return render_to_response('lok/contact_form.html', {'form': form}, context_instance=RequestContext(request))

def thanks(request):
	return render_to_response('lok/thanks.html', {})

def rest(request):
	current_character = Character.objects.get(player=request.user.id)
	current_character.rest()
	return render_to_response('lok/rest.html', {})
	
def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/lok/story/')
