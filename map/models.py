from django.db import models
from installations.models import City

# Create your models here.
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
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, 
        null=False, default='')
    neighbourhood_number = models.PositiveIntegerField(null=True, blank=True)
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, blank=True, 
        null=True, default=None)
    extent_shapefile = models.FileField(upload_to='shapefiles/', max_length=50, 
        null=True,blank=True)  # Is it correct way?

    def __str__(self):
        st = self.city.name + ' ' + str(self.neighbourhood_number)
        return st

class Figure(models.Model):
    '''figure to be plotted on a map.'''
    name = models.CharField(max_length=200)
    style = models.ForeignKey(Style,  on_delete=models.SET_NULL, blank=False, 
        null=False, default='')
    start_date = PartialDateField(null=True, blank=True)
    end_date = PartialDateField(null=True, blank=True)
    geojson = models.FileField(upload_to='shapefiles/', null=False, 
        blank=False, default='')
    neighbourhood = models.ManyToManyField(Neighbourhood, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, 
        null=False, default='')
    description = models.CharField(max_length=1000, blank=True, default='', null=True)
