from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from fire.models import Locations, Incident, FireStation, WeatherConditions, FireTruck
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime
from collections import defaultdict
from django.urls import reverse_lazy
from fire.forms import *
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q


class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass


def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)


def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}

    return JsonResponse(result_with_month_names)


def MultilineIncidentTop3Country(request):

    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

def map_station(request):
     fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

     for fs in fireStations:
         fs['latitude'] = float(fs['latitude'])
         fs['longitude'] = float(fs['longitude'])

     fireStations_list = list(fireStations)

     context = {
         'fireStations': fireStations_list,
     }

     return render(request, 'map_station.html', context)
 

def map_incidents(request):
    incidents = Incident.objects.select_related('location').values(
        'location__name', 'location__city', 'location__latitude', 'location__longitude', 'description', 'date_time', 'severity_level'
    )

    locations = defaultdict(lambda: {'incidents': []})
    for incident in incidents:
        location_name = incident['location__name']
        location_data = {
            'name': location_name,
            'city': incident['location__city'],
            'latitude': float(incident['location__latitude']),
            'longitude': float(incident['location__longitude']),
            'incidents': locations[location_name]['incidents']
        }
        location_data['incidents'].append({
            'description': incident['description'],
            'date_time': incident['date_time'].strftime('%Y-%m-%d %H:%M:%S'),
            'severity_level': incident['severity_level']
        })
        locations[location_name] = location_data

    locations_list = list(locations.values())
    distinct_cities = Locations.objects.values_list('city', flat=True).distinct()

    context = {
        'locations': locations_list,
        'distinct_cities': distinct_cities,
    }

    return render(request, 'map_incidents.html', context)


# Weather Conditions Views
class WeatherConditionsList(ListView):
    model = WeatherConditions
    context_object_name = 'weather'
    template_name = "weatherconditions_list.html"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(WeatherConditionsList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
             query = self.request.GET.get('q')
             qs = qs.filter(Q(incident__location__name__icontains=query) |
                            # Q(temperature__icontains=query) |
                            # Q(humidity__icontains=query) |
                            # Q(wind_speed__icontains=query) |
                            Q(weather_description__icontains=query))
        return qs
    

class WeatherConditionsAdd(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = "weatherconditions_add.html"
    success_url = reverse_lazy('weather-list')
    

class WeatherConditionsUpdate(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = "weatherconditions_edit.html"
    success_url = reverse_lazy('weather-list')
    
    
class WeatherConditionsDelete(DeleteView):
    model = WeatherConditions
    template_name = "weatherconditions_delete.html"
    success_url = reverse_lazy('weather-list')


# Fire Truck Views
class FireTruckList(ListView):
    model = FireTruck
    context_object_name = 'firetruck'
    template_name = "firetruck_list.html"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
         qs = super(FireTruckList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None:
             query = self.request.GET.get('q')
             qs = qs.filter(Q(truck_number__icontains=query) |
                            Q(model__icontains=query) |
                            Q(capacity__icontains=query) )
                            # Q(firestation__name__icontains=query))
         return qs

class FireTruckAdd(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = "firetruck_add.html"
    success_url = reverse_lazy('firetruck-list')

class FireTruckUpdate(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = "firetruck_edit.html"
    success_url = reverse_lazy('firetruck-list')
    
class FireTruckDelete(DeleteView):
    model = FireTruck
    template_name = "firetruck_delete.html"
    success_url = reverse_lazy('firetruck-list')


# Incident Views
class IncidentList(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = "incident_list.html"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
         qs = super(IncidentList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None:
             query = self.request.GET.get('q')
             qs = qs.filter(Q(location__name__icontains=query) |
                            # Q(date_time__icontains=query) |
                            Q(severity_level__icontains=query) |
                            Q(description__icontains=query))
         return qs


class IncidentAdd(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = "incident_add.html"
    success_url = reverse_lazy('incident-list')

class IncidentUpdate(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = "incident_edit.html"
    success_url = reverse_lazy('incident-list')
    
class IncidentDelete(DeleteView):
    model = Incident
    template_name = "incident_delete.html"
    success_url = reverse_lazy('incident-list')


# Fire Stations Views
class FireStationList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = "firestation_list.html"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
         qs = super(FireStationList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None:
             query = self.request.GET.get('q')
             qs = qs.filter(Q(name__icontains=query) |
                           # Q(latitude__icontains=query) |
                            Q(address__icontains=query) |
                            Q(city__icontains=query) |
                            Q(country__icontains=query))
         return qs

class FireStationAdd(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = "firestation_add.html"
    success_url = reverse_lazy('firestation-list')

class FireStationUpdate(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = "firestation_edit.html"
    success_url = reverse_lazy('firestation-list')
    
class FireStationDelete(DeleteView):
    model = FireStation
    template_name = "firestation_delete.html"
    success_url = reverse_lazy('firestation-list')


# Locations Views
class LocationsList(ListView):
    model = Locations
    context_object_name = 'locations'
    template_name = "locations_list.html"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
         qs = super(LocationsList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None:
             query = self.request.GET.get('q')
             qs = qs.filter(Q(name__icontains=query) |
                           # Q(latitude__icontains=query) |
                            Q(address__icontains=query) |
                            Q(city__icontains=query) |
                            Q(country__icontains=query))
         return qs

class LocationsAdd(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = "locations_add.html"
    success_url = reverse_lazy('locations-list')

class LocationsUpdate(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = "locations_edit.html"
    success_url = reverse_lazy('locations-list')
    
class LocationsDelete(DeleteView):
    model = Locations
    template_name = "locations_delete.html"
    success_url = reverse_lazy('locations-list')


# Fire Fighters Views
class FirefightersList(ListView):
    model = Firefighters
    context_object_name = 'firefighters'
    template_name = "firefighters_list.html"
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
         qs = super(FirefightersList, self).get_queryset(*args, **kwargs)
         if self.request.GET.get("q") != None:
             query = self.request.GET.get('q')
             qs = qs.filter(Q(name__icontains=query) |
                            Q(rank__icontains=query) |
                            Q(experience_level__icontains=query) |
                            Q(station__icontains=query))
         return qs


class FirefightersAdd(CreateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = "firefighters_add.html"
    success_url = reverse_lazy('firefighters-list')

class FirefightersUpdate(UpdateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = "firefighters_edit.html"
    success_url = reverse_lazy('firefighters-list')
    
class FirefightersDelete(DeleteView):
    model = Firefighters
    template_name = "firefighters_delete.html"
    success_url = reverse_lazy('firefighters-list')