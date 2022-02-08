import random
import string
from django.core import serializers
import json

class info():
	'''inherit from this class to add extra viewing functionality for models'''

	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	def view(self):
		'''show all attributes of instance'''
		print(self.UNDERLINE,self.__class__,self.END)
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		for k in self.__dict__.keys():
			print(k.ljust(n),self.BLUE,self.__dict__[k], self.END)

	@property
	def info(self):
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		m = '<table class="table table-borderless" >'
		for k in self.__dict__.keys():
			if k == '_state' or k == 'id': continue
			m += '<tr class="d-flex">'
			m += '<th class="col-2">'+k.ljust(n)+'</th>'
			m += '<td class="col-8">'+str(self.__dict__[k]) +'</td>'
		m += '</table>'
		return m

	

class Helper:
	@property
	def identifier(self):
		app_name, model_name = instance2names(self)
		return '_'.join([app_name,model_name,str(self.pk)]).lower()

	@property
	def detail_url(self):
		app_name, model_name = instance2names(self)
		return app_name + ':' + model_name.lower()

	@property
	def edit_url(self):
		app_name, model_name = instance2names(self)
		return app_name + ':' + model_name.lower() + ':new' 

	@property
	def start_date_str(self):
		if self.construction_date_lower and self.construction_date_upper:
			if self.construction_date_lower == self.construction_date_upper:
				return str(self.construction_date_lower.year)
			ly = str(self.construction_date_lower.year)
			uy = str(self.construction_date_upper.year)
			return '(' + ly + ' ' + uy + ')'
		if self.construction_date_lower:
			return str(self.construction_date_lower.year)
		if self.construction_date_upper:
			return str(self.construction_date_upper.year)
		return ''

	@property
	def end_date_str(self):
		if self.end_functioning_year_lower and self.end_functioning_year_upper:
			if self.end_functioning_year_lower == self.end_functioning_year_upper:
				return str(self.end_functioning_year_upper.year)
			ly = str(self.end_functioning_year_lower.year)
			uy = str(self.end_functioning_year_upper.year)
			return '(' + ly + ' ' + uy + ')'
		if self.end_functioning_year_lower:
			return str(self.end_functioning_year_lower.year)
		if self.end_functioning_year_upper:
			return str(self.end_functioning_year_upper.year)
		return ''

	@property
	def start_date(self):
		if self.construction_date_lower: 
			return self.construction_date_lower
		if self.construction_date_upper:
			return self.construction_date_upper
		return None
		
	@property
	def end_date(self):
		if self.end_functioning_year_upper: 
			return self.end_functioning_year_upper
		if self.end_functioning_year_lower:
			return self.end_functioning_year_lower
		return None


	@property
	def has_exact_location(self):
		return bool(self.extent_shapefile and self.latitude and self.longitude)



def id_generator(id_type= 'letters', length = 9):
	if id_type == 'letters':
		return ''.join(random.sample(string.ascii_letters*length,length))
	if id_type == 'numbers':
		return int(''.join(random.sample('123456789'*length,length)))


def instance2names(instance):
    app_name = instance._meta.app_label 
    model_name = instance._meta.model_name.capitalize()
    return app_name, model_name

def instance2name(instance):
    app_name, model_name = instance2names(instance)
    return model_name

def model2json(model):
	app_name, model_name = instance2names(model)
	instances = model.objects.all()
	o = serializers.serialize('json',instances)
	filename = app_name + '_' + model_name + '.json'
	with open(filename,'w') as fout:
		json.dump(o,fout)
	return o
	
	
