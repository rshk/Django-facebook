## Context Processors
import urlparse

def facebook(request):
    context = {}
    
    protocol_relative_url = request.build_absolute_uri('/')
    
    context['protocol_relative_url'] = "//%s" % urlparse.urlparse(protocol_relative_url).netloc
    context['absolute_root_url'] = protocol_relative_url
    return context
