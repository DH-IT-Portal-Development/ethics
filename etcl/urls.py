"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),

    url(r'^', include('core.urls', namespace='core')),
    url(r'^proposals/', include('proposals.urls', namespace='proposals')),
    url(r'^studies/', include('studies.urls', namespace='studies')),
    url(r'^tasks/', include('tasks.urls', namespace='tasks')),
    url(r'^observations/', include('observations.urls', namespace='observations')),
    url(r'^interventions/', include('interventions.urls', namespace='interventions')),
    url(r'^reviews/', include('reviews.urls', namespace='reviews')),
    url(r'^feedback/', include('feedback.urls', namespace='feedback')),
    url(r'^faqs/', include('faqs.urls', namespace='faqs')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^i18n/', include('django.conf.urls.i18n')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'ETCL'
admin.site.site_title = 'ETCL administratie'
admin.site.index_title = 'ETCL administratie'
