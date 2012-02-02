"""This module extends the Python SDK by adding some django-specific
functionality, such as caching support.
"""

from django.core.cache import get_cache, DEFAULT_CACHE_ALIAS
from django.conf import settings
import facebook
import hashlib
import urllib
import logging
logger = logging.getLogger(__name__)

class CachingGraphAPI(facebook.GraphAPI):
    """GraphAPI alternative with support for caching requests.
    
    - We want to cache ONLY "safe" methods: GET|HEAD|OPTIONS
    - The cache key is built on: access_token|path|args
    """
    
    def request(self, path, args=None, post_args=None):
        
        logger.debug("Sending request: %s GET=%r POST=%r" % (path, args, post_args))
        
        _fb_response = None
        
        use_cache = bool(post_args is None and getattr(settings, 'FACEBOOK_REQUESTS_CACHE_ENABLE', False))
        
        if use_cache:
            logger.debug("---> Trying to retrieve from cache")
            cache_name = getattr(settings, 'FACEBOOK_REQUESTS_CACHE_NAME', None)
            if cache_name is None:
                cache_name = DEFAULT_CACHE_ALIAS
            cache = get_cache(cache_name)
            logger.debug("---> Calculating cache key")
            cache_key = "facebook_request_%s" % hashlib.sha1("%s %s %s" % (self.access_token, path, urllib.urlencode(args or {}))).hexdigest()
            logger.debug("---> Cache key is %s" % cache_key)
            _fb_response = cache.get(cache_key)
        
        if _fb_response is None:
            logger.debug("---> Retrieving from Graph API")
            _fb_response = facebook.GraphAPI.request(self, path, args=args, post_args=post_args)
        
        logger.debug("===> Result: %r" % _fb_response)
        
        if use_cache:
            ## Store to cache
            logger.debug("Storing result into cache")
            cache.set(cache_key, _fb_response, 3 * 60)
        
        return _fb_response

#def request(self, path, args=None, post_args=None):
#        """Fetches the given path in the Graph API.
#
#        We translate args to a valid query string. If post_args is given,
#        we send a POST request to the given path with the given arguments.
#        """
#        if not args: args = {}
#        if self.access_token:
#            if post_args is not None:
#                post_args["access_token"] = self.access_token
#            else:
#                args["access_token"] = self.access_token
#        post_data = None if post_args is None else urllib.urlencode(post_args)
#        try:
#            file = urllib2.urlopen("https://graph.facebook.com/" + path + "?" +
#                                  urllib.urlencode(args), post_data)
#        except urllib2.HTTPError, e:
#            response = _parse_json( e.read() )
#            raise GraphAPIError(response["error"]["type"],
#                    response["error"]["message"])
#
#        try:
#            fileInfo = file.info()
#            if fileInfo.maintype == 'text':
#                response = _parse_json(file.read())
#            elif fileInfo.maintype == 'image':
#                mimetype = fileInfo['content-type']
#                response = {
#                    "data": file.read(),
#                    "mime-type": mimetype,
#                    "url": file.url,
#                }
#            else:
#                raise GraphAPIError('Response Error', 'Maintype was not text or image')
#        finally:
#            file.close()
#        if response and isinstance(response, dict) and response.get("error"):
#            raise GraphAPIError(response["error"]["type"],
#                                response["error"]["message"])
#        return response
