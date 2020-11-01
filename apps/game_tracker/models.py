from django.db import models
from django.utils.translation import gettext_lazy as _


class Game(models.Model):
    date = models.DateField()
    finished = models.BooleanField(default=False)
    won = models.BooleanField(null=True)
    number_of_cities = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)


class Region(models.Model):
    code = models.CharField(max_length=10, primary_key=True, unique=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class City(models.Model):
    REGION_CHOICES = (
        ('na', _('North America')),
        ('sa', _('South America')),
        ('eu', _('Europe')),
        ('af', _('Africa')),
        ('as', _('Asia')),
        ('pr', _('Pacific Rim')),
    )
    name = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey('game_tracker.Region', related_name='cities', on_delete=models.CASCADE)
    affiliation = models.ForeignKey('game_tracker.Affiliation', on_delete=models.SET_NULL, null=True, blank=True)
    has_safe_house = models.BooleanField(default=False)
    surveillance_level = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return self.name

    @property
    def active_cards(self):
        return self.infection_cards.filter(active=True)

    @property
    def inactive_cards(self):
        return self.infection_cards.filter(active=False)

    @property
    def number_of_agents(self):
        return self.agents.count()


class Card(models.Model):
    CARD_TYPE_CHOICES = (
        ('threat', _('Threat')),
        ('player', _('Player'))
    )

    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    city = models.ForeignKey('City', related_name='infection_cards', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.card_type}: {self.city.name}'


class Round(models.Model):
    round_number = models.IntegerField(default=1)
    cards = models.ManyToManyField('game_tracker.Card', related_name='epidemic_rounds')
    game = models.ForeignKey('game_tracker.Game', related_name='rounds', on_delete=models.CASCADE, null=True)


class Affiliation(models.Model):
    name = models.CharField(max_length=25, verbose_name=_('Affiliation'))
    logo = models.ImageField(verbose_name=_('Logo for afffiliation'), null=True, blank=True)

    def __str__(self):
        return self.name


class Agent(models.Model):
    city = models.ForeignKey('game_tracker.City', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='agents')
