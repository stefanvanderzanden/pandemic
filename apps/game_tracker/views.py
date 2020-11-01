from django.http import JsonResponse
from django.urls import reverse_lazy

from django.views.generic import TemplateView, FormView, ListView
from django.views.generic.base import View, RedirectView
from operator import itemgetter

from apps.game_tracker.forms import AddNewCityForm, NewGameForm, CompleteFormView
from apps.game_tracker.models import City, Round, Card, Game, Agent


class Overview(TemplateView):
    template_name = 'game_tracker/overview.html'

    def get_context_data(self, **kwargs):
        return super(Overview, self).get_context_data(
            games=Game.objects.all().order_by('pk'),
            **kwargs
        )


class GameView(TemplateView):
    template_name = 'game_tracker/game.html'
    game_id = None

    def dispatch(self, request, *args, **kwargs):
        self.game_id = kwargs.get('id')
        if Round.objects.filter(game=self.game_id).count() == 0:
            Round.objects.create(round_number=1, game_id=self.game_id)
        return super(GameView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def _calculate_number_of_cards_from_previous_rounds(previous_rounds, current_round):
        """
        In order to calculate the chance of getting a card we first need to get the total amount of
        previous drawn cards.
        Because we want it to be a percentage of that total, not the complete total.

        So e.g. when we have drawn 18 cards in round 1 and we start a new round, we want to know the chance of
        getting one of the cards we draw in the first round, because that have been put on top
        """

        total_cards_drawn = 0
        remaining_total_cards_from_previous_round = 0
        if previous_rounds:
            for city in City.objects.all():
                cards_drawn_per_round_per_city = []
                for r in previous_rounds:
                    cards_drawn_per_round_per_city.append(r.cards.filter(city=city).count())

                city_max = max(cards_drawn_per_round_per_city)
                total_cards_drawn += city_max

                remaining_total_cards_from_previous_round = total_cards_drawn - current_round.cards.all().count()
        return total_cards_drawn, remaining_total_cards_from_previous_round

    def get_context_data(self, **kwargs):
        total_cards = Card.objects.filter(active=True).count()
        rounds_for_game = Round.objects.filter(game_id=self.game_id)
        current_round = rounds_for_game.order_by('-round_number').first()
        previous_rounds = rounds_for_game.filter(round_number__lt=current_round.round_number)

        total_cards_drawn_previous_rounds, \
        remaining_total_cards_from_previous_round = self._calculate_number_of_cards_from_previous_rounds(
            previous_rounds, current_round
        )

        data = []
        for city in City.objects.all():
            total_city_cards = Card.objects.filter(city=city, active=True).count()
            city_data = {
                # This is to sort on
                'name': city.name,
                'region': city.region.name,
                'agents': city.agents.count(),

                'city': city,
                'rounds': [],  # How often has this city been picked in every round, for displaying in the table
                'total': total_city_cards,
            }

            for r in rounds_for_game:
                city_data['rounds'].append(r.cards.filter(city=city).count())

            if current_round.round_number == 1:
                drawn_cards_for_city = current_round.cards.filter(city=city).count()
                # Chance is number of remaining city card for this city divided by the number of city cards in play
                chance = ((total_city_cards - drawn_cards_for_city) / (
                        total_cards - current_round.cards.all().count())) * 100
                city_data['chance'] = chance
            else:
                cards_drawn_per_round_per_city = []
                for r in previous_rounds:
                    # Calculate max over rounds
                    cards_drawn_per_round_per_city.append(r.cards.filter(city=city).count())
                total_cards_drawn_per_city = max(cards_drawn_per_round_per_city)

                if current_round.cards.all().count() < total_cards_drawn_previous_rounds:
                    # We are in the situation we have turned the disposal cards back on top
                    if total_cards_drawn_per_city > 0:
                        remaining_city_cards = total_cards_drawn_per_city - current_round.cards.filter(
                            city=city).count()
                        chance = (remaining_city_cards / remaining_total_cards_from_previous_round) * 100
                        city_data['chance'] = chance
                    else:
                        city_data['chance'] = 0
                else:
                    # All disposal cards are drawn, new cards
                    drawn_cards = current_round.cards.filter(city=city).count()
                    chance = ((Card.objects.filter(city=city).count() - drawn_cards) / (
                            total_cards - current_round.cards.all().count())) * 100
                    city_data['chance'] = chance

            data.append(city_data)

        sorting_key = 'name'
        if self.request.GET.get('sort'):
            if self.request.GET.get('sort') in data[0].keys():
                sorting_key = self.request.GET.get('sort')
        if sorting_key == 'chance':
            sorted_data = sorted(data, key=itemgetter(sorting_key, 'agents'), reverse=True)
        else:
            sorted_data = sorted(data, key=itemgetter(sorting_key), reverse=False)

        return super(GameView, self).get_context_data(
            data=sorted_data,
            rounds=rounds_for_game,
            unassigned_agents=Agent.objects.filter(city__isnull=True),
            **kwargs
        )


class NewGameView(FormView):
    game = None
    template_name = 'game_tracker/new_game.html'
    form_class = NewGameForm

    def form_valid(self, form):
        if form.is_valid():
            new_game = Game.objects.create(date=form.cleaned_data['date'])
            self.game = new_game
            return super(NewGameView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('game_tracker:game', args=[self.game.pk])


class InfectCity(View):

    def post(self, request, *args, **kwargs):
        city_name = request.POST.get('city')
        action = request.POST.get('action')
        game_id = kwargs.get('id')

        current_round = Round.objects.filter(game_id=game_id).order_by('-round_number').first()
        total_amount_for_city = Card.objects.filter(city__name=city_name).count()
        amount_for_city_in_current_round = current_round.cards.filter(city__name=city_name).count()

        message = 'no valid action'
        if action == 'up':
            if amount_for_city_in_current_round < total_amount_for_city:
                card = Card.objects.exclude(epidemic_rounds__cards__city__name=city_name,
                                            epidemic_rounds=current_round).filter(city__name=city_name).first()
                current_round.cards.add(card)
                message = 'success'

        elif action == 'down':
            if amount_for_city_in_current_round >= 1:
                card = Card.objects.filter(epidemic_rounds__cards__city__name=city_name,
                                           epidemic_rounds=current_round).filter(city__name=city_name).first()
                current_round.cards.remove(card)
                message = 'success'

        return JsonResponse({'message': message})


class AddAgentView(View):
    def post(self, request, *args, **kwargs):
        city_name = request.POST.get('city')
        action = request.POST.get('action')
        game_id = kwargs.get('id')

        city = City.objects.get(name=city_name)

        if action == 'up':
            available_agents = Agent.objects.filter(city__isnull=True)
            if not available_agents:
                return JsonResponse({'message': 'failure'})
            else:
                agent = available_agents.first()
                agent.city = city
                agent.save()

        elif action == 'down':
            if city.agents.all().count() == 0:
                return JsonResponse({'message': 'failure'})
            else:
                first_agent = city.agents.all().first()
                city.agents.remove(first_agent)
                return JsonResponse({'message': 'success'})

        return JsonResponse({'message': 'success'})


class NewRound(View):

    def post(self, request, *args, **kwargs):
        game_id = kwargs.get('id')

        current_round = Round.objects.filter(game_id=game_id).order_by('-round_number').first()
        Round.objects.create(round_number=current_round.round_number + 1, game_id=game_id)
        return JsonResponse({'message': 'success'})


class AddCityView(FormView):
    template_name = 'game_tracker/add_city.html'
    form_class = AddNewCityForm
    success_url = reverse_lazy('game_tracker:city_list')

    def form_valid(self, form):
        form.save()
        return super(AddCityView, self).form_valid(form)


class CityListView(ListView):
    template_name = 'game_tracker/city_list.html'
    model = City


class UpdateCityCards(View):

    def post(self, request, *args, **kwargs):
        city = City.objects.get(name=request.POST.get('city'))
        action = request.POST.get('action')

        if action == 'remove':
            if city.active_cards.count() > 0:
                card = city.active_cards.first()
                card.active = False
                card.save()
                message = 'remove success'
            else:
                message = 'remove failed, no active cards'

        elif action == 'add':
            # This is only for correction
            if city.inactive_cards.count() > 0:
                card = city.inactive_cards.first()
                card.active = True
                card.save()
                message = 'add success'
            else:
                message = 'add failed, no inactive cards left'
        else:
            message = 'wrong action'

        return JsonResponse({'message': message})


class CompleteGameView(FormView):
    form_class = CompleteFormView
    template_name = 'game_tracker/complete_game.html'
    success_url = reverse_lazy('game_tracker:overview')
    game_id = None

    def dispatch(self, request, *args, **kwargs):
        self.game_id = kwargs.get('id')
        return super(CompleteGameView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super(CompleteGameView, self).get_context_data(
            game_id=self.game_id,
            **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            cd = form.cleaned_data
            game = Game.objects.get(pk=self.game_id)
            game.won = cd.get('won', False)
            game.finished = True
            game.number_of_cities = cd.get('number_of_cities')
            game.points = cd.get('points')
            game.save()

            return super(CompleteGameView, self).form_valid(form)
        else:
            return self.form_invalid(form)
