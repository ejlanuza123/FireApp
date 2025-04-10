from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Incident, FireStation, Locations

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

def fire_map(request):
    # Get all unique cities from incidents
    cities = Locations.objects.values_list('city', flat=True).distinct()
    selected_city = request.GET.get('city')
    
    # Get all incidents with related location data
    incidents = Incident.objects.select_related('location').all()
    
    if selected_city:
        incidents = incidents.filter(location__city=selected_city)
    
    # Prepare data for map
    incidents_data = []
    for incident in incidents:
        incidents_data.append({
            'id': incident.id,
            'severity': incident.severity_level,
            'date': incident.date_time.strftime('%Y-%m-%d') if incident.date_time else '',
            'description': incident.description,
            'latitude': float(incident.location.latitude),
            'longitude': float(incident.location.longitude),
            'address': incident.location.address,
            'city': incident.location.city
        })
    
    # Get fire stations for reference
    fire_stations = FireStation.objects.values('name', 'latitude', 'longitude', 'city')
    stations_data = [{
        'name': fs['name'],
        'latitude': float(fs['latitude']),
        'longitude': float(fs['longitude']),
        'city': fs['city']
    } for fs in fire_stations if fs['latitude'] and fs['longitude']]

    context = {
        'incidents': incidents_data,
        'stations': stations_data,
        'cities': cities,
        'selected_city': selected_city
    }
    return render(request, 'fire_map.html', context)

def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude', 'city')
    
    for fs in fireStations:
        if fs['latitude'] and fs['longitude']:
            fs['latitude'] = float(fs['latitude'])
            fs['longitude'] = float(fs['longitude'])
    
    context = {
        'fireStations': [fs for fs in fireStations if 'latitude' in fs],
    }
    return render(request, 'map_station.html', context)