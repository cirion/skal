from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from django.views.generic import RedirectView
import django.contrib.auth
import django.contrib.auth.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#urlpatterns = patterns('lok.views',
urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('registration.backends.default.urls')),
	#url(r'^login/$', 'django.contrib.auth.views.login'),
	url(r'^lok/', include('lok.urls')),
	url(r'^$', RedirectView.as_view(url='/lok/story/')),
)
