from django.urls import path

from .views import InterventionCreate, InterventionUpdate

app_name = 'interventions'

urlpatterns = [
    path('create/<int:pk>/', InterventionCreate.as_view(), name='create'),
    path('update/<int:pk>/', InterventionUpdate.as_view(), name='update'),
]
