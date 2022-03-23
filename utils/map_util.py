from installations.models import Figure, Style, City, Neighbourhood, Installation 
from installations.models import Institution, Installation, WatersystemCategories
import json

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
    
class Filters():
    def __init__(self):
        self.watersystemcategories = WatersystemCategories.objects.all()
        self.make_all()

    def make_all(self):
        self._make_category_filters()
        self._make_installation_ids2city_dict()
        self._make_city2installation_ids_dict()
        
    def _make_category_filters(self):
        self.category_filters,self.installations = [],[]
        self.filters,self.installation_ids = [],[]
        for watersystem_category in self.watersystemcategories:
            cf = CategoryFilter(watersystem_category)
            self.filters.extend(cf.filters)
            self.category_filters.append(cf)
            self.installation_ids.extend(cf.installation_ids)
            self.installations.extend(cf.installations)

    def _make_installation_ids2city_dict(self):
        self.installation_ids2city_dict = {}
        for f in self.filters:
            self.installation_ids2city_dict.update(f.installation_ids2city_dict)

    def _make_city2installation_ids_dict(self):
        self.city2installation_ids_dict = {}
        for installation_id, city in self.installation_ids2city_dict.items():
            if city not in self.city2installation_ids_dict.keys():
                self.city2installation_ids_dict[city] = []
            self.city2installation_ids_dict[city].append(installation_id)

    def to_dict(self):
        d = {'filters':[],'category_filters':[],'installation_ids':self.installation_ids}
        d['filter_dict'] = {}
        d['category_filter_dict'] = {}
        d['city2installations'] = self.city2installation_ids_dict
        d['installations2city'] = self.installation_ids2city_dict
        for cf in self.category_filters:
            cfd = cf.to_dict()
            d['category_filters'].append(cfd)
            d['category_filter_dict'][cf.name] = cfd
            d['filters'].extend(cfd['filters'])
        for f in self.filters:
            d['filter_dict'][f.name] = f.to_dict()
        return d




class CategoryFilter():
    def __init__(self, watersystem_category):
        self.watersystem_category = watersystem_category
        self.name = watersystem_category.name
        self._set_all()

    def __repr__(self):
        m = self.name.ljust(15) +' | '
        m += 'ninstallations: ' + str(len(self.installations)).ljust(3) + ' | '
        m += 'nfilters: ' + str(len(self.filters)).ljust(3) + ' | '
        m += ', '.join([f.name for f in self.filters]) 
        return m

    def _set_all(self):
        self.watersystems = self.watersystem_category.watersystems
        self._group_watersystem_types()
        self.filters,self.installations,self.installation_ids = [], [], []
        wc = self.watersystem_category
        for watersystem_type, watersystem_instances in self.watersystem_types.items():
            f = Filter(watersystem_type,watersystem_instances,wc)
            self.filters.append(f)
            self.installations.extend(f.installations)
            self.installation_ids.extend(f.installation_ids)
        self.filter_names = ','.join([f.name for f in self.filters])

    def _group_watersystem_types(self):
        self.watersystem_types = {}
        for watersystem in self.watersystems:
            if watersystem.type not in self.watersystem_types.keys():
                self.watersystem_types[watersystem.type] = []
            self.watersystem_types[watersystem.type].append(watersystem)

    def to_dict(self):
        d = {'name':self.name}
        d['ninstallations'] = len(self.installations)
        d['nfilters']=len(self.filters)
        d['filter_names']=self.filter_names
        d['installation_ids_str'] = ','.join(self.installation_ids)
        d['filters'] = []
        d['active'] =True
        d['filter_dict'] = {}
        for f in self.filters:
            fd = f.to_dict()
            d['filters'].append(fd)
            d['filter_dict'][f.name] = fd
        return d

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d)

        

class Filter():
    def __init__(self, name, watersystem_instances, watersystem_category):
        self.name = name.replace(',','')
        self.watersystem_instances = watersystem_instances
        self.watersystem_category = watersystem_category
        self.category_name = watersystem_category.name
        self._set_all()

    def __repr__(self):
        m = self.name.ljust(15) +' | '
        m += 'ninstallations: ' + str(len(self.installations)).ljust(3) + ' | '
        m += ', '.join([wi.name for wi in self.watersystem_instances]) 
        return m
        
    def _set_all(self):
        self._set_installations()
        self._make_installation_ids2city_dict()

    def _set_installations(self):
        self.installations = []
        self.installation_ids = []
        for watersystem in self.watersystem_instances:
            self.installations.extend([i for i in watersystem.installations if i.city])
            self.installation_ids.extend(watersystem.installation_identifiers.split(','))

    def _make_installation_ids2city_dict(self):
        self.installation_ids2city_dict = {}
        for installation in self.installations:
            if not installation.city:continue
            self.installation_ids2city_dict[installation.identifier] = installation.city.name

    def to_dict(self):
        d = {}
        d['ninstallations'] = len(self.installations)
        d['installation_ids_str'] = ','.join(self.installation_ids)
        d['active'] =True
        for k, value in self.__dict__.items():
            if k in 'watersystem_category,watersystem_instances,installations':continue
            d[k] =value
        return d

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d)
        

def installation_date_range():
    installations = Installation.objects.all()
    earliest_date = 10000
    latest_date = 0
    for installation in installations:
        start = installation.map_start_date
        end = installation.map_end_date
        if start and start < earliest_date:
            earliest_date = start
        if end and end > latest_date: 
            latest_date = end
    if earliest_date > latest_date: earliest_date = 0
    if latest_date == 0: latest_date = 2000
    d = {'earliest_date':earliest_date, 'latest_date':latest_date}
    return d

