from django.contrib import admin
from django.urls import path
from fire.views import HomePageView, map_station, fire_map

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('stations/', map_station, name='map-station'),
    path('fire-map/', fire_map, name='fire-map'),
]