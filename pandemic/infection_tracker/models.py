from django.db import models


class Game(models.Model):
    date = models.DateField()
    finished = models.BooleanField(default=False)
    won = models.NullBooleanField()
    number_of_cities = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)

    @property
    def active_cards(self):
        return self.infection_cards.filter(active=True)

    @property
    def inactive_cards(self):
        return self.infection_cards.filter(active=False)


class InfectionCard(models.Model):
    city = models.ForeignKey('City', related_name='infection_cards', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.city


class Round(models.Model):
    round_number = models.IntegerField(default=1)
    cards = models.ManyToManyField('InfectionCard', related_name='epidemic_rounds')
    game = models.ForeignKey('Game', related_name='rounds', on_delete=models.CASCADE, null=True)
