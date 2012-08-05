from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('lok.views',
	url(r'^lok/', include('lok.urls')),
	url(r'^admin/', include(admin.site.urls)),
)
