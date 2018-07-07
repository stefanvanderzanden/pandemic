from django.http import JsonResponse
from django.urls import reverse_lazy

from django.views.generic import TemplateView, FormView, ListView
from django.views.generic.base import View
from operator import itemgetter

from infection_tracker.forms import AddNewCityForm
from infection_tracker.models import City, Round, InfectionCard, Game


class Overview(TemplateView):
    template_name = 'infection_tracker/overview.html'

    def get_context_data(self, **kwargs):
        return super(Overview, self).get_context_data(
            games=Game.objects.all().order_by('pk'),
            **kwargs
        )


class GameView(TemplateView):
    template_name = 'infection_tracker/game.html'

    def dispatch(self, request, *args, **kwargs):
        if Round.objects.all().count() == 0:
            Round.objects.create(round_number=1)
        return super(GameView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        total_cards = InfectionCard.objects.filter(active=True).count()
        current_round = Round.objects.all().order_by('-round_number').first()
        rounds = Round.objects.filter(round_number__lt=current_round.round_number)

        # Count the total number of cards drawn, by adding the max drawn cards per city
        total_cards_drawn = 0
        for city in City.objects.all():
            cards_drawn_per_round_per_city = []
            for r in rounds:
                cards_drawn_per_round_per_city.append(r.cards.filter(city=city).count())

            city_max = max(cards_drawn_per_round_per_city)
            total_cards_drawn += city_max

        remaining_total_cards = total_cards_drawn - current_round.cards.all().count()
        data = []

        for city in City.objects.all():
            total_city_cards = InfectionCard.objects.filter(city=city, active=True).count()
            city_data = {'name': city.name, 'rounds': [], 'total': total_city_cards}

            for r in Round.objects.all():
                city_data['rounds'].append(r.cards.filter(city=city).count())

            if current_round.round_number == 1:
                drawn_cards = current_round.cards.filter(city=city).count()
                chance = ((total_city_cards - drawn_cards) / (
                            total_cards - current_round.cards.all().count())) * 100
                city_data['chance'] = chance
            else:
                cards_drawn_per_round_per_city = []
                for r in rounds:
                    # Calculate max over rounds
                    cards_drawn_per_round_per_city.append(r.cards.filter(city=city).count())
                total_cards_drawn_per_city = max(cards_drawn_per_round_per_city)
                # print('DRAWN FOR %s = %s' % (city.name, total_cards_drawn_per_city))

                if current_round.cards.all().count() < total_cards_drawn:
                    # We are in the situation we have turned the disposal cards back on top
                    if total_cards_drawn_per_city > 0:
                        remaining_city_cards = total_cards_drawn_per_city - current_round.cards.filter(
                            city=city).count()
                        print('remaining_city_cards: for %s = %s' % (city.name, remaining_city_cards))
                        print('remaining_total_cards: %s' % remaining_total_cards)
                        chance = (remaining_city_cards / remaining_total_cards) * 100
                        city_data['chance'] = chance
                    else:
                        city_data['chance'] = 0
                else:
                    # All disposal cards are drawn, new cards
                    drawn_cards = current_round.cards.filter(city=city).count()
                    chance = ((InfectionCard.objects.filter(city=city).count() - drawn_cards) / (
                            total_cards - current_round.cards.all().count())) * 100
                    city_data['chance'] = chance

            data.append(city_data)

        sorting_key = 'name'
        if self.request.GET.get('sort'):
            if self.request.GET.get('sort') in data[0].keys():
                sorting_key = self.request.GET.get('sort')

        sorted_data = sorted(data, key=itemgetter(sorting_key), reverse=sorting_key == 'chance')

        return super(GameView, self).get_context_data(
            data=sorted_data,
            rounds=Round.objects.all(),
            **kwargs
        )


class InfectCity(View):

    def post(self, request, *args, **kwargs):
        city_name = request.POST.get('city')
        action = request.POST.get('action')

        current_round = Round.objects.all().order_by('-round_number').first()
        total_amount_for_city = InfectionCard.objects.filter(city__name=city_name).count()
        amount_for_city_in_current_round = current_round.cards.filter(city__name=city_name).count()

        message = 'no valid action'
        if action == 'up':
            if amount_for_city_in_current_round < total_amount_for_city:
                card = InfectionCard.objects.exclude(epidemic_rounds__cards__city__name=city_name,
                                                 epidemic_rounds=current_round).filter(city__name=city_name).first()
                current_round.cards.add(card)
                message = 'success'

        elif action == 'down':
            if amount_for_city_in_current_round >= 1:
                card = InfectionCard.objects.filter(epidemic_rounds__cards__city__name=city_name,
                                              epidemic_rounds=current_round).filter(city__name=city_name).first()
                current_round.cards.remove(card)

        return JsonResponse({'message': message})


class NewRound(View):

    def post(self, request, *args, **kwargs):
        current_round = Round.objects.all().order_by('-round_number').first()
        Round.objects.create(round_number=current_round.round_number+1)
        return JsonResponse({'message': 'success'})


class AddCityView(FormView):
    template_name = 'infection_tracker/add_city.html'
    form_class = AddNewCityForm
    success_url = reverse_lazy('infection_tracker:city_list')

    def form_valid(self, form):
        form.save()
        return super(AddCityView, self).form_valid(form)


class CityListView(ListView):
    template_name = 'infection_tracker/city_list.html'
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
