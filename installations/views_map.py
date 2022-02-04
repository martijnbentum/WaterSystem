from django.http import JsonResponse
from django.shortcuts import render 
from django.core import serializers
import json

from .models import Figure, Style, City, Neighbourhood

# Map Visualization map MAP
def MapVisualization(request):
    f = Figure.objects.all()
    f = serializers.serialize('json', f)
    f = json.loads(f)
    s = Style.objects.all()
    s = serializers.serialize('json', s)
    s = json.loads(s)
    cities = City.objects.all() # used for the selection dropdown
    cjs = serializers.serialize('json', cities)
    # used for having access to the fields of city model in the js scripts
    cjs = json.loads(cjs) 
    n = Neighbourhood.objects.all()
    n = serializers.serialize('json', n)
    n = json.loads(n)
    context = {'page_name': 'Map', 'figures': f, 'styles': s, 
        'cities': cities, 'cjs':cjs, 'neighbourhoods':n}
    return render(request, 'installations/map_visualization.html', context)

def geojson_file(request, filename):
    print(filename)
    if not os.path.isfile('media/shapefiles/'+filename): data = {'file': False}
    a = open('media/shapefiles/'+filename).read()
    try:
        data = json.loads(a)
    except:
        data = {'json': False}
    return JsonResponse(data)
