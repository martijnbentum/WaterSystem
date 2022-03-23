from django.http import JsonResponse
from django.shortcuts import render 
from django.core import serializers
import json
from utils import map_util
from utils import model_util
import os
import sys
from waterSystem import settings

from installations.models import Figure, Style, City, Neighbourhood 
from installations.models import Institution, Installation, WatersystemCategories

# Map Visualization map MAP
def MapVisualization(request, city = 'Cairo'):
    figures = [x.to_dict() for x in Figure.objects.all()]
    s = Style.objects.all()
    s = serializers.serialize('json', s)
    s = json.loads(s)
    cities = City.objects.all() # used for the selection dropdown
    # used for having access to the fields of city model in the js scripts
    cjs = serializers.serialize('json', cities)
    cjs = json.loads(cjs) 
    neighbourhoods = [x.to_dict() for x in Neighbourhood.objects.all()]
    installations = Installation.objects.all()
    date_range = map_util.installation_date_range(installations)
    watersystemcategories = WatersystemCategories.objects.all()
    filters = map_util.Filters().to_dict()
    context = {'page_name': 'Map', 'figures': figures, 'styles': s, 
    'cjs':cjs, 'cities':cities,'date_range':date_range,
    'installations':installations,'watersystemcategories':watersystemcategories,
    'city':city,'filters':filters, 'neighbourhoods':neighbourhoods}
    return render(request, 'map/map.html', context)

def geojson_file(request, filename):
    path = settings.MEDIA_DIR + '/shapefiles/'+filename
    if not os.path.isfile(path): 
        print('file not found',path,filename)
        return JsonResponse({'file': False})
    a = open(path).read()
    try:data = json.loads(a)
    except:
        print('could not load json file:',path,filename,'error info:',sys.exc_info())
        return JsonResponse({'json': False})
    print('succesfully loaded:',filename,path)
    return JsonResponse(data)

def get_map_representation(request, installation_identifier):
    installation = model_util.identifier2instance(installation_identifier)
    d = {'neighbourhoods':[n.to_dict() for n in installation.neighbourhoods]}
    if installation.figure:
        d['figure'] = installation.figure.to_dict()
    else: d['figure'] = None
    d['latitude'] = installation.latitude 
    d['longitude'] = installation.longitude
    return JsonResponse(d)



