"""URLs for django_facebook default views"""

from django.conf.urls.defaults import *

urlpatterns = patterns('django_facebook.views',
    url(r'^channel.html/?$', 'fb_js_sdk_channel_html'),
)
