from django.urls import path

from infection_tracker.views import InfectCity, NewRound, AddCityView, CityListView, UpdateCityCards, \
    Overview, GameView

app_name = 'infection_tracker'

urlpatterns = [
    path('', Overview.as_view(), name='overview'),

    path('game/<int:id>', GameView.as_view(), name='game'),

    path('city_list', CityListView.as_view(), name='city_list'),
    path('add_city', AddCityView.as_view(), name='add_city'),
    path('update_city', UpdateCityCards.as_view(), name='update_city'),

    path('infect_city', InfectCity.as_view(), name='infect_city'),
    path('new_round', NewRound.as_view(), name='new_round'),
]