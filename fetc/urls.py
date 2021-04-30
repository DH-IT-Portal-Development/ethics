"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

handler404 = 'main.error_views.error_404'
handler500 = 'main.error_views.error_500'
handler403 = 'main.error_views.error_403'
handler400 = 'main.error_views.error_400'


urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', include('main.urls')),
    path('proposals/', include('proposals.urls')),
    path('studies/', include('studies.urls')),
    path('tasks/', include('tasks.urls')),
    path('observations/', include('observations.urls')),
    path('interventions/', include('interventions.urls')),
    path('reviews/', include('reviews.urls')),
    path('feedback/', include('feedback.urls')),
    path('faqs/', include('faqs.urls')),

    path('admin/', admin.site.urls),
    path('impersonate/', include('impersonate.urls')),

    path('i18n/', include('django.conf.urls.i18n')),
    path('uilcore/', include('uil.core.urls')),
    path('vue/', include('uil.vue.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)

if 'debug_toolbar' in settings.INSTALLED_APPS and settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(
        path('__debug__/', include(debug_toolbar.urls)),
    )

admin.site.site_header = 'FETC-GW'
admin.site.site_title = 'FETC-GW administratie'
admin.site.index_title = 'FETC-GW administratie'
