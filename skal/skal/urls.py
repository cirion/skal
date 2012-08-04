from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'skal.views.home', name='home'),
    # url(r'^skal/', include('skal.foo.urls')),
	url(r'^lok/story/$', 'lok.views.story'),
	url(r'^lok/scenario/(?P<scenario_id>\d+)/$', 'lok.views.scenario'),
#	url(r'^lok/choice/(?P<choice_id>\d+)/$', 'lok.views.choice'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
