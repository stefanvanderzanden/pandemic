from django.urls import path

from infection_tracker import views

app_name = 'infection_tracker'

urlpatterns = [
    path('', views.Overview.as_view(), name='overview'),

    path('city_list', views.CityListView.as_view(), name='city_list'),
    path('add_city', views.AddCityView.as_view(), name='add_city'),
    path('update_city', views.UpdateCityCards.as_view(), name='update_city'),

    path('game/new', views.NewGameView.as_view(), name='new_game'),
    path('game/<int:id>', views.GameView.as_view(), name='game'),

    path('game/<int:id>/infect_city', views.InfectCity.as_view(), name='infect_city'),
    path('game/<int:id>/new_round', views.NewRound.as_view(), name='new_round'),
    path('game/<int:id>/complete', views.CompleteGameView.as_view(), name='complete_game'),
]