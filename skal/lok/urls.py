from django.conf.urls import patterns, include, url

urlpatterns = patterns('lok.views',
	url(r'^story/$', 'story'),
	url(r'^create/$', 'create_character'),
	url(r'^character/$', 'character'),
	url(r'^travel/$', 'travel'),
	url(r'^market/$', 'market'),
	url(r'^travel/(?P<route_id>\d+)/$', 'travel_to'),
	url(r'^scenario/(?P<scenario_id>\d+)/$', 'scenario'),
	url(r'^choice/(?P<choice_id>\d+)/$', 'choice'),
	url(r'^battle/(?P<battle_id>\d+)/$', 'battle'),
	url(r'^equip/(?P<fieldname>\w+)/(?P<equip_id>\d+)/$', 'equip'),
	url(r'^buy/(?P<item_id>\d+)/(?P<quantity>\d+)/$', 'buy'),
	url(r'^sell/(?P<item_id>\d+)/(?P<quantity>\w+)/$', 'sell'),
	url(r'^result/(?P<result_id>\d+)/$', 'result'),
	url(r'^battle_result/(?P<result_id>\d+)/$', 'battle_result'),
)

