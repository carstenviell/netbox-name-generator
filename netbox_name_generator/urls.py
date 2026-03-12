from django.urls import path

from .views import NameGeneratorView

app_name = 'netbox_name_generator'

urlpatterns = [
    path('', NameGeneratorView.as_view(), name='index'),
]
