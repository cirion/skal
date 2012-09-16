from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('lok.views',
	url(r'^story/$', 'story'),
	url(r'^create/$', 'create_character'),
	url(r'^party/$', 'party'),
	url(r'^invite_friend/$', 'invite_friend'),
	url(r'^leave_party/$', 'leave_party'),
	url(r'^dismiss_message/(?P<message_id>\d+)/$', 'dismiss_message'),
	url(r'^accept_friend/(?P<user_id>\d+)/$', 'accept_friend'),
	url(r'^invite_party/(?P<character_id>\d+)/$', 'invite_party'),
	url(r'^accept_party/(?P<invite_id>\d+)/$', 'accept_party'),
	url(r'^cancel_invite_party/(?P<invite_id>\d+)/$', 'cancel_invite_party'),
	url(r'^character/$', 'character'),
	url(r'^dead/$', 'dead'),
	url(r'^rest/$', 'rest'),
	url(r'^travel/$', 'travel'),
	url(r'^market/$', 'market'),
	url(r'^travel/(?P<route_id>\d+)/$', 'travel_to'),
	url(r'^scenario/(?P<scenario_id>\d+)/$', 'scenario'),
	url(r'^choice/(?P<choice_id>\d+)/$', 'choice'),
	url(r'^battle/(?P<battle_id>\d+)/$', 'battle'),
	url(r'^title/(?P<title_id>\d+)/$', 'title'),
	url(r'^equip/(?P<fieldname>\w+)/(?P<equip_id>\d+)/$', 'equip'),
	url(r'^buy/(?P<item_id>\d+)/(?P<quantity>\d+)/$', 'buy'),
	url(r'^sell/(?P<item_id>\d+)/(?P<quantity>\w+)/$', 'sell'),
	url(r'^result/(?P<result_id>\d+)/$', 'result'),
	url(r'^battle_result/(?P<result_id>\d+)/$', 'battle_result'),
	url(r'^contact/$', 'contact'),
	url(r'^logout/$', 'logout_view'),
	url(r'^thanks/$', 'thanks'),
)



