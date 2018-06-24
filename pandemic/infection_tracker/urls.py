from django.urls import path

from infection_tracker.views import TableView, InfectCity, NewRound, AddCityView

app_name = 'infection_tracker'

urlpatterns = [
    path('', TableView.as_view(), name='list'),
    path('infect_city', InfectCity.as_view(), name='infect_city'),
    path('new_round', NewRound.as_view(), name='new_round'),
    path('add_city', AddCityView.as_view(), name='add_city'),
]