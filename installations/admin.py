from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(City)
admin.site.register(Religion)
admin.site.register(Person)
admin.site.register(CityPersonRelation)
admin.site.register(Watersystem)
admin.site.register(Installation)
admin.site.register(CityInstallationRelation)
admin.site.register(Institution)
admin.site.register(InstitutionType)
admin.site.register(SecondaryLiterature)
admin.site.register(Evidence)
admin.site.register(UserProfileInfo)
admin.site.register(Neighbourhood)
admin.site.register(InstitutionInstallationRelation)
admin.site.register(EvidencePersonRelation)
admin.site.register(EvidenceInstallationRelation)
admin.site.register(EvidenceInstitutionRelation)
admin.site.register(Style)
