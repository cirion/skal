from django.conf.urls import patterns, include, url

urlpatterns = patterns('lok.views',
	url(r'^story/$', 'story'),
	url(r'^create/$', 'create_character'),
	url(r'^scenario/(?P<scenario_id>\d+)/$', 'scenario'),
	url(r'^choice/(?P<choice_id>\d+)/$', 'choice'),
	url(r'^result/(?P<result_id>\d+)/$', 'result'),
)

