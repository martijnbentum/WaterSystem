from django.http import JsonResponse
from django.shortcuts import render 
from django.core import serializers
import json
from utils import map_util
import os
import sys
from waterSystem import settings

from .models import Figure, Style, City, Neighbourhood, Institution, Installation

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
	installations = Installation.objects.all()
	context = {'page_name': 'Map', 'figures': f, 'styles': s, 
	'cities': cities, 'cjs':cjs, 'neighbourhoods':n,
	'installations':installations}
	return render(request, 'installations/map_visualization.html', context)

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
