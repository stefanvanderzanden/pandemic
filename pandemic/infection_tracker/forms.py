from django import forms

from infection_tracker.models import City, InfectionCard


class AddNewCityForm(forms.Form):
    city_name = forms.CharField()
    number_of_cards = forms.IntegerField()

    def save(self):
        data = self.cleaned_data
        city = City.objects.create(name=data.get('city_name'))
        for x in range(data['number_of_cards']):
            InfectionCard.objects.create(city=city)
