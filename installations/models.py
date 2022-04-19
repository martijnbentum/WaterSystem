from django.db import models
from partial_date import PartialDateField
from django.urls import reverse
# from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User
import unidecode
from colorfield.fields import ColorField
from utils.model_util import Helper


# User model
class UserProfileInfo(models.Model):
	# Create relationship (don't inherit from User!)
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
	profile_pic = models.ImageField(upload_to='profile_pics', blank=True)

	def __str__(self):
		# Built-in attribute of django.contrib.auth.models.User!
		return self.user.username


class City(models.Model):
	name = models.CharField(max_length=100, blank=False)
	latitude = models.DecimalField(max_digits=7, decimal_places=5, default=0)
	longitude = models.DecimalField(max_digits=7, decimal_places=5, default=0)

	def __str__(self):
		return self.name

	@property
	def installations(self):
		if hasattr(self,'_installations'): return self._installations
		self._installations = list(self.installation_set.all())
		return self._installations

	@property
	def installation_identifiers(self):
		return ','.join([x.identifier for x in self.installations])


class Style(models.Model):
	name = models.CharField(max_length=200)
	color = ColorField(default='#FF0000')
	stroke_opacity = models.FloatField(default=0.8, )
	stroke_weight = models.IntegerField(default=2)
	fill_opacity = models.FloatField(default=0.3)
	dashed = models.BooleanField(default=False)
	z_index = models.IntegerField(default=0)

	def __str__(self):
		return self.name + ' ' + self.color

class Neighbourhood(models.Model):
	name = models.CharField(max_length=300,default = '')
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, 
		null=False, default='')
	neighbourhood_number = models.PositiveIntegerField(null=True, blank=True)
	style= models.ForeignKey(Style, on_delete=models.SET_NULL, blank=True, 
		null=True, default=None)
	extent_shapefile = models.FileField(upload_to='shapefiles/', max_length=50, 
		null=True,blank=True)  # Is it correct way?

	def __str__(self):
		st = self.city.name + ' ' + str(self.neighbourhood_number)
		return st

	def save(self,*args,**kwargs):
		self.name = self.__str__()
		super(Neighbourhood,self).save(*args,**kwargs)
	
	def to_dict(self):
		d = {}
		d['name'] = self.name
		d['pk'] = self.pk
		d['style'] = self.style.pk if self.style else None
		d['geojson'] = self.extent_shapefile.name if self.extent_shapefile else None
		d['number'] = self.neighbourhood_number
		d['city'] = self.city.pk if self.city else None
		d['installation_ids'] = self.installation_ids
		return d

	@property
	def installations(self):
		if hasattr(self,'_installations'): return self._installations
		installations = self.installation_set.all()
		self._installations = installations if installations else None
		return self._installations

	@property
	def installation_ids(self):
		if self.installations: return [x.identifier for x in self.installations]
		return None


class Figure(models.Model):
	'''figure to be plotted on a map.'''
	name = models.CharField(max_length=200)
	style = models.ForeignKey(Style,  on_delete=models.SET_NULL, blank=False, 
		null=True, default='')
	start_date = PartialDateField(null=True, blank=True)
	end_date = PartialDateField(null=True, blank=True)
	geojson = models.FileField(upload_to='shapefiles/', null=False, 
		blank=False, default='')
	neighbourhood = models.ManyToManyField(Neighbourhood, blank=True)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, 
		null=False, default='')
	description = models.CharField(max_length=1000, blank=True, default='', null=True)
# Landmarks

	def __str__(self):
		return self.name

	def to_dict(self):
		d = {}
		d['name'] = self.name
		d['pk'] = self.pk
		d['style'] = self.style.pk if self.style else None
		d['city'] = self.city.pk if self.city else None
		d['installation_ids'] = self.installation_ids
		d['map_start_date'] = self.map_start_date
		d['map_end_date'] = self.map_end_date
		d['geojson'] = self.geojson.name if self.geojson else None
		d['description'] = self.description
		return d

	@property
	def installations(self):
		if hasattr(self,'_installations'): return self._installations
		installations = self.installation_set.all()
		self._installations = installations if installations else None
		return self._installations

	@property
	def installation_ids(self):
		if self.installations: return [x.identifier for x in self.installations]
		return None

	@property
	def map_start_date(self):
		if not self.installations: 
			if self.start_date: return self.start_date.year
			return None
		if len(self.installations) > 1:
			return min([x.map_start_date for x in self.installations])
		return self.installations[0].map_start_date 

	@property
	def map_end_date(self):
		if not self.installations: 
			if self.end_date: return self.end_date.year
			return None
		if len(self.installations) > 1:
			return min([x.map_end_date for x in self.installations])
		return self.installations[0].map_end_date	

class Religion(models.Model):
	name = models.CharField(max_length=100, blank=False)
	description = models.TextField(blank=True, default='', null=True)

	def __str__(self):
		return self.name


class SecondaryLiterature(models.Model):
	title = models.CharField(max_length=250, blank=False, default='', null=True)
	author = models.CharField(max_length=100, blank=False, default='', null=True)
	editor = models.CharField(max_length=100, blank=True, default='', null=True)
	book_title = models.CharField(max_length=250, blank=True, default='', null=True)
	journal = models.CharField(max_length=100, blank=True, default='', null=True)
	publisher = models.CharField(max_length=100, blank=True, default='', null=True)
	volume = models.CharField(max_length=25, blank=True, default='', null=True)
	issue = models.CharField(max_length=25, blank=True, default='', null=True)
	page_number = models.CharField(max_length=25, blank=True, default='', null=True)
	place = models.CharField(max_length=25, blank=True, default='', null=True)
	year = PartialDateField(blank=True, null=True, default='')
	status = models.BooleanField("Completed", default=False, blank=True)

	def __str__(self):
		return 'Author: ' + self.author + ' | Title: ' + self.title


class Evidence(models.Model):
	title = models.CharField(max_length=250, blank=False)
	author = models.CharField(max_length=100, blank=False, default='', null=True)
	date_lower = PartialDateField(blank=True, null=True)
	date_upper = PartialDateField(blank=True, null=True)
	secondary_literature = models.ForeignKey(SecondaryLiterature, 
		on_delete=models.SET_NULL, blank=True, default='',null=True)
	description = models.TextField(max_length=1000, blank=True, default='', null=True)
	status = models.BooleanField("Completed", default=False, blank=True)
	# searchable fields for fields with diacritics	(un: unaccent)
	un_title = models.CharField(max_length=250, blank=True, default='')  
	un_author = models.CharField(max_length=250, blank=True, default='')
	un_description = models.TextField(max_length=1000, blank=True, default='')

	def __str__(self):
		return 'Author: ' + self.author + ' | Title: ' + self.title

	def save(self):
		if not self.id:
			self.un_title = unidecode.unidecode(self.title)
			self.un_author = unidecode.unidecode(self.author)
			self.un_description = unidecode.unidecode(self.description)
		super(Evidence, self).save()

	def get_absolute_url(self):
		return reverse("installations:home", kwargs={'pk': self.pk})


class Person(models.Model):
	name = models.CharField(max_length=50, blank=False)
	GENDER = (
		('M', 'Male'),
		('F', 'Female'),
		('O', 'Other'),
	)
	gender = models.CharField(max_length=1, choices=GENDER, default='M')
	birth_lower = PartialDateField(blank=True, default='', null=True)
	birth_upper = PartialDateField(blank=True, default='', null=True)
	death_lower = PartialDateField(blank=True, default='', null=True)
	death_upper = PartialDateField(blank=True, default='', null=True)
	# Role field for person and type of involvement field for 
	# person-installation relation
	role = models.CharField(max_length=100, blank=True)  
	religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, 
		blank=True, default='', null=True)
	secondary_literature = models.ManyToManyField(SecondaryLiterature, blank=True)
	comment = models.TextField(max_length=1000, blank=True, default='', null=True)
	status = models.BooleanField("Completed", default=False, blank=True)
	# searchable fields for fields with diacritics	(un: unaccent)
	un_name = models.CharField(max_length=250, blank=True, default='')	
	un_role = models.CharField(max_length=250, blank=True, default='')
	un_comment = models.TextField(max_length=1000, blank=True, default='', null=True)

	def __str__(self):
		return self.name

	def save(self):
		if not self.id:
			self.un_name = unidecode.unidecode(self.name)
			self.un_role = unidecode.unidecode(self.role)
			self.un_comment = unidecode.unidecode(self.comment)
		super(Person, self).save()


class InstitutionType(models.Model):
	name = models.CharField(max_length=100, blank=False)
	description = models.TextField(max_length=1000, blank=True)
	# searchable fields for fields with diacritics	(un: unaccent)
	un_name = models.CharField(max_length=100, blank=True, default='')	

	def __str__(self):
		return self.name

	def save(self):
		if not self.id:
			self.un_name = unidecode.unidecode(self.name)
		super(InstitutionType, self).save()


class Purpose(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(max_length=1000, blank=True)

	def __str__(self):
		return self.name


class Institution(models.Model):
	name = models.CharField(max_length=100, blank=False)
	type = models.ForeignKey(InstitutionType, on_delete=models.SET_NULL, 
		blank=True, null=True)	# this will not be
	# used in the future. I didn't delete this because there is data saved 
	# for some entries on the database.
	type_many = models.ManyToManyField(InstitutionType, related_name='installations', 
		blank=True, default='')
	purpose = models.ManyToManyField(Purpose, blank=True)
	city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
	neighbourhood = models.ManyToManyField(Neighbourhood, blank=True)
	latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, 
		null=True, default=0)
	longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, 
		null=True, default=0)
	# this field is for test and explaine the partitial dat
	start_date_lower = PartialDateField(blank=True, null=True)	
	start_date_upper = PartialDateField(blank=True, null=True)
	first_reference_lower = PartialDateField(blank=True, null=True)
	first_reference_upper = PartialDateField(blank=True, null=True)
	end_date_lower = PartialDateField(blank=True, null=True)
	end_date_upper = PartialDateField(blank=True, null=True)
	religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, 
		blank=True, null=True)
	secondary_literature = models.ManyToManyField(SecondaryLiterature, blank=True)
	comment = models.TextField(max_length=1000, blank=True, default='', null=True)
	status = models.BooleanField("Completed", default=False, blank=True)
	# searchable fields for fields with diacritics	(un: unaccent)
	un_name = models.CharField(max_length=250, blank=True, default='')	
	un_comment = models.TextField(max_length=1000, blank=True, default='', null=True)

	def __str__(self):
		return self.name

	def save(self):
		if not self.id:
			self.un_name = unidecode.unidecode(self.name)
			self.un_comment = unidecode.unidecode(self.comment)
		super(Institution, self).save()


class Watersystem(models.Model):
	original_term = models.CharField(max_length=100, blank=False)
	type = models.CharField(max_length=100, blank=True, null=True)
	description = models.TextField(max_length=1000, blank=True, null=True)
	secondary_literature = models.ForeignKey(SecondaryLiterature, 
		on_delete=models.SET_NULL, blank=True, default='',
											 null=True)
	# searchable fields for fields with diacritics	(un: unaccent)
	un_original_term = models.CharField(max_length=100, blank=True,
										default='')  

	def __str__(self):
		if self.type is not None:
			s = self.original_term + ' (' + self.type + ')'
		else:
			s = self.original_term
		return s

	def save(self):
		if not self.id:
			self.un_original_term = unidecode.unidecode(self.original_term)
		super(Watersystem, self).save()

	@property
	def name(self):
		return self.__str__()

	@property
	def installations(self):
		if hasattr(self,'_installations'): return self._installations
		self._installations = []
		self._installations = list(self.installation_set.all())
		return self._installations

	@property
	def installation_identifiers(self):
		return ','.join([x.identifier for x in self.installations])

	@property
	def installation_count(self):
		return len(self.installations)


class WatersystemCategories(models.Model):
	name = models.CharField(max_length=250, blank=False)
	watersystem = models.ManyToManyField(Watersystem, blank=True)
	description = models.TextField(max_length=1000, blank=True, null=True)

	def __str__(self):
		return self.name

	@property
	def watersystems(self):
		if hasattr(self,'_watersystems'): return self._watersystems
		self._watersystems = list(self.watersystem.all())
		return self._watersystems

	@property
	def watersystem_names(self):
		return ','.join([x.name for x in self.watersystems])

	@property
	def watersystem_types(self):
		return ','.join([x.type for x in self.watersystems])

	@property
	def installations(self):
		if hasattr(self,'_installations'):return self._installations
		self._installations = []
		for watersystem in self.watersystems:
			self._installations.extend(watersystem.installations)
		return self._installations
			
	@property
	def installation_identifiers(self):
		return ','.join([x.identifier for x in self.installations])

	@property
	def installation_count(self):
		return len(self.installations)


class Installation(models.Model, Helper):
	name = models.CharField(max_length=250, blank=True, default='')
	watersystem = models.ForeignKey(Watersystem, on_delete=models.SET_NULL, 
		blank=True, null=True)
	construction_date_lower = PartialDateField(blank=True, null=True)
	construction_date_upper = PartialDateField(blank=True, null=True)
	first_reference_lower = PartialDateField(blank=True, null=True)
	first_reference_upper = PartialDateField(blank=True, null=True)
	end_functioning_year_lower = PartialDateField(blank=True, null=True)
	end_functioning_year_upper = PartialDateField(blank=True, null=True)
	purpose = models.ManyToManyField(Purpose, blank=True)
	city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
	neighbourhood = models.ManyToManyField(Neighbourhood, blank=True)
	latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, 
		null=True, default=0)
	longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, 
		null=True, default=0)
	institution_as_location = models.ForeignKey(Institution, on_delete=models.SET_NULL,
		blank=True, null=True)
	extent_shapefile = models.FileField(upload_to='shapefiles/', max_length=50, 
		null=True,blank=True)
	figure = models.ForeignKey(Figure, on_delete = models.SET_NULL, blank=True,null=True)
	secondary_literature = models.ManyToManyField(SecondaryLiterature, blank=True)
	comment = models.TextField(max_length=1000, blank=True, default='', null=True)
	status = models.BooleanField("Completed", default=False, blank=True, 
		help_text="Complete")
	# searchable fields for fields with diacritics	(un: unaccent)
	un_name = models.CharField(max_length=250, blank=True, default='')	
	un_comment = models.TextField(max_length=1000, blank=True, default='', null=True)

	def __str__(self):
		return self.name

	def save(self):
		if not self.id:
			self.un_name = unidecode.unidecode(self.name)
			self.un_comment = unidecode.unidecode(self.comment)
		super(Installation, self).save()

	@property
	def map_start_date(self):
		if self.construction_date_lower: return self.construction_date_lower.year
		elif self.construction_date_upper: return self.construction_date_upper.year
		elif self.first_reference_lower: return self.first_reference_lower.year
		elif self.first_reference_upper: return self.first_reference_upper.year
		return None

	@property
	def map_end_date(self):
		if self.end_functioning_year_upper: return self.end_functioning_year_upper.year
		if self.end_functioning_year_lower: return self.end_functioning_year_lower.year
		return None
		




# Relations
class CityPersonRelation(models.Model):
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True)
	person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True)
	type_of_involvement = models.CharField(max_length=100, blank=True)

	def __str__(self):
		message = "relation is " + self.type_of_involvement
		return message


class NeighbourhoodPersonRelation(models.Model):
	neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE, 
		blank=True)
	person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True)
	type_of_involvement = models.CharField(max_length=100, blank=True)

	def __str__(self):
		message = "relation is " + self.type_of_involvement
		return message


class PersonInstitutionRelation(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True)
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE, 
		blank=True, default='')
	type_of_involvement = models.CharField(max_length=50, blank=True)

	def __str__(self):
		message = "relation is " + self.type_of_involvement
		return message


class PersonInstallationRelation(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True)
	installation = models.ForeignKey(Installation, on_delete=models.CASCADE, 
		blank=True, default='')
	type_of_involvement = models.CharField(max_length=100, blank=True)

	def __str__(self):
		message = "relation is " + self.type_of_involvement
		return message


class CityInstallationRelation(models.Model):
	installation = models.ForeignKey(Installation, on_delete=models.CASCADE, 
		blank=False)
	city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True)
	capacity_absolute = models.DecimalField(max_digits=7, decimal_places=2, default=0)
	capacity_percentage=models.DecimalField(max_digits=7, decimal_places=2, default=0)


class InstitutionInstallationRelation(models.Model):
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE, 
		blank=True, default='')
	installation = models.ForeignKey(Installation, on_delete=models.CASCADE, 
		blank=True)
	type_of_involvement = models.CharField(max_length=100, blank=True)

	def __str__(self):
		message = "relation is " + self.type_of_involvement
		return message


class EvidencePersonRelation(models.Model):
	evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False)
	page_number = models.CharField(max_length=100,blank=False)
	description = models.TextField(max_length=1000, blank=True, default=0)

	def __str__(self):
		message = "relation is " + self.page_number + " " + self.description
		return message


class EvidenceInstitutionRelation(models.Model):
	evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE, 
		blank=True, default='')
	page_number = models.CharField(max_length=100,blank=False)
	description = models.TextField(max_length=1000, blank=True)

	def __str__(self):
		message = "relation is " + self.page_number + " " + self.description
		return message


class EvidenceInstallationRelation(models.Model):
	evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
	installation = models.ForeignKey(Installation, on_delete=models.CASCADE, 
		blank=True, default='')
	page_number = models.CharField(max_length=100,blank=True)
	description = models.TextField(max_length=1000, blank=True)

	def __str__(self):
		message = "relation is " + self.page_number + " " + self.description
		return message


class InstallationInstallationRelation(models.Model):
	primary = models.ForeignKey(Installation, related_name='primary', 
		on_delete=models.CASCADE)
	secondary = models.ForeignKey(Installation, related_name='secondary', 
		on_delete=models.CASCADE)
	description = models.CharField(max_length=1000, blank=True)


class InstitutionInstitutionRelation(models.Model):
	primary = models.ForeignKey(Institution, related_name='primary', 
		on_delete=models.CASCADE)
	secondary = models.ForeignKey(Institution, related_name='secondary', 
		on_delete=models.CASCADE)
	description = models.CharField(max_length=1000, blank=True)


class PersonPersonRelation(models.Model):
	primary = models.ForeignKey(Person, related_name='primary', 
		on_delete=models.CASCADE)
	secondary = models.ForeignKey(Person, related_name='secondary', 
		on_delete=models.CASCADE)
	description = models.CharField(max_length=1000, blank=True)


