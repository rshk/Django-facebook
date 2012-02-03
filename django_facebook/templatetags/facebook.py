from django import template
from django.conf import settings
register = template.Library()


@register.inclusion_tag('tags/facebook_load.html')
def facebook_load():
    pass


@register.tag
def facebook_init(parser, token):
    nodelist = parser.parse(('endfacebook',))
    parser.delete_first_token()
    return FacebookNode(nodelist)


class FacebookNode(template.Node):
    """ Allow code to be added inside the facebook asynchronous closure. """
    def __init__(self, nodelist):
        try:
            app_id = settings.FACEBOOK_APP_ID
        except AttributeError:
            raise template.TemplateSyntaxError, "facebook_init tag requires " \
                "FACEBOOK_APP_ID to be configured."
        self.app_id = app_id
        self.nodelist = nodelist

    def render(self, context):
        t = template.loader.get_template('tags/facebook_init.html')
        code = self.nodelist.render(context)
        custom_context = context
        custom_context['code'] = code
        custom_context['app_id'] = self.app_id
        #custom_context['channel_url'] = request.build_absolute_uri(reversed('django_facebook.views.fb_js_sdk_channel_html'))
        return t.render(context)


@register.simple_tag
def facebook_perms():
    return ",".join(getattr(settings, 'FACEBOOK_PERMS', []))
