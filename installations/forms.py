from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, HTML
from django.forms import ModelForm, inlineformset_factory
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django import forms

from .models import City, Institution, Person, UserProfileInfo
from .models import *
from utils.view_util import generate_num
from crispy_forms.helper import FormHelper
from django_select2 import forms as s2forms
from django.forms.widgets import ClearableFileInput


attrs_lower_bound={'placeholder': 'Please enter lower bound'}
attrs_upper_bound={'placeholder': 'Please enter upper bound'}

# Widgets
class InstitutionTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'name__icontains',
        'un_name__icontains',
    ]

class InstitutionTypeWidgetMulti(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'name__icontains',
        'un_name__icontains',
    ]

class CityWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

class NeighbourhoodWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'neighbourhood_number__icontains',
        'city__name__icontains',
    ]

class NeighbourhoodWidget2(s2forms.ModelSelect2Widget):  # this is for o
    search_fields = [
        'neighbourhood_number__icontains',
        'city__name__icontains',
    ]

class FigureWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

class ReligionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

class SecondaryLiteratureWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title__icontains",
        "author__icontains",
    ]

class SecondaryLiteratureWidgetMulti(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "title__icontains",
        "author__icontains",
    ]

class EvidenceWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title__icontains",
        "author__icontains",
        "un_title__icontains",
        "un_author__icontains",
    ]

class EvidenceWidgetMulti(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "title__icontains",
        "author__icontains",
        "un_title__icontains",
        "un_author__icontains",
    ]

class WatersystemWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'original_term__icontains',
        'un_original_term__icontains',
    ]

class WatersystemWidgetMulti(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'original_term__icontains',
        'un_original_term__icontains',
    ]

class PurposeWidget(s2forms.ModelSelect2MultipleWidget):
    model = Purpose
    search_fields = ['name__icontains']

class InstallationWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'name__icontains',
        'un_name__icontains',
    ]

class InstitutionWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'name__icontains',
        'un_name__icontains',
    ]

class PersonWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'name__icontains',
        'un_name__icontains',
    ]

class StyleWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains', ]


# User form
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')


class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        # fields = ('portfolio_site', 'profile_pic')
        fields = ()


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name', 'latitude', 'longitude']
        # its possible to use following line for all fields, also exclude
        # fields = '__all__'
        labels = {
            'name': 'City Name'
        }

    def __init__(self, *args, **kwargs):
        super(CityForm, self).__init__(*args, **kwargs)
        # self.fields['country'].empty_label = "Select"
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.helper = FormHelper()

class InstitutionForm(ModelForm):
    class Meta:
        model = Institution
        fields = '__all__'

    type = forms.ModelChoiceField(
        queryset=InstitutionType.objects.all(),
        # this line refreshes the list when a new item is entered using the plus button
        widget=InstitutionTypeWidget(
            attrs={'data-placeholder': 'Select institution type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}),
        required=False)
    type_many = forms.ModelMultipleChoiceField(
        queryset=InstitutionType.objects.all(),
        widget=InstitutionTypeWidgetMulti(
            attrs={'data-placeholder': 'Select institution type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}),
        required=False)
    purpose = forms.ModelMultipleChoiceField(
        queryset=Purpose.objects.all(),
        widget=PurposeWidget(
            attrs={'data-placeholder': 'Select purposes',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}),
        required=False)
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select city',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    neighbourhood = forms.ModelMultipleChoiceField(
        queryset=Neighbourhood.objects.all(),
        widget=NeighbourhoodWidget(
            attrs={'data-placeholder': 'Select neighbourhood',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    latitude = forms.DecimalField(max_digits=8, decimal_places=5,
        widget=forms.NumberInput(attrs={'placeholder': 'Latitude'}))
    longitude = forms.DecimalField(max_digits=8, decimal_places=5,
        widget=forms.NumberInput(attrs={'placeholder': 'Longitude'}))
    start_date_lower = forms.CharField(widget=forms.TextInput(attrs=attrs_lower_bound))
    start_date_upper = forms.CharField(widget=forms.TextInput(attrs=attrs_upper_bound))
    first_reference_lower=forms.CharField(widget=forms.TextInput(
        attrs=attrs_lower_bound))
    first_reference_upper=forms.CharField(widget=forms.TextInput(
        attrs=attrs_upper_bound))
    end_date_lower = forms.CharField(widget=forms.TextInput(attrs=attrs_lower_bound))
    end_date_upper = forms.CharField(widget=forms.TextInput(attrs=attrs_upper_bound))
    religion = forms.ModelChoiceField(
        queryset=Religion.objects.all(),
        widget=ReligionWidget(
            attrs={'data-placeholder': 'Select religion',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    secondary_literature = forms.ModelMultipleChoiceField(
        queryset=SecondaryLiterature.objects.all(),
        widget=SecondaryLiteratureWidgetMulti(
            attrs={'data-placeholder': 'Select secondary literature',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(InstitutionForm, self).__init__(*args, **kwargs)
        self.fields['type_many'].required = False
        self.fields['city'].required = False
        self.fields['neighbourhood'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['start_date_lower'].required = False
        self.fields['start_date_upper'].required = False
        self.fields['first_reference_lower'].required = False
        self.fields['first_reference_upper'].required = False
        self.fields['end_date_lower'].required = False
        self.fields['end_date_upper'].required = False
        self.fields['religion'].required = False
        self.fields['secondary_literature'].required = False
        self.fields['status'].required = False

        if not instance:
            name = 'Institution-'  
            name += str(generate_num('installations', 'Institution')).zfill(4)
            self.initial['name'] = name


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        widgets = {
            "religion": ReligionWidget(
                attrs={'data-placeholder': 'Select religion','style': 'width:100%;',
                    'class': 'searching','data-minimum-input-length': '0'}),
                                  
            "evidence": EvidenceWidget(
                attrs={'data-placeholder': 'Select evidence','style': 'width:100%;',
                    'class': 'searching','data-minimum-input-length': '0'}),
        }
    birth_lower = forms.CharField(widget=forms.TextInput(attrs=attrs_lower_bound))
    birth_upper = forms.CharField(widget=forms.TextInput(attrs=attrs_upper_bound))
    death_lower = forms.CharField(widget=forms.TextInput(attrs=attrs_lower_bound))
    death_upper = forms.CharField(widget=forms.TextInput(attrs=attrs_upper_bound))
    secondary_literature = forms.ModelMultipleChoiceField(
        queryset=SecondaryLiterature.objects.all(),
        widget=SecondaryLiteratureWidgetMulti(
            attrs={'data-placeholder': 'Select secondary literature',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['gender'].required = False
        self.fields['secondary_literature'].required = False
        self.fields['birth_lower'].required = False
        self.fields['birth_upper'].required = False
        self.fields['death_lower'].required = False
        self.fields['death_upper'].required = False
        self.fields['status'].required = False
        self.fields['secondary_literature'].empty_label = "Select secondary literature"
        self.fields['gender'].empty_label = "Select gender"


class SecondaryLiteratureForm(ModelForm):
    class Meta:
        model = SecondaryLiterature
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SecondaryLiteratureForm, self).__init__(*args, **kwargs)
        self.fields['journal'].required = False
        self.fields['publisher'].required = False
        self.fields['year'].required = False
        self.fields['status'].required = False


class InstallationForm(ModelForm):
    watersystem = forms.ModelChoiceField(
        # this line refreshes the list when new item is entered using plus button
        queryset=Watersystem.objects.all(),  
        widget=WatersystemWidget(
            attrs={'data-placeholder': 'Select a water system',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}),
        required=False)
    alb, aub = attrs_lower_bound, attrs_upper_bound
    construction_date_lower = forms.CharField(widget=forms.TextInput(attrs=alb))
    construction_date_upper = forms.CharField(widget=forms.TextInput(attrs=aub))
    first_reference_lower = forms.CharField(widget=forms.TextInput(attrs=alb))
    first_reference_upper = forms.CharField(widget=forms.TextInput(attrs=aub))
    end_functioning_year_lower = forms.CharField(
        widget=forms.TextInput(attrs=alb))
    end_functioning_year_upper = forms.CharField(
        widget=forms.TextInput(attrs=aub))
    purpose = forms.ModelMultipleChoiceField(
        queryset=Purpose.objects.all().order_by('name'),
        widget=PurposeWidget(
            attrs={'data-placeholder': 'Select purposes',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}),
        required=False)
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select city',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    neighbourhood = forms.ModelMultipleChoiceField(
        queryset=Neighbourhood.objects.all(),
        widget=NeighbourhoodWidget(
            attrs={'data-placeholder': 'Select neighbourhood',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    latitude = forms.DecimalField(max_digits=8, decimal_places=5,
        widget=forms.NumberInput(attrs={'placeholder': 'Latitude'}))
    longitude = forms.DecimalField(max_digits=8, decimal_places=5,
        widget=forms.NumberInput(attrs={'placeholder': 'Longitude'}))
    institution_as_location = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstitutionWidget(
            attrs={'data-placeholder': 'Select institution as location ',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    # extent_shapefile = forms.FileField(widget=forms.ClearableFileInput)
    figure= forms.ModelChoiceField(
        queryset=Figure.objects.all(),
        widget=FigureWidget(
            attrs={'data-placeholder': 'Select figure',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    secondary_literature = forms.ModelMultipleChoiceField(
        queryset=SecondaryLiterature.objects.all(),
        widget=SecondaryLiteratureWidgetMulti(
            attrs={'data-placeholder': 'Select secondary literature',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    class Meta:
        model = Installation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(InstallationForm, self).__init__(*args, **kwargs)
        self.fields['watersystem'].required = False
        self.fields['construction_date_lower'].required = False
        self.fields['construction_date_upper'].required = False
        self.fields['first_reference_lower'].required = False
        self.fields['first_reference_upper'].required = False
        self.fields['end_functioning_year_lower'].required = False
        self.fields['end_functioning_year_upper'].required = False
        self.fields['purpose'].required = False
        self.fields['city'].required = False
        self.fields['neighbourhood'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['institution_as_location'].required = False
        # self.fields['extent_shapefile'].required = False
        self.fields['figure'].required = False
        self.fields['secondary_literature'].required = False
        self.fields['comment'].required = False
        self.fields['status'].required = False

        if not instance:
            name = 'Installation-' 
            name += str(generate_num('installations', 'Installation')).zfill(4)
            self.initial['name'] = name



class EvidenceForm(ModelForm):
    date_lower = forms.CharField(widget=forms.TextInput(attrs=attrs_lower_bound))
    date_upper = forms.CharField(widget=forms.TextInput(attrs=attrs_upper_bound))
    secondary_literature = forms.ModelChoiceField(
        queryset=SecondaryLiterature.objects.all(),
        widget=SecondaryLiteratureWidget(
            attrs={'data-placeholder': 'Select secondary literature',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}),
        required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    class Meta:
        model = Evidence
        f = 'title,author,date_lower,date_upper,secondary_literature,description'
        f += ',status'
        fields = f.split(',')

    def __init__(self, *args, **kwargs):
        super(EvidenceForm, self).__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['date_lower'].required = False
        self.fields['date_upper'].required = False
        self.fields['status'].required = False


# Landmarks
class FigureForm(ModelForm):
    style = forms.ModelChoiceField(
        queryset=Style.objects.all(),
        widget=StyleWidget(
            attrs={'data-placeholder': 'Select style',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    start_date=forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'start date'}))
    end_date = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'end date'}))
    neighbourhood = forms.ModelMultipleChoiceField(
        queryset=Neighbourhood.objects.all(),
        widget=NeighbourhoodWidget(
            attrs={'data-placeholder': 'Select neighbourhood',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select city',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 4}))

    class Meta:
        model = Figure
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(FigureForm, self).__init__(*args, **kwargs)
        self.fields['style'].required = True
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['city'].required = False
        self.fields['description'].required = False
        self.fields['neighbourhood'].required = False
        self.fields['geojson'].required = True


class WatersystemForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}))
    secondary_literature = forms.ModelChoiceField(
        queryset=SecondaryLiterature.objects.all(),
        widget=SecondaryLiteratureWidget(
            attrs={'data-placeholder': 'Select secondary literature',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = Watersystem
        fields = ('original_term', 'type', 'secondary_literature', 'description')

    def __init__(self, *args, **kwargs):
        super(WatersystemForm, self).__init__(*args, **kwargs)
        self.fields['type'].required = False
        self.fields['secondary_literature'].required = False
        self.fields['description'].required = False


class WatersystemCategoriesForm(ModelForm):
    watersystem = forms.ModelMultipleChoiceField(
        queryset=Watersystem.objects.all(),
        widget=WatersystemWidgetMulti(
            attrs={'data-placeholder': 'Select water systems',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)

    class Meta:
        model = WatersystemCategories
        fields = ('name', 'watersystem', 'description')

    def __init__(self, *args, **kwargs):
        super(WatersystemCategoriesForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['watersystem'].required = False
        self.fields['description'].required = False


class NeighbourhoodForm(ModelForm):
    extent_shapefile = forms.FileField(widget=forms.ClearableFileInput)

    style= forms.ModelChoiceField(
        queryset=Style.objects.all(),
        widget=StyleWidget(
            attrs={'data-placeholder': 'Select style',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = Neighbourhood
        fields = ('city', 'neighbourhood_number', 'style', 'extent_shapefile')

    def __init__(self, *args, **kwargs):
        super(NeighbourhoodForm, self).__init__(*args, **kwargs)
        # self.fields['style'].required = False


class InstitutionTypeForms(ModelForm):
    name = forms.CharField()

    class Meta:
        model = InstitutionType
        fields = ('name', 'description')


# Relations form
class CityPersonRelationForm(ModelForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select city',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = CityPersonRelation
        fields = ('city', 'person', 'type_of_involvement')
        # widget = {
        #     "city": CityWidget,
        # }


class NeighbourhoodPersonRelationForm(ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    neighbourhood = forms.ModelChoiceField(
        queryset=Neighbourhood.objects.all(),
        widget=NeighbourhoodWidget2(
            attrs={'data-placeholder': 'Select neighbourhood',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = NeighbourhoodPersonRelation
        fields = ('neighbourhood', 'person', 'type_of_involvement')


class PersonInstitutionRelationForm(ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select a person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstitutionWidget(
            attrs={'data-placeholder': 'Select institution',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = PersonInstitutionRelation
        fields = ('person', 'institution', 'type_of_involvement')


class PersonInstallationRelationForm(ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select a person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    installation = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = PersonInstallationRelation
        fields = ('person', 'installation', 'type_of_involvement')


class EvidencePersonRelationForm(ModelForm):
    evidence = forms.ModelChoiceField(
        queryset=Evidence.objects.all(),
        widget=EvidenceWidget(
            attrs={'data-placeholder': 'Select evidence',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    page_number = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 4}),
        required=False)

    class Meta:
        model = EvidencePersonRelation
        fields = ('evidence', 'person', 'page_number', 'description')


class InstitutionInstallationRelationForm(ModelForm):
    installation = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstitutionWidget(
            attrs={'data-placeholder': 'Select institution',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))

    class Meta:
        model = InstitutionInstallationRelation
        fields = ('institution', 'installation', 'type_of_involvement')


class EvidenceInstallationRelationForm(ModelForm):
    evidence = forms.ModelChoiceField(
        queryset=Evidence.objects.all(),
        widget=EvidenceWidget(
            attrs={'data-placeholder': 'Select evidence',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    installation = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    page_number = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 4}),
        required=False)

    class Meta:
        model = EvidenceInstallationRelation
        fields = ('evidence', 'installation', 'page_number', 'description')


class EvidenceInstitutionRelationForm(ModelForm):
    evidence = forms.ModelChoiceField(
        queryset=Evidence.objects.all(),
        widget=EvidenceWidget(
            attrs={'data-placeholder': 'Select evidence',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstitutionWidget(
            attrs={'data-placeholder': 'Select institution',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    page_number = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 4}),
        required=False)

    class Meta:
        model = EvidenceInstitutionRelation
        fields = ('evidence', 'institution', 'page_number', 'description')


class InstallationInstallationRelationForm(ModelForm):
    primary = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    secondary = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 1}),
        required=False)

    class Meta:
        model = InstallationInstallationRelation
        fields = ('primary', 'secondary', 'description')


class InstitutionInstitutionRelationForm(ModelForm):
    primary = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstitutionWidget(
            attrs={'data-placeholder': 'Select institution',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    secondary = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstitutionWidget(
            attrs={'data-placeholder': 'Select institution',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 1}),
        required=False)

    class Meta:
        model = InstitutionInstitutionRelation
        fields = ('primary', 'secondary', 'description')


class PersonPersonRelationForm(ModelForm):
    primary = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    secondary = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '0'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 1}),
        required=False)

    class Meta:
        model = PersonPersonRelation
        fields = ('primary', 'secondary', 'description')


# Formsets
personcity_formset = inlineformset_factory(
    Person, CityPersonRelation, form=CityPersonRelationForm, extra=1)

personneighbourhood_formset = inlineformset_factory(
    Person, NeighbourhoodPersonRelation, form=NeighbourhoodPersonRelationForm, extra=1)

personinstitution_formset = inlineformset_factory(
    Person, PersonInstitutionRelation, form=PersonInstitutionRelationForm, extra=1)
institutionperson_formset = inlineformset_factory(
    Institution, PersonInstitutionRelation, form=PersonInstitutionRelationForm, 
    extra=1)

personinstallation_formset = inlineformset_factory(
    Person, PersonInstallationRelation, form=PersonInstallationRelationForm, extra=1)
installationperson_formset = inlineformset_factory(
    Installation, PersonInstallationRelation, form=PersonInstallationRelationForm, 
    extra=1)

personevidence_formset = inlineformset_factory(
    Person, EvidencePersonRelation, form=EvidencePersonRelationForm, extra=1)
evidenceperson_formset = inlineformset_factory(
    Evidence, EvidencePersonRelation, form=EvidencePersonRelationForm, extra=1)

installationinstitution_formset = inlineformset_factory(
    Installation, InstitutionInstallationRelation, 
    form=InstitutionInstallationRelationForm, extra=1)
institutioninstallation_formset = inlineformset_factory(
    Institution, InstitutionInstallationRelation, 
    form=InstitutionInstallationRelationForm, extra=1)

installationevidence_formset = inlineformset_factory(
    Installation, EvidenceInstallationRelation, 
    form=EvidenceInstallationRelationForm, extra=1)
evidenceinstallation_formset = inlineformset_factory(
    Evidence, EvidenceInstallationRelation, form=EvidenceInstallationRelationForm, 
    extra=1)

institutionevidence_formset = inlineformset_factory(
    Institution, EvidenceInstitutionRelation, 
    form=EvidenceInstitutionRelationForm, extra=1)
evidenceinstitution_formset = inlineformset_factory(
    Evidence, EvidenceInstitutionRelation, form=EvidenceInstitutionRelationForm, 
    extra=1)

installationinstallation_formset = inlineformset_factory(
    Installation, InstallationInstallationRelation, 
    fk_name='primary', fields='__all__', extra=1,
    form=InstallationInstallationRelationForm)

institutioninstitution_formset = inlineformset_factory(
    Institution, InstitutionInstitutionRelation, fk_name='primary', 
    fields='__all__', extra=1,
    form=InstitutionInstitutionRelationForm)

personperson_formset = inlineformset_factory(
    Person, PersonPersonRelation, fk_name='primary', fields='__all__', 
    extra=1, form=PersonPersonRelationForm)

dattr = {'attrs': {'style': 'width:100%'}}
dnumber = {'widget': forms.NumberInput(attrs={'style': 'width:100%', 'rows': 3}), 
    'required': False}
dchar_required = {'widget': forms.TextInput(**dattr), 'required': True}


class StyleForm(ModelForm):
    name = forms.CharField(**dchar_required)
    stroke_opacity = forms.FloatField(**dnumber)
    stroke_weight = forms.IntegerField(**dnumber)
    fill_opacity = forms.FloatField(**dnumber)
    z_index = forms.FloatField(**dnumber)

    class Meta:
        model = Style
        f = 'stroke_weight,stroke_opacity,color,fill_opacity'
        f += ',dashed,name,z_index'
        fields = f.split(',')
