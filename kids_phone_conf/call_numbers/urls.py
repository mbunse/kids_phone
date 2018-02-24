from django.urls import path

from . import views
app_name = 'call_numbers'
urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
]