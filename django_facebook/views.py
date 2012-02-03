"""Default views for django_facebook"""

from django.http import HttpResponse
import datetime

def fb_js_sdk_channel_html(request):
    """Serves the ``channel.html`` file, needed for the Facebook
    JavaScript SDK.
    
    From the official documentation:
    
        The channel file addresses some issues with cross domain communication
        in certain browsers.
        
        It is important for the channel file to be cached for as long as possible.
        When serving this file, you must send valid Expires headers with a long
        expiration period. This will ensure the channel file is cached by
        the browser which is important for a smooth user experience.
        Without proper caching, cross domain communication will become very
        slow and users will suffer a severely degraded experience.
    
    See also: https://developers.facebook.com/docs/reference/javascript/
    """
    
    print "---------------------------------------------------------------------------- REQUESTED channel.html"
    
    from django.utils.dateformat import format
    response = HttpResponse('<script src="//connect.facebook.net/en_US/all.js"></script>')
    cache_expire = datetime.timedelta(days=365)
    cache_expire_date = datetime.datetime.now() + cache_expire
    response['Pragma'] = 'public'
    response['Cache-Control'] = 'max-age=%d' % cache_expire.days
    response['Expires'] = format(cache_expire_date, 'D, d M Y H:i:s')
    return response
