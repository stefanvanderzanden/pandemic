from django.db import models


class CardSpecial(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)


class InfectionCard(models.Model):
    city = models.ForeignKey('City', related_name='infection_cards', on_delete=models.CASCADE)
    special = models.OneToOneField('CardSpecial', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.city


class Round(models.Model):
    round_number = models.IntegerField(default=1)
    cards = models.ManyToManyField('InfectionCard', related_name='epidemic_rounds')
