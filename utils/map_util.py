from installations.models import Figure, Style, City, Neighbourhood 
from installations.models import Institution, Installation

def city_to_installation_dict():
	cities = City.objects.all()
	d = {}
	for city in cities:
		installations = Installation.objects.filter(city__name = city.name)
		d[city.name] = installations
	return d

def city_figure_dict():
	cities = City.objects.all()
	d = {}
	for city in cities:
		figures= Figure.objects.filter(city__name = city.name)
		d[city.name] = figures
	return d

def earliest_latest_figure(city = '', figures = None):
	city_name = _get_city_name(city)
	if city_name: figures = Figure.objects.filter(city__name = city_name)
	if not figures: raise ValueError('provide city or figures')
	fl = [x for x in figures if x.start_date]
	fl= sorted(fl, key = lambda x:x.start_date)
	earliest_date = fl[0].start_date.year
	fu = [x for x in figures if x.end_date]
	fu= sorted(fu, key = lambda x:x.end_date)
	latest_date = fu[-1].end_date.year
	return earliest_date, latest_date

def earliest_latest_installation(city = '', installations= None):
	city_name = _get_city_name(city)
	if city_name: installations = Installation.objects.filter(city__name = city_name)
	if not installations: raise ValueError('provide city or installations')
	il = [x for x in installations if x.start_date]
	il= sorted(il, key = lambda x:x.start_date)
	earliest_date = il[0].start_date.year
	ui= [x for x in installations if x.end_date]
	ui= sorted(ui, key = lambda x:x.end_date)
	latest_date = ui[-1].end_date.year
	return earliest_date, latest_date

def get_date_span(city):
	city_name = _get_city_name(city)
	edf,ldf = earliest_latest_figure(city_name)
	edi,ldi = earliest_latest_installation(city_name)
	earliest_date = edf if edf < edi else edi
	latest_date = ldf if ldf > ldi else ldi
	return earliest_date, latest_date
	
	
def _get_city_name(city):
	if hasattr(city,'name'): city_name = city.name
	elif type(city) == str: city_name = city
	else: city_name = None
	return city_name
	
