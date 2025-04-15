from typing import Any
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions

fake = Faker('fil-PH')

class Command(BaseCommand):
    help = 'Create dummy data for the application'

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.create_locations(50)
        self.create_incidents(50)
        self.create_fire_stations(50)
        self.create_firefighters(50)
        self.create_fire_trucks(50)
        self.create_weather_conditions(50)

    def create_locations(self, count: int) -> None:
        for _ in range(count):
            Locations.objects.create(
                name=fake.building_name(),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.street_address(),
                city=fake.province_lgu(),
                country=fake.current_country()
            )
        self.stdout.write(self.style.SUCCESS('Locations created successfully.'))

    def create_incidents(self, count: int) -> None:
        severity_choices = ['Minor Fire', 'Moderate Fire', 'Major Fire']
        locations = list(Locations.objects.all())

        for _ in range(count):
            incident = Incident.objects.create(
                location=fake.random_element(locations),
                date_time=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.get_current_timezone()),
                severity_level=fake.random_element(severity_choices),
                description=fake.sentence(nb_words=10)
            )
            incident.save()
        self.stdout.write(self.style.SUCCESS('Incidents created successfully.'))

    def create_fire_stations(self, count: int) -> None:
        for _ in range(count):
            FireStation.objects.create(
                name=fake.company(),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.address(),
                city=fake.city(),
                country=fake.country()
            )
        self.stdout.write(self.style.SUCCESS('Fire stations created successfully.'))

    def create_firefighters(self, count: int) -> None:
        xp_choices = ['Probationary Firefighter', 'Firefighter I', 'Firefighter II', 'Firefighter III', 'Driver', 'Captain', 'Battalion Chief']
        stations = list(FireStation.objects.all())

        for _ in range(count):
            Firefighters.objects.create(
                name=fake.name(),
                rank=fake.random_element(xp_choices),
                experience_level=fake.job(),
                station=fake.random_element(stations)
            )
        self.stdout.write(self.style.SUCCESS('Firefighters created successfully.'))

    def create_fire_trucks(self, count: int) -> None:
        stations = list(FireStation.objects.all())
        vehicle_makes = ['Ford', 'Chevrolet', 'Dodge', 'International', 'Freightliner', 'Spartan', 'Peterbilt']

        for _ in range(count):
            make = fake.random_element(vehicle_makes)
            model = f"{make} {fake.word().capitalize()}{fake.random_int(1000, 9999)}"
            FireTruck.objects.create(
                truck_number=fake.uuid4(),
                model=model,
                capacity=fake.random_int(min=1000, max=5000),
                station=fake.random_element(stations)
            )
        self.stdout.write(self.style.SUCCESS('Fire trucks created successfully.'))

    def create_weather_conditions(self, count: int) -> None:
        incidents = list(Incident.objects.all())

        for _ in range(count):
            WeatherConditions.objects.create(
                incident=fake.random_element(incidents),
                temperature=fake.random_int(min=20, max=40),
                humidity=fake.random_int(min=30, max=90),
                wind_speed=fake.random_int(min=5, max=30),
                weather_description=fake.sentence(nb_words=3)
            )
        self.stdout.write(self.style.SUCCESS('Weather conditions created successfully.'))