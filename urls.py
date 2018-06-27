#*- coding: utf-8 -*-
# Etienne Glossi - Novembre 2009
# etienne.glossi@gmail.com

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from publish import models, categorie
import settings

admin.autodiscover()

# Regex génériques #
urlbegin_re = '([-\w]+/){0,%d}' % categorie.PROFONDEUR_MAX

# Sitemap #
info_dict = {
    'queryset': models.Article.objects.filter(online=True),
    'date_field': 'date_parution',
}

sitemaps = {
    'blog': GenericSitemap(info_dict, priority=0.6),
}

urlpatterns = patterns('',
    # Index
    url(r'^$', direct_to_template, {'template': 'index.html', 'extra_context': {'edito' : models.Edito.objects.get_latest_publication()}}, name="index"),
    
    # Crawlers
    url(r'^sitemap.xml$',   sitemap, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^robots.txt$',    lambda _: HttpResponse('User-agent: *\nDisallow:\n', mimetype='text/plain')),
    #url(r'^favicon.ico$',   lambda _: HttpResponseRedirect('%scss/images/logo.png' % settings.MEDIA_URL)),
    
    # Admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    
    # Static
    url(r'^contact/$', direct_to_template, {'template': 'static/contact.html'}, name="contact"),
    url(r'^mentions/$', direct_to_template, {'template': 'static/mentions_legales.html'}, name="mention_leg"),
    url(r'^redac/$', direct_to_template, {'template': 'static/redac.html'}, name="redac"),
    
    # Publication
    # Ne fonctionne pas avec resolve()
    # url(r'^((?P<categorie_link>[-\w]+)/){1,3}(?P<publication_label>[-\w]+).html$', \
    #                                                   'publish.views.view_publication', name="publication"),
     url(r'^%(urlbegin_re)s(?P<categorie_link>[-\w]+)/(?P<publication_label>[-\w]+).html$' % locals(), \
                                                        'publish.views.view_publication', name="publication"),
    #url(r'^(?P<categorie_link>[-\w]+)/(?P<publication_label>[-\w]+).html$' % locals(), \
    #                                                    'publish.views.view_publication', name="publication"),
    #url(r'^([-\w]+)/(?P<categorie_link>[-\w]+)/(?P<publication_label>[-\w]+).html$' % locals(), \
    #                                                    'publish.views.view_publication', name="publication"),
    #url(r'^([-\w]+)/([-\w]+)/(?P<categorie_link>[-\w]+)/(?P<publication_label>[-\w]+).html$' % locals(), \
    #                                                    'publish.views.view_publication', name="publication"),
    
    # Categories
    # Ne fonctionne pas avec resolve()
    # url(r'^((?P<categorie_link>[-\w]+)/){1,3}$', 'publish.views.detail_categorie', name="categorie"),
    # url(r'^%(urlbegin_re)s(?P<categorie_link>[-\w]+)/$' % locals(), \
    #                                                    'publish.views.detail_categorie', name="categorie"),
    url(r'^(?P<categorie_link>[-\w]+)/$' % locals(), \
                                                        'publish.views.detail_categorie', name="categorie"),
    url(r'^([-\w]+)/(?P<categorie_link>[-\w]+)/$' % locals(), \
                                                        'publish.views.detail_categorie', name="categorie"),
    url(r'^([-\w]+)/([-\w]+)/(?P<categorie_link>[-\w]+)/$' % locals(), \
                                                        'publish.views.detail_categorie', name="categorie"),  
)

## Media (local)
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            dict(
                document_root = settings.MEDIA_ROOT,
                show_indexes = True
            )
        ),
    )

