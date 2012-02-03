from django.conf import settings
from django.contrib import auth
import facebook
import datetime
import logging
from django.contrib.auth.models import User
from django.contrib.auth import login
logger = logging.getLogger(__name__)

from django_facebook import django_fbapi

class DjangoFacebook(object):
    """ Simple accessor object for the Facebook user."""
    def __init__(self, user):
        self._fb_user = user
        self._access_token = user['access_token']
        self._graph = None
        self._auth_user = None
        #self.graph = facebook.GraphAPI(user['access_token'])
    
    @property
    def user(self):
        return self._fb_user
    
    @property
    def uid(self):
        return self._fb_user['uid']
    
    @property
    def access_token(self):
        return self._access_token
    
    @property
    def graph(self):
        """Property used to access GraphAPI connector in "lazy mode"
        """
        if not self._graph:
            self._graph = facebook.GraphAPI(self.access_token)
        return self._graph
    
    @property
    def auth_user(self):
        """Property to access the standard user associated with
        this Facebook user.
        """
        if not self._auth_user:
            self._auth_user = User.objects.get(username=self.uid)
        return self._auth_user
    
    @property
    def facebook_user(self):
        return self.graph.get_object('me')
    
    def is_canvas(self):
        return self.user.get('method') == 'canvas'


class FacebookDebugCanvasMiddleware(object):
    """
    Emulates signed_request behaviour to test your applications embedding.

    This should be a raw string as is sent from facebook to the server in the
    POST data, obtained by LiveHeaders, Firebug or similar. This should
    initialised before FacebookMiddleware.

    """
    def process_request(self, request):
        cp = request.POST.copy()
        request.POST = cp
        request.POST['signed_request'] = settings.FACEBOOK_DEBUG_SIGNEDREQ
        return None


class FacebookDebugCookieMiddleware(object):
    """
    Sets an imaginary cookie to make it easy to work from a development
    environment.

    This should be a raw string as is sent from a browser to the server,
    obtained by LiveHeaders, Firebug or similar. The middleware takes care of
    naming the cookie correctly. This should initialised before
    FacebookMiddleware.

    """
    def process_request(self, request):
        cookie_name = "fbs_" + settings.FACEBOOK_APP_ID
        request.COOKIES[cookie_name] = settings.FACEBOOK_DEBUG_COOKIE
        return None


class FacebookDebugTokenMiddleware(object):
    """
    Forces a specific access token to be used.

    This should be used instead of FacebookMiddleware. Make sure you have
    FACEBOOK_DEBUG_UID and FACEBOOK_DEBUG_TOKEN set in your configuration.

    """
    def process_request(self, request):
        user = {
            'uid': settings.FACEBOOK_DEBUG_UID,
            'access_token': settings.FACEBOOK_DEBUG_TOKEN,
        }
        request.facebook = DjangoFacebook(user)
        return None

class FacebookCanvasMiddleware(object):
    """Middleware for canvas apps.
    
    To be placed before ``django.middleware.csrf.CsrfViewMiddleware``
    """
    def process_request(self, request):
        if request.POST.get('signed_request'):
            signed_request = request.POST["signed_request"]
            data = facebook.parse_signed_request(signed_request, settings.FACEBOOK_SECRET_KEY)
            if data:
                request.csrf_processing_done = True

class FacebookMiddleware(object):
    """
    Transparently integrate Django accounts with Facebook.

    If the user presents with a valid facebook cookie, then we want them to be
    automatically logged in as that user. We rely on the authentication backend
    to create the user if it does not exist.

    We do not want to persist the facebook login, so we avoid calling
    auth.login() with the rationale that if they log out via fb:login-button
    we want them to be logged out of Django also.

    We also want to allow people to log in with other backends, which means we
    need to be careful before replacing request.user.

    """
    def get_fb_user_cookie(self, request):
        """ Attempt to find a facebook user using a cookie. """
        fb_user = facebook.get_user_from_cookie(request.COOKIES,
            settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
        if fb_user:
            fb_user['method'] = 'cookie'
        return fb_user

    def get_fb_user_canvas(self, request):
        """ Attempt to find a user using a signed_request (canvas). """
        fb_user = None
        if request.POST.get('signed_request'):
            signed_request = request.POST["signed_request"]
            data = facebook.parse_signed_request(signed_request,
                                                 settings.FACEBOOK_SECRET_KEY)
            if data and data.get('user_id'):
                fb_user = data['user']
                fb_user['method'] = 'canvas'
                fb_user['uid'] = data['user_id']
                fb_user['access_token'] = data['oauth_token']
        return fb_user

    def get_fb_user(self, request):
        """
        Return a dict containing the facebook user details, if found.

        The dict must contain the auth method, uid, access_token and any
        other information that was made available by the authentication
        method.

        """
        fb_user = None
        methods = ['get_fb_user_cookie', 'get_fb_user_canvas']
        for method in methods:
            logging.debug("-- Trying to find user with %s" % method)
            fb_user = getattr(self, method)(request)
            if (fb_user):
                break
        logging.debug("-- Found user: %r" % fb_user)
        return fb_user

    def process_request(self, request):
        """
        Add `facebook` into the request context and attempt to authenticate
        the user.

        If no user was found, request.facebook will be None. Otherwise it will
        contain a DjangoFacebook object containing:

        uid: The facebook users UID
        user: Any user information made available as part of the
        authentication process
        graph: A GraphAPI object connected to the current user.

        An attempt to authenticate the user is also made. The fb_uid and
        fb_graphtoken parameters are passed and are available for any
        AuthenticationBackends.

        The user however is not "logged in" via login() as facebook sessions
        are ephemeral and must be revalidated on every request.

        However, by specifying ``FACEBOOK_LOGIN_ON_SIGNED_REQUEST = True``,
        you can force login upon signed request.
        """
        logger.debug("Running FacebookMiddleware.process_request()")
        
        fb_user = self.get_fb_user(request)
        request.facebook = DjangoFacebook(fb_user) if fb_user else None
        
        if fb_user and request.user.is_anonymous():
            
            logger.debug("Logging user in: %r" % fb_user)
            
            user = auth.authenticate(fb_uid=fb_user['uid'],
                                     fb_graphtoken=fb_user['access_token'])
            if user:
                if getattr(settings, 'FACEBOOK_LOGIN_ON_SIGNED_REQUEST', False):
                    login(request, user)
                else:
                    user.last_login = datetime.datetime.now()
                    user.save()
                    request.user = user
        
        logger.debug("Execution done: FacebookMiddleware.process_request()")
        return None
