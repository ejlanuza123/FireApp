from django.contrib import admin
from .models import Incident, Locations, Firefighters, FireStation, FireTruck, WeatherConditions

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('location', 'date_time', 'severity_level', 'description')
    list_filter = ('severity_level',)
    search_fields = ('location__name', 'severity_level', 'description')

@admin.register(Locations)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'address', 'city', 'country')

@admin.register(Firefighters)
class FirefightersAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank', 'experience_level', 'station')
    list_filter = ('experience_level', 'station')
    search_fields = ('name', 'rank')

@admin.register(FireStation)
class FireStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'address', 'city', 'country')

@admin.register(FireTruck)
class FireTruckAdmin(admin.ModelAdmin):
    list_display = ('truck_number', 'model', 'capacity', 'station')
    list_filter = ('station',)
    search_fields = ('truck_number', 'model')

@admin.register(WeatherConditions)
class WeatherConditionsAdmin(admin.ModelAdmin):
    list_display = ('incident', 'temperature', 'humidity', 'wind_speed', 'weather_description')
    list_filter = ('weather_description',)
    search_fields = ('incident__location__name', 'weather_description')