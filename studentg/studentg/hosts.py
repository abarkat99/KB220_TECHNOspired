from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
                         host(r'admin', 'redressal.admin_urls', name='admin'),
                         host(r'www', settings.ROOT_URLCONF, name='www'),
                         host(r'redressal', 'redressal.committee_urls', name='redressal'),
                         # host(r'(\w+)', settings.ROOT_URLCONF, name='wildcard'),
                         )
