from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import *
from .models import *
from django.views.generic import View, TemplateView, ListView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

# Extra Imports for the Login and Logout Capabilities
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from utilities.views import edit_model
from utilities.views import search, institutionsimplesearch, personsimplesearch 
from utilities.views import institutionadvancedsearch, installationadvancedsearch
from utilities.views import unaccent_installations, unaccent_institution 
from utilities.views import unaccent_person, unaccent_evidence, unaccent_watersystem
from utilities.views import dcopy_complete,unaccent_institutiontype

from django.db.models.functions import Lower
from .filters import *
import os

from .views_user import register, user_login, user_logout
from .views_map import MapVisualization, geojson_file

# Forms and lists
def Home(request):
    return render(request, 'installations/home.html')


@login_required
def CityCreate(request, id=0, view=None):
    if request.method == "GET":
        if id == 0:
            form = CityForm()
        else:
            city = City.objects.get(pk=id)
            form = CityForm(instance=city)
        return render(request, 'installations/city_form.html', {'form': form})
    else:  # request.method == "POST":
        if id == 0:
            form = CityForm(request.POST)
        else:
            city = City.objects.get(pk=id)
            form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
    if view == 'inline':
        return redirect('utilities:close')
    else:
        return redirect('installations:city-list')



def CityList(request):
    context = {'city_list': City.objects.all()}
    return render(request, 'installations/city_list.html', context)


@login_required
def CityDelete(request, id):
    city = get_object_or_404(City, pk=id)
    city.delete()
    return redirect('installations:city-list')


@login_required
def edit_institution(request, pk=None, focus='', view='complete'):
    names = 'institutioninstitution_formset,institutionperson_formset'
    names += ',institutioninstallation_formset,institutionevidence_formset'
    return edit_model(request, __name__, 'Institution', 'installations', pk, 
        formset_names=names,focus=focus, view=view)


def InstitutionList(request):
    query_set = institutionsimplesearch(request)
    query = request.GET.get("q", "")
    context = {'institution_list': query_set,
               'nentries': len(query_set),
               'query': query}
    return render(request, 'installations/institution_list.html', context)


def InstitutionAdvancedSearchList(request):
    query_set = institutionadvancedsearch(request)
    q_name = request.GET.get("q_name", "")
    q_type = request.GET.get("q_type", "")
    q_city = request.GET.get("q_city", "")
    q_startdate_l = request.GET.get("q_startdate_l", "")
    q_startdate_u = request.GET.get("q_startdate_u", "")
    q_firstreference_l = request.GET.get("q_firstreference_l", "")
    q_firstreference_u = request.GET.get("q_firstreference_u", "")
    q_enddate_l = request.GET.get("q_enddate_l", "")
    q_enddate_u = request.GET.get("q_enddate_u", "")
    q_comment = request.GET.get("q_comment", "")
    q_installation = request.GET.get("q_installation", "")
    q_person = request.GET.get("q_person", "")
    q_evidence = request.GET.get("q_evidence", "")
    order_by = request.GET.get("order_by", "id")
    context = {'institution_list': query_set.distinct(),
               'nentries': len(query_set),
               'query_name': q_name,
               'query_type': q_type,
               'query_city': q_city,
               'query_startdate_l': q_startdate_l,
               'query_startdate_u': q_startdate_u,
               'query_firstreference_l': q_firstreference_l,
               'query_firstreference_u': q_firstreference_u,
               'query_enddate_l': q_enddate_l,
               'query_enddate_u': q_enddate_u,
               'query_comment': q_comment,
               'query_installation': q_installation,
               'query_person': q_person,
               'query_evidence': q_evidence,
               'order_by': order_by
               }

    return render(request, 'installations/institution_advanced_search.html', context)


@login_required
def InstitutionDelete(request, id):
    institution = get_object_or_404(Institution, pk=id)
    institution.delete()
    return redirect('installations:institution-list')

@method_decorator(login_required, name='dispatch')
class InstitutionDetailView(DetailView):
    model = Institution

@login_required
def edit_person(request, pk=None, focus='', view='complete'):
    names = 'personperson_formset,personcity_formset,personneighbourhood_formset'
    names += ',personinstitution_formset,'
    names += 'personinstallation_formset,personevidence_formset'
    return edit_model(request, __name__, 'Person', 'installations', pk, 
        formset_names=names,focus=focus, view=view)

def PersonList(request):
    query_set = personsimplesearch(request)
    query = request.GET.get("q", "")
    context = {'person_list': query_set,
               'nentries': len(query_set),
               'query': query}
    return render(request, 'installations/person_list.html', context)


@login_required
def PersonDelete(request, id):
    person = get_object_or_404(Person, pk=id)
    person.delete()
    return redirect('installations:person-list')


@method_decorator(login_required, name='dispatch')
class PersonDetailView(DetailView):
    model = Person


@method_decorator(login_required, name='dispatch')
class SecondaryLiteratureListView(ListView):
    model = SecondaryLiterature
    template_name = 'installations/secondaryliterature_list.html'
    context_object_name = 'secondaryliteratures'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        else:
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super(SecondaryLiteratureListView, self).get_context_data(**kwargs)
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context


@method_decorator(login_required, name='dispatch')
class SecondaryLiteratureCreatView(CreateView):
    model = SecondaryLiterature
    fields = '__all__'
    template_name = 'installations/secondaryliterature_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:secondaryliterature-list')


@method_decorator(login_required, name='dispatch')
class SecondaryLiteratureUpdateView(UpdateView):
    model = SecondaryLiterature
    fields = '__all__'
    success_url = reverse_lazy('installations:secondaryliterature-list')


@method_decorator(login_required, name='dispatch')
class SecondaryLiteratureDeleteView(DeleteView):
    model = SecondaryLiterature
    success_url = reverse_lazy("installations:secondaryliterature-list")


@method_decorator(login_required, name='dispatch')
class SecondaryLiteratureDetailView(DetailView):
    model = SecondaryLiterature


@login_required
def edit_installation(request, pk=None, focus='', view='complete'):
    names = 'installationinstallation_formset,installationinstitution_formset'
    names += ',installationperson_formset,installationevidence_formset'
    return edit_model(request, __name__, 'Installation', 'installations', pk, 
        formset_names=names,focus=focus, view=view)

def InstallationList(request):
    query_set = search(request, 'installations', 'installation')
    query = request.GET.get("q", "")
    context = {'installation_list': query_set,
               'nentries': len(query_set),
               'query': query}
    return render(request, 'installations/installation_list.html', context)


# this method was working with Django-filter package which had some problems 
# with partial date which I omit it.
class InstallationListView(ListView):
    model = Installation
    template_name = "installations/installation_advanced_search.html"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        if direction == "descending":
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = InstallationFilter(self.request.GET, 
            queryset=self.get_queryset())
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context


def InstallationAdvancedSearchList(request):
    query_set = installationadvancedsearch(request)
    q_name = request.GET.get("q_name", "")
    q_watersystem = request.GET.get("q_watersystem", "")
    q_constructiondate_l = request.GET.get("q_constructiondate_l", "")
    q_constructiondate_u = request.GET.get("q_constructiondate_u", "")
    q_firstreference_l = request.GET.get("q_firstreference_l", "")
    q_firstreference_u = request.GET.get("q_firstreference_u", "")
    q_enddate_l = request.GET.get("q_enddate_l", "")
    q_enddate_u = request.GET.get("q_enddate_u", "")
    q_city = request.GET.get("q_city", "")
    q_neighbourhoodno = request.GET.get("q_neighbourhoodno", "")
    q_institutionaslocation = request.GET.get("q_institutionaslocation", "")
    q_comment = request.GET.get("q_comment", "")
    q_institution = request.GET.get("q_institution", "")
    q_person = request.GET.get("q_person", "")
    q_evidence = request.GET.get("q_evidence", "")
    order_by = request.GET.get("order_by", "id")

    context = {'installation_list': query_set.distinct(),
               'nentries': len(query_set),
               'query_name': q_name,
               'query_watersystem': q_watersystem,
               'query_constructiondate_l': q_constructiondate_l,
               'query_constructiondate_u': q_constructiondate_u,
               'query_firstreference_l': q_firstreference_l,
               'query_firstreference_u': q_firstreference_u,
               'query_enddate_l': q_enddate_l,
               'query_enddate_u': q_enddate_u,
               'query_city': q_city,
               'query_neighbourhoodno': q_neighbourhoodno,
               'query_institutionaslocation': q_institutionaslocation,
               'query_comment': q_comment,
               'query_institution': q_institution,
               'query_person': q_person,
               'query_evidence': q_evidence,
               'order_by': order_by
               }

    return render(request, 'installations/installation_advanced_search.html', context)


@login_required
def InstallationDelete(request, id):
    installation = get_object_or_404(Installation, pk=id)
    installation.delete()
    return redirect('installations:installation-list')


@method_decorator(login_required, name='dispatch')
class InstallationDetailView(DetailView):
    model = Installation


def InstallationDuplicate(request, id):
    instance = get_object_or_404(Installation, pk=id)
    dcopy = dcopy_complete(instance)
    dcopy.save()
    return redirect('installations:installation-list')


# Using Class based View

@method_decorator(login_required, name='dispatch')
class EvidenceListView(ListView):
    model = Evidence
    template_name = 'installations/evidence_list'
    context_object_name = 'evidences'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        else:
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super(EvidenceListView, self).get_context_data(**kwargs)
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context


@login_required
def edit_evidence(request, pk=None, focus='', view='complete'):
    names = ''
    return edit_model(request, __name__, 'Evidence', 'installations', pk, 
        formset_names=names,focus=focus, view=view)

@method_decorator(login_required, name='dispatch')
class EvidenceDeleteView(DeleteView):
    model = Evidence
    success_url = reverse_lazy("installations:evidence-list")

@method_decorator(login_required, name='dispatch')
class EvidenceDetailView(DetailView):
    model = Evidence

@login_required
def edit_figure(request, pk=None, focus='', view='complete'):
    names = ''
    return edit_model(request, __name__, 'Figure', 'installations', pk, 
        formset_names=names,focus=focus, view=view)

@method_decorator(login_required, name='dispatch')
class WaterSystemListView(ListView):
    model = Watersystem
    template_name = 'installations/watersystem_list.html'
    context_object_name = 'watersystems'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        else:
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super(WaterSystemListView, self).get_context_data(**kwargs)
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context

@method_decorator(login_required, name='dispatch')
class WaterSystemCreatView(CreateView):
    model = Watersystem
    form_class = WatersystemForm
    template_name = 'installations/watersystem_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:watersystem-list')


@method_decorator(login_required, name='dispatch')
class WaterSystemUpdateView(UpdateView):
    model = Watersystem
    form_class = WatersystemForm
    success_url = reverse_lazy('installations:watersystem-list')


@method_decorator(login_required, name='dispatch')
class WaterSystemDeleteView(DeleteView):
    model = Watersystem
    success_url = reverse_lazy("installations:watersystem-list")


@method_decorator(login_required, name='dispatch')
class WaterSystemCategoriesListView(ListView):
    model = WatersystemCategories
    template_name = 'installations/watersystemcategories_list.html'
    context_object_name = 'watersystemcategories'


@method_decorator(login_required, name='dispatch')
class WaterSystemCategoriesCreatView(CreateView):
    model = WatersystemCategories
    form_class = WatersystemCategoriesForm
    template_name = 'installations/watersystemcategories_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:watersystemcategories-list')


@method_decorator(login_required, name='dispatch')
class WaterSystemCategoriesUpdateView(UpdateView):
    model = WatersystemCategories
    form_class = WatersystemCategoriesForm
    success_url = reverse_lazy('installations:watersystemcategories-list')


@method_decorator(login_required, name='dispatch')
class WaterSystemCategoriesDeleteView(DeleteView):
    model = WatersystemCategories
    success_url = reverse_lazy("installations:watersystemcategories-list")


@method_decorator(login_required, name='dispatch')
class PurposeListView(ListView):
    model = Purpose
    template_name = 'installations/purpose_list.html'
    context_object_name = 'purposes'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        else:
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super(PurposeListView, self).get_context_data(**kwargs)
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context


@method_decorator(login_required, name='dispatch')
class PurposeCreatView(CreateView):
    model = Purpose
    fields = '__all__'
    template_name = 'installations/purpose_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:purpose-list')


@method_decorator(login_required, name='dispatch')
class PurposeUpdateView(UpdateView):
    model = Purpose
    fields = '__all__'
    success_url = reverse_lazy('installations:purpose-list')


@method_decorator(login_required, name='dispatch')
class PurposeDeleteView(DeleteView):
    model = Purpose
    success_url = reverse_lazy("installations:purpose-list")


@method_decorator(login_required, name='dispatch')
class InstitutionTypeListView(ListView):
    model = InstitutionType
    template_name = 'installations/institutiontype_list.html'
    context_object_name = 'institutiontypes'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        else:
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super(InstitutionTypeListView, self).get_context_data(**kwargs)
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context


@method_decorator(login_required, name='dispatch')
class InstitutionTypeCreatView(CreateView):
    model = InstitutionType
    fields = ('name', 'description')
    template_name = 'installations/institutiontype_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:institutiontype-list')


@method_decorator(login_required, name='dispatch')
class InstitutionTypeUpdateView(UpdateView):
    model = InstitutionType
    fields = '__all__'
    success_url = reverse_lazy('installations:institutiontype-list')


@method_decorator(login_required, name='dispatch')
class InstitutionTypeDeleteView(DeleteView):
    model = InstitutionType
    success_url = reverse_lazy("installations:institutiontype-list")


@method_decorator(login_required, name='dispatch')
class ReligionListView(ListView):
    model = Religion
    template_name = 'installations/religion_list.html'
    context_object_name = 'religions'


@method_decorator(login_required, name='dispatch')
class ReligionCreatView(CreateView):
    model = Religion
    fields = '__all__'
    template_name = 'installations/religion_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:religion-list')


@method_decorator(login_required, name='dispatch')
class ReligionUpdateView(UpdateView):
    model = Religion
    fields = '__all__'
    success_url = reverse_lazy('installations:religion-list')


@method_decorator(login_required, name='dispatch')
class ReligionDeleteView(DeleteView):
    model = Religion
    success_url = reverse_lazy("installations:religion-list")


@method_decorator(login_required, name='dispatch')
class NeighbourhoodCreatView(CreateView):
    model = Neighbourhood
    form_class = NeighbourhoodForms
    template_name = 'installations/neighbourhood_form.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:neighbourhood-list')  


@method_decorator(login_required, name='dispatch')
class NeighbourhoodListView(ListView):
    model = Neighbourhood
    template_name = 'installations/neighbourhood_list.html'
    context_object_name = 'neighbourhoods'

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        order_by = self.request.GET.get("order_by", "id")
        direction = self.request.GET.get("direction", "ascending")
        if direction == "ascending":
            query_set = self.model.objects.all().order_by(Lower(order_by))
        else:
            query_set = self.model.objects.all().order_by(Lower(order_by)).reverse()
        return query_set

    def get_context_data(self, **kwargs):
        context = super(NeighbourhoodListView, self).get_context_data(**kwargs)
        context["order_by"] = self.request.GET.get("order_by", "id")
        context["direction"] = self.request.GET.get("direction", "ascending")
        return context


@method_decorator(login_required, name='dispatch')
class NeighbourhoodUpdateView(UpdateView):
    model = Neighbourhood
    fields = '__all__'
    success_url = reverse_lazy('installations:neighbourhood-list')


@method_decorator(login_required, name='dispatch')
class NeighbourhoodDeleteView(DeleteView):
    model = Neighbourhood
    success_url = reverse_lazy("installations:neighbourhood-list")


# Relations
# -------------------------------------------
# CityPersonRelation
@method_decorator(login_required, name='dispatch')
class CityPersonRelationListView(ListView):
    model = CityPersonRelation
    template_name = 'installations/citypersonrelation_list.html'
    context_object_name = 'citypersonrelations'


@method_decorator(login_required, name='dispatch')
class CityPersonRelationCreatView(CreateView):
    model = CityPersonRelation
    fields = '__all__'
    template_name = 'installations/citypersonrelation_form.html'
    success_url = reverse_lazy('installations:citypersonrelation-list')


@method_decorator(login_required, name='dispatch')
class CityPersonRelationUpdateView(UpdateView):
    model = CityPersonRelation
    fields = '__all__'
    success_url = reverse_lazy('installations:citypersonrelation-list')


@method_decorator(login_required, name='dispatch')
class CityPersonRelationDeleteView(DeleteView):
    model = CityPersonRelation
    success_url = reverse_lazy("installations:citypersonrelation-list")


# PersonInstitutionRelation
@method_decorator(login_required, name='dispatch')
class PersonInstitutionRelationListView(ListView):
    model = PersonInstitutionRelation
    template_name = 'installations/personinstitutionrelation_list.html'
    context_object_name = 'personinstitutionrelations'


@method_decorator(login_required, name='dispatch')
class PersonInstitutionRelationCreatView(CreateView):
    model = PersonInstitutionRelation
    fields = '__all__'
    template_name = 'installations/personinstitutionrelation_form.html'
    success_url = reverse_lazy('installations:personinstitutionrelation-list')


@method_decorator(login_required, name='dispatch')
class PersonInstitutionRelationUpdateView(UpdateView):
    model = PersonInstitutionRelation
    fields = '__all__'
    success_url = reverse_lazy('installations:personinstitutionrelation-list')


@method_decorator(login_required, name='dispatch')
class PersonInstitutionRelationDeleteView(DeleteView):
    model = PersonInstitutionRelation
    success_url = reverse_lazy("installations:personinstitutionrelation-list")


# PersonInstallationRelation
@method_decorator(login_required, name='dispatch')
class PersonInstallationRelationListView(ListView):
    model = PersonInstallationRelation
    template_name = 'installations/personinstallationrelation_list.html'
    context_object_name = 'personinstallationrelations'


@method_decorator(login_required, name='dispatch')
class PersonInstallationRelationCreatView(CreateView):
    model = PersonInstallationRelation
    fields = '__all__'
    template_name = 'installations/personinstallationrelation_form.html'
    success_url = reverse_lazy('installations:personinstallationrelation-list')


@method_decorator(login_required, name='dispatch')
class PersonInstallationRelationUpdateView(UpdateView):
    model = PersonInstallationRelation
    fields = '__all__'
    success_url = reverse_lazy('installations:personinstallationrelation-list')


@method_decorator(login_required, name='dispatch')
class PersonInstallationRelationDeleteView(DeleteView):
    model = PersonInstallationRelation
    success_url = reverse_lazy("installations:personinstallationrelation-list")


# CityInistallationRelation
@method_decorator(login_required, name='dispatch')
class CityInstallationRelationListView(ListView):
    model = CityInstallationRelation
    template_name = 'installations/cityinstallationrelation_list.html'
    context_object_name = 'cityinstallationrelations'


@method_decorator(login_required, name='dispatch')
class CityInstallationRelationCreatView(CreateView):
    model = CityInstallationRelation
    fields = '__all__'
    template_name = 'installations/cityinstallationrelation_form.html'
    success_url = reverse_lazy('installations:cityinstallationrelation-list')


@method_decorator(login_required, name='dispatch')
class CityInstallationRelationUpdateView(UpdateView):
    model = CityInstallationRelation
    fields = '__all__'
    success_url = reverse_lazy('installations:cityinstallationrelation-list')


@method_decorator(login_required, name='dispatch')
class CityInstallationRelationDeleteView(DeleteView):
    model = CityInstallationRelation
    success_url = reverse_lazy("installations:cityinstallationrelation-list")


# Accessory page View
@login_required(login_url='/admin/')
def Accessory(request):
    action = request.GET.get("unaccent_action", "")
    if action == "un_installation":
        unaccent_installations(request, 'installations', 'installation')
    print(action)

    if action == "un_institution":
        unaccent_institution(request, 'installations', 'institution')

    if action == "un_person":
        unaccent_person(request, 'installations', 'person')

    if action == "un_evidence":
        unaccent_evidence(request, 'installations', 'evidence')

    if action == "un_watersystem":
        unaccent_watersystem(request, 'installations', 'watersystem')

    if action == "un_institutiontype":
        unaccent_institutiontype(request, 'installations', 'institutiontype')

    return render(request, 'installations/accessory.html')


@method_decorator(login_required, name='dispatch')
class FigureListView(ListView):
    model = Figure
    template_name = 'installations/figure_list.html'
    context_object_name = 'figures'


@method_decorator(login_required, name='dispatch')
class FigureCreatView(CreateView):
    model = Figure
    fields = '__all__'
    template_name = 'installations/add_figure_old.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:figure-list')


@method_decorator(login_required, name='dispatch')
class FigureUpdateView(UpdateView):
    model = Figure
    fields = '__all__'
    template_name = 'installations/add_figure_old.html'
    success_url = reverse_lazy('installations:figure-list')


@method_decorator(login_required, name='dispatch')
class FigureDeleteView(DeleteView):
    model = Figure
    success_url = reverse_lazy("installations:figure-list")


@method_decorator(login_required, name='dispatch')
class StyleListView(ListView):
    model = Style
    template_name = 'installations/style_list.html'
    context_object_name = 'styles'


@method_decorator(login_required, name='dispatch')
class StyleCreatView(CreateView):
    model = Style
    fields = '__all__'
    template_name = 'installations/add_style.html'

    def get_success_url(self):
        if 'view' in self.kwargs:
            viewmode = self.kwargs['view']
            if viewmode == 'inline':
                return reverse_lazy('utilities:close')
        else:
            return reverse_lazy('installations:style-list')


@method_decorator(login_required, name='dispatch')
class StyleUpdateView(UpdateView):
    model = Style
    fields = '__all__'
    template_name = 'installations/add_style.html'
    success_url = reverse_lazy('installations:style-list')


@method_decorator(login_required, name='dispatch')
class StyleDeleteView(DeleteView):
    model = Style
    success_url = reverse_lazy("installations:style-list")
