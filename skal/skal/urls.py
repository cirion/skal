from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.views.generic import RedirectView
import django.contrib.auth
import django.contrib.auth.views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#urlpatterns = patterns('lok.views',
urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('registration.backends.default.urls')),
	#url(r'^login/$', 'django.contrib.auth.views.login'),
	url(r'^lok/', include('lok.urls')),
	url(r'^friends/', include('friends.urls')),
	url(r'^$', RedirectView.as_view(url='/lok/story/')),
)
if settings.DEBUG:	
	urlpatterns += patterns('', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),)
	urlpatterns += patterns('', url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,}),)

#urlpatterns += staticfiles_urlpatterns()

