from django.core.management.base import BaseCommand
from game_tracker.models import City, Card


class Command(BaseCommand):
    help = 'Create all cards'

    cities = [
        {
            'name': 'New York',
            'number': 3
        },
        {
            'name': 'Washington',
            'number': 3
        },
        {
            'name': 'Sao Paulo',
            'number': 3
        },
        {
            'name': 'Jacksonville',
            'number': 3
        },
        {
            'name': 'Londen',
            'number': 3
        },
        {
            'name': 'Tripoli',
            'number': 3
        },
        {
            'name': 'Cairo',
            'number': 3
        },
        {
            'name': 'Lagos',
            'number': 3
        },
        {
            'name': 'Chicago',
            'number': 2
        },
        {
            'name': 'Parijs',
            'number': 2
        },
        {
            'name': 'Atlanta',
            'number': 1
        },
        {
            'name': 'Lima',
            'number': 1
        },
        {
            'name': 'Bogota',
            'number': 2
        },
        {
            'name': 'Santiago',
            'number': 1
        },
        {
            'name': 'Buenos Aires',
            'number': 2
        }
    ]

    def handle(self, *args, **options):
        for city in self.cities:
            if not City.objects.filter(name=city['name']):
                c = City.objects.create(name=city['name'])
                for x in range(1, city['number']+1):
                    Card.objects.create(city=c)
