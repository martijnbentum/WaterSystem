from django.conf.urls import url
from django.urls import path
from . import views

# TEMPLATE URLS
app_name = 'map'

urlpatterns = [
    path('map/', views.MapVisualization, name='map-visualization'),
    path('geojson_file/shapefiles/<str:filename>/', views.geojson_file, 
        name='geojson_file'),
    path('get_map_representation/<str:installation_identifier>/', views.get_map_representation, 
        name='get_map_representation'),
	]
