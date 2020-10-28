from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Layout, Fieldset, HTML
from django.forms import ModelForm, inlineformset_factory
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django import forms

from .models import City, Institution, Person, UserProfileInfo
from .models import *
from crispy_forms.helper import FormHelper
from django_select2 import forms as s2forms


# Widgets
class InstitutionTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class CityWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class NeighbourhoodWidget(s2forms.ModelSelect2Widget):
    search_fields = ['neighbourhood_number__icontains']


class LocationWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'latitude__icontains',
        'longitude__icontains',
        ]
class ReligionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class SecondaryLiteratureWidget(s2forms.ModelSelect2Widget):
    search_fields = ['title__icontains']
    # search_fields = ['title__startswith'] this can used if you want to search based on first letter


class EvidenceWidget(s2forms.ModelSelect2Widget):
    search_fields = ['title__icontains']


class WatersystemWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

class PurposeWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ['name__icontains']

class InstallationWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

class InstitutionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

class PersonWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


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


#
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

        labels = {
            'name': 'Institution Name',
            'policy': 'Period'
        }
        widgets = {
            "type": InstitutionTypeWidget(attrs={'style': 'width:100%'}),
            "city": CityWidget(attrs={'style': 'width:100%'}),
            "religion": ReligionWidget(attrs={'style': 'width:100%'}),
            "secondary_literature": SecondaryLiteratureWidget(attrs={'style': 'width:100%'}),
            "evidence": EvidenceWidget(attrs={'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)
        self.fields['secondary_literature'].required = False
        self.fields['type'].empty_label = "Select institution type"
        self.fields['city'].empty_label = "Select city"
        self.fields['religion'].empty_label = "Select religion"
        self.fields['evidence'].empty_label = "Select evidence"
        self.fields['secondary_literature'].empty_label = "Select secondary literature"

    comment = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        widgets = {
            "religion": ReligionWidget,
            "secondary_literature": SecondaryLiteratureWidget,
            "evidence": EvidenceWidget,
        }

    comment = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['gender'].required = False
        self.fields['secondary_literature'].required = False
        self.fields['religion'].empty_label = "Select religion"
        self.fields['secondary_literature'].empty_label = "Select secondary literature"
        self.fields['gender'].empty_label = "Select gender"
        self.fields['evidence'].empty_label = "Select evidence"




class SecondaryLiteratureForm(ModelForm):
    class Meta:
        model = SecondaryLiterature
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SecondaryLiteratureForm, self).__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['journal'].required = False
        self.fields['publisher'].required = False
        self.fields['year'].required = False


class InstallationForm(ModelForm):
    watersystem = forms.ModelChoiceField(
        queryset=Watersystem.objects.all(),   # this line refreshes the list when new item is entered using plus button
        widget=WatersystemWidget(
            attrs={'data-placeholder': 'Select a water system',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    purpose = forms.ModelChoiceField(
        queryset=Purpose.objects.all(),
        widget=PurposeWidget(
            attrs={'data-placeholder': 'Select purposes',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select city',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    neighbourhood = forms.ModelChoiceField(
        queryset=Neighbourhood.objects.all(),
        widget=NeighbourhoodWidget(
            attrs={'data-placeholder': 'Select neighbourhood',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=LocationWidget(
            attrs={'data-placeholder': 'Select location',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    secondary_literature = forms.ModelChoiceField(
        queryset=SecondaryLiterature.objects.all(),
        widget=SecondaryLiteratureWidget(
            attrs={'data-placeholder': 'Select secondary literature',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    evidence = forms.ModelChoiceField(
        queryset=Evidence.objects.all(),
        widget=EvidenceWidget(
            attrs={'data-placeholder': 'Select evidence',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)

    class Meta:
        model = Installation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(InstallationForm, self).__init__(*args, **kwargs)
        self.fields['construction_date'].required = False
        self.fields['purpose'].required = False
        self.fields['city'].required = False
        self.fields['neighbourhood'].required = False
        self.fields['location'].required = False
        self.fields['secondary_literature'].required = False
        self.fields['evidence'].required = False
        self.fields['comment'].required = False

class EvidenceForm(ModelForm):
    class Meta:
        model = Evidence
        fields = ('title', 'author', 'date', 'secondary_literature', 'description')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'secondary_literature': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


# Relations form
class CityPersonRelationForm(ModelForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select city',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))

    class Meta:
        model = CityPersonRelation
        fields = ('city', 'person', 'type_of_involvement')
        # widget = {
        #     "city": CityWidget,
        # }


class NeighbourhoodPersonRelationForm(ModelForm):
    class Meta:
        model = NeighbourhoodPersonRelation
        fields = ('neighbourhood', 'person', 'type_of_involvement')


class PersonInstitutionRelationForm(ModelForm):
    class Meta:
        model = PersonInstitutionRelation
        fields = ('person', 'institution', 'type_of_involvement')


class PersonInstallationRelationForm(ModelForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=PersonWidget(
            attrs={'data-placeholder': 'Select a person',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    installation = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))

    class Meta:
        model = PersonInstallationRelation
        fields = ('person', 'installation', 'type_of_involvement')


class EvidencePersonRelationForm(ModelForm):
    class Meta:
        model = EvidencePersonRelation
        fields = ('evidence', 'person', 'page_number', 'description')

    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 1}),
        required=False)


class InstitutionInstallationRelationForm(ModelForm):
    installation = forms.ModelChoiceField(
        queryset=Installation.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select installation',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        widget=InstallationWidget(
            attrs={'data-placeholder': 'Select institution',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}))

    class Meta:
        model = InstitutionInstallationRelation
        fields = ('institution', 'installation', 'type_of_involvement')


# Formsets
personcity_formset = inlineformset_factory(
    Person, CityPersonRelation, form=CityPersonRelationForm, extra=1)

personneighbourhood_formset = inlineformset_factory(
    Person, NeighbourhoodPersonRelation, form=NeighbourhoodPersonRelationForm, extra=1)

personinstitution_formset = inlineformset_factory(
    Person, PersonInstitutionRelation, form=PersonInstitutionRelationForm, extra=1)

personinstallation_formset = inlineformset_factory(
    Person, PersonInstallationRelation, form=PersonInstallationRelationForm, extra=1)
installationperson_formset = inlineformset_factory(
    Installation, PersonInstallationRelation, form=PersonInstallationRelationForm, extra=1)

personevidence_formset = inlineformset_factory(
    Person, EvidencePersonRelation, form=EvidencePersonRelationForm, extra=1)

installationinstitution_formset = inlineformset_factory(
    Installation, InstitutionInstallationRelation, form=InstitutionInstallationRelationForm, extra=1)