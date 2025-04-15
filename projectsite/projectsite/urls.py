from django.contrib import admin
from django.urls import path
from fire.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('stations', map_station, name='map-station'),
    path('incidents', map_incidents, name='map-incidents'),

    path('weather_list', WeatherConditionsList.as_view(), name='weather-list'),
    path('weather_list/add', WeatherConditionsAdd.as_view(), name='weather-add'),
    path('weather_list/edit/<int:pk>', WeatherConditionsUpdate.as_view(), name='weather-update'),
    path('weather_list/delete/<int:pk>', WeatherConditionsDelete.as_view(), name='weather-delete'),

    path('firetruck_list', FireTruckList.as_view(), name='firetruck-list'),
    path('firetruck_list/add', FireTruckAdd.as_view(), name='firetruck-add'),
    path('firetruck_list/edit/<int:pk>', FireTruckUpdate.as_view(), name='firetruck-update'),
    path('firetruck_list/delete/<int:pk>', FireTruckDelete.as_view(), name='firetruck-delete'),

    path('incident_list', IncidentList.as_view(), name='incident-list'),
    path('incident_list/add', IncidentAdd.as_view(), name='incident-add'),
    path('incident_list/edit/<int:pk>', IncidentUpdate.as_view(), name='incident-update'),
    path('incident_list/delete/<int:pk>', IncidentDelete.as_view(), name='incident-delete'),

    path('firestation_list', FireStationList.as_view(), name='firestation-list'),
    path('firestation_list/add', FireStationAdd.as_view(), name='firestation-add'),
    path('firestation_list/edit/<int:pk>', FireStationUpdate.as_view(), name='firestation-update'),
    path('firestation_list/delete/<int:pk>', FireStationDelete.as_view(), name='firestation-delete'),

    path('locations_list', LocationsList.as_view(), name='locations-list'),
    path('locations_list/add', LocationsAdd.as_view(), name='locations-add'),
    path('locations_list/edit/<int:pk>', LocationsUpdate.as_view(), name='locations-update'),
    path('locations_list/delete/<int:pk>', LocationsDelete.as_view(), name='locations-delete'),

    path('firefighters_list', FirefightersList.as_view(), name='firefighters-list'),
    path('firefighters_list/add', FirefightersAdd.as_view(), name='firefighters-add'),
    path('firefighters_list/edit/<int:pk>', FirefightersUpdate.as_view(), name='firefighters-update'),
    path('firefighters_list/delete/<int:pk>', FirefightersDelete.as_view(), name='firefighters-delete'),
]
