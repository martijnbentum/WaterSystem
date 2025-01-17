from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from utils import view_util
from utils.model_util import instance2names, instance2name
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from .models import copy_complete
from utilities.search import Search
from django.db.models import CharField, ForeignKey
from partial_date import PartialDateField
from django.db.models import Q
import unidecode


def list_view(request, model_name, app_name):
    '''list view of a model.'''
    s = Search(request, model_name, app_name)
    instances = s.filter()
    if model_name == 'UserLoc': model_name = 'location'
    var = {model_name.lower() + '_list': instances, 'page_name': model_name,
           'order': s.order.order_by, 'direction': s.order.direction,
           'query': s.query.query, 'nentries': s.nentries}
    print(s.notes, 000)
    return render(request, app_name + '/' + model_name.lower() + '_list.html', var)


# @permission_required('utilities.add_generic')
def edit_model(request, name_space, model_name, app_name, instance_id=None,
               formset_names='', focus='', view='complete'):
    '''edit view generalized over models.
    assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
    and {{model_name}}Form
    '''
    names = formset_names
    model = apps.get_model(app_name, model_name)
    modelform = view_util.get_modelform(name_space, model_name + 'Form')
    instance = model.objects.get(pk=instance_id) if instance_id else None
    crud = Crud(instance) if instance else None
    ffm, form = None, None
    if request.method == 'POST':
        focus, button = getfocus(request), getbutton(request)
        if button in 'delete,cancel,confirm_delete':
            return delete_model(request, name_space, model_name, 
                app_name, instance_id)
        if button == 'saveas' and instance: instance = copy_complete(instance)
        form = modelform(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            print('form is valid: ', form.cleaned_data, type(form))

            instance = form.save()
            if view == 'complete':
                ffm = FormsetFactoryManager(name_space, names, request, instance)
                valid = ffm.save()
                if valid:
                    show_messages(request, button, model_name)
                    if button == 'add_another':
                        url = app_name + ':' + model_name.lower() + '-insert'
                        return HttpResponseRedirect(reverse(url))
                    if focus == '':
                        focus = 'Edit'
                    return HttpResponseRedirect(reverse(
                        app_name + ':' + model_name.lower() + '-update',
                        kwargs={'pk': instance.pk, 'focus': focus}))
                else:
                    print('ERROR', ffm.errors)
            else:
                return HttpResponseRedirect('/utilities/close/')
    if not form: form = modelform(instance=instance)
    if not ffm: ffm = FormsetFactoryManager(name_space, names, instance=instance)
    tabs = make_tabs(model_name.lower(), focus_names=focus)
    name = model_name.lower()
    page_name = 'Edit ' + name if instance_id else 'Add ' + name
    args = {'form': form, 'page_name': page_name, 'crud': crud,
            'tabs': tabs, 'view': view}
    args.update(ffm.dict)
    return render(request, app_name + '/add_' + model_name.lower() + '.html', args)


# @permission_required('utilities.add_generic')
def add_simple_model(request, name_space, model_name, app_name, page_name):
    '''Function to add simple models with only a form could be extended.
    request     django object
    name_space  the name space of the module calling this function 
                (to load forms / models)
    model_name  name of the model
    app_name    name of the app
    page_name   name of the page
    The form name should be of format <model_name>Form
    '''
    modelform = view_util.get_modelform(name_space, model_name + 'Form')
    form = modelform(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, model_name + ' saved')
            return HttpResponseRedirect('/utilities/close/')
    model = apps.get_model(app_name, model_name)
    instances = model.objects.all().order_by('name')
    var = {'form': form, 'page_name': page_name, 'instances': instances}
    return render(request, 'utilities/add_simple_model.html', var)


# @permission_required('utilities.delete_generic')
def delete_model(request, name_space, model_name, app_name, pk):
    model = apps.get_model(app_name, model_name)
    instance = get_object_or_404(model, id=pk)
    focus, button = getfocus(request), getbutton(request)
    print(request.POST.keys())
    print(99, instance.view(), instance, 888)
    print(button)
    if request.method == 'POST':
        if button == 'cancel':
            show_messages(request, button, model_name)
            return HttpResponseRedirect(reverse(
                app_name + ':' + model_name.lower() + '-update',
                kwargs={'pk': instance.pk, 'focus': focus}))
        if button == 'confirm_delete':
            instance.delete()
            show_messages(request, button, model_name)
            return HttpResponseRedirect('/' + app_name + '/' + model_name.lower())
    info = instance.info
    print(1, info, instance, pk)
    var = {'info': info, 'page_name': 'Delete ' + model_name.lower()}
    print(2)
    return render(request, 'utilities/delete_model.html', var)


def getfocus(request):
    '''extracts focus variable from the request object to correctly 
    set the active tabs.
    '''
    if 'focus' in request.POST.keys():
        return request.POST['focus']
    else:
        return 'default'


# Create your views here.
def getbutton(request):
    if 'save' in request.POST.keys():
        return request.POST['save']
    else:
        return 'default'


def show_messages(request, button, model_name):
    '''provide user feedback on submitting a form.'''
    if button == 'saveas':
        m = 'saved a copy of ' + model_name 
        m += '. Use "save" button to store edits to this copy'
        messages.warning(request,m)
                         
    elif button == 'confirm_delete':
        messages.success(request, model_name + ' deleted')
    elif button == 'cancel':
        messages.warning(request, 'delete aborted')
    else:
        messages.success(request, model_name + ' saved')


def close(request):
    '''page that closes itself for on the fly creation of 
    model instances (loaded in a new tab).
    '''
    return render(request, 'utilities/close.html')


# simple search methods
def search(request, app_name, model_name):
    '''Search function between all fields in a model.
    app_name : application name
    model_name : model name for search
    '''
    model = apps.get_model(app_name, model_name)
    query = request.GET.get("q", "")
    order_by = request.GET.get("order_by", "id")
    query_set = model.objects.all().order_by(order_by)
    queries = query.split()
    if query is not None:
        query_setall = model.objects.none()
        for qs in queries:
            query_seti = query_set.filter(
                Q(name__icontains=qs) |
                Q(un_name__icontains=qs) |
                Q(watersystem__original_term__icontains=qs) |
                Q(watersystem__un_original_term__icontains=qs) |
                Q(construction_date_lower__icontains=qs) |
                Q(construction_date_upper__icontains=qs) |
                Q(first_reference_lower__icontains=qs) |
                Q(first_reference_upper__icontains=qs) |
                Q(end_functioning_year_lower__icontains=qs) |
                Q(end_functioning_year_upper__icontains=qs) |
                Q(city__name__icontains=qs) |
                Q(purpose__name__icontains=qs) |
                Q(neighbourhood__neighbourhood_number__icontains=qs) |
                Q(latitude__icontains=qs) |
                Q(longitude__icontains=qs) |
                Q(institution_as_location__name__icontains=qs) |
                Q(secondary_literature__title__icontains=qs) |
                Q(secondary_literature__author__icontains=qs) |
                Q(comment__icontains=qs) |
                Q(un_comment__icontains=qs)

            )
            query_setall = query_setall | query_seti
        query_set = query_setall.order_by(order_by)
    if query == "":
        query_set = model.objects.all().order_by(order_by)

    return query_set.distinct()


def institutionsimplesearch(request):
    '''
    Simple search function between specified fields in the institution model.
    Simple search return the OR result between the search result for each field
    '''
    model = apps.get_model('installations', 'institution')  # app_name, model_name
    query = request.GET.get("q", "")
    order_by = request.GET.get("order_by", "id")
    query_set = model.objects.all().order_by(order_by)

    queries = query.split()
    if query is not None:
        query_setall = model.objects.none()
        for qs in queries:
            query_seti = query_set.filter(
                Q(name__icontains=qs) |
                Q(un_name__icontains=qs) |
                Q(type_many__name__icontains=qs) |
                Q(type_many__un_name__icontains=qs) |
                Q(purpose__name__icontains=qs) |
                Q(city__name__icontains=qs) |
                Q(neighbourhood__neighbourhood_number__icontains=qs) |
                Q(latitude__icontains=qs) |
                Q(longitude__icontains=qs) |
                Q(start_date_lower__icontains=qs) |
                Q(start_date_upper__icontains=qs) |
                Q(first_reference_lower__icontains=qs) |
                Q(first_reference_upper__icontains=qs) |
                Q(end_date_lower__icontains=qs) |
                Q(end_date_upper__icontains=qs) |
                Q(religion__name__icontains=qs) |
                Q(secondary_literature__title__icontains=qs) |
                Q(secondary_literature__author__icontains=qs) |
                Q(comment__icontains=qs) |
                Q(un_comment__icontains=qs)

            )
            query_setall = query_setall | query_seti
        query_set = query_setall.order_by(order_by)
    if query == "":
        query_set = model.objects.all().order_by(order_by)

    return query_set


def personsimplesearch(request):
    '''
    Simple search function between specified fields in the person model.
    Simple search return the OR result between the search result for each field
    '''
    model = apps.get_model('installations', 'person')  # app_name, model_name
    query = request.GET.get("q", "")
    order_by = request.GET.get("order_by", "id")
    query_set = model.objects.all().order_by(order_by)

    queries = query.split()
    if query is not None:
        query_setall = model.objects.none()
        for qs in queries:
            query_seti = query_set.filter(
                Q(name__icontains=qs) |
                Q(un_name__icontains=qs) |
                Q(role__icontains=qs) |
                Q(un_role__icontains=qs) |
                Q(religion__name__icontains=qs) |
                Q(secondary_literature__title__icontains=qs) |
                Q(secondary_literature__author__icontains=qs) |
                Q(comment__icontains=qs) |
                Q(un_comment__icontains=qs)
            )
            query_setall = query_setall | query_seti
        query_set = query_setall.order_by(order_by)
    if query == "":
        query_set = model.objects.all().order_by(order_by)

    return query_set

# Advanced search methods
def institutionadvancedsearch(request):
    '''
    Advanced search function between specified fields in the institution model.
    Advanced search return the AND result between the search result for each field
    '''
    model = apps.get_model('installations', 'institution')  # app_name, model_name
    query_name = request.GET.get("q_name", "")
    query_type = request.GET.get("q_type", "")
    query_city = request.GET.get("q_city", "")
    query_startdate_l = request.GET.get("q_startdate_l", "")
    query_startdate_u = request.GET.get("q_startdate_u", "")
    query_firstreference_l = request.GET.get("q_firstreference_l", "")
    query_firstreference_u = request.GET.get("q_firstreference_u", "")
    query_enddate_l = request.GET.get("q_enddate_l", "")
    query_enddate_u = request.GET.get("q_enddate_u", "")
    query_comment = request.GET.get("q_comment", "")
    query_installation = request.GET.get("q_installation", "")
    query_person = request.GET.get("q_person", "")
    query_evidence = request.GET.get("q_evidence", "")
    order_by = request.GET.get("order_by", "id")
    query_set = model.objects.all()

    if query_name:
        query_set = query_set.filter(Q(un_name__icontains=query_name) | Q(name__icontains=query_name))

    if query_type:
        query_set = query_set.filter(
            Q(type_many__name__icontains=query_type) | Q(type_many__un_name__icontains=query_type))

    if query_city:
        query_set = query_set.filter(city__name__icontains=query_city)

    if query_startdate_l:
        query_set = query_set.filter(
            Q(start_date_lower__gte=query_startdate_l) | Q(start_date_upper__gte=query_startdate_l))

    if query_startdate_u:
        query_set = query_set.filter(
            Q(start_date_lower__lte=query_startdate_u) | Q(start_date_upper__lte=query_startdate_u))

    if query_firstreference_l:
        query_set = query_set.filter(
            Q(first_reference_lower__gte=query_firstreference_l) | Q(first_reference_upper__gte=query_firstreference_l))

    if query_firstreference_u:
        query_set = query_set.filter(
            Q(first_reference_lower__lte=query_firstreference_u) | Q(first_reference_upper__lte=query_firstreference_u))

    if query_enddate_l:
        query_set = query_set.filter(
            Q(end_date_lower__gte=query_enddate_l) | Q(end_date_upper__gte=query_enddate_l))

    if query_enddate_u:
        query_set = query_set.filter(
            Q(end_date_lower__lte=query_enddate_u) | Q(end_date_upper__lte=query_enddate_u))

    if query_comment:
        query_set = query_set.filter(Q(un_comment__icontains=query_comment) | Q(comment__icontains=query_comment))

    if query_installation:
        query_set = query_set.filter(
            Q(institutioninstallationrelation__installation__name__icontains=query_installation) |
            Q(institutioninstallationrelation__installation__un_name__icontains=query_installation) |
            Q(institutioninstallationrelation__type_of_involvement__icontains=query_installation) |
            Q(institutioninstallationrelation__installation__watersystem__original_term__icontains=query_installation) |
            Q(institutioninstallationrelation__installation__watersystem__type__icontains=query_installation))

    if query_person:
        query_set = query_set.filter(Q(personinstitutionrelation__person__name__icontains=query_person) |
                                     Q(personinstitutionrelation__person__un_name__icontains=query_person) |
                                     Q(personinstitutionrelation__person__role__icontains=query_person) |
                                     Q(personinstitutionrelation__person__un_role__icontains=query_person) |
                                     Q(personinstitutionrelation__type_of_involvement__icontains=query_person))

    if query_evidence:
        query_set = query_set.filter(Q(evidenceinstitutionrelation__evidence__title__icontains=query_evidence) |
                                     Q(evidenceinstitutionrelation__evidence__un_title__icontains=query_evidence) |
                                     Q(evidenceinstitutionrelation__evidence__author__icontains=query_evidence) |
                                     Q(evidenceinstitutionrelation__evidence__un_author__icontains=query_evidence))

    return query_set.order_by(order_by).distinct()


def installationadvancedsearch(request):
    '''
        Advanced search function between specified fields in the installation model.
        Advanced search return the AND result between the search result for each field
        '''
    model = apps.get_model('installations', 'installation')  # app_name, model_name
    query_name = request.GET.get("q_name", "")
    query_watersystem = request.GET.get("q_watersystem", "")
    query_constructiondate_l = request.GET.get("q_constructiondate_l", "")
    query_constructiondate_u = request.GET.get("q_constructiondate_u", "")
    query_firstreference_l = request.GET.get("q_firstreference_l", "")
    query_firstreference_u = request.GET.get("q_firstreference_u", "")
    query_enddate_l = request.GET.get("q_enddate_l", "")
    query_enddate_u = request.GET.get("q_enddate_u", "")
    query_city = request.GET.get("q_city", "")
    query_neighbourhoodno = request.GET.get("q_neighbourhoodno", "")
    query_institutionaslocation = request.GET.get("q_institutionaslocation", "")
    query_comment = request.GET.get("q_comment", "")
    query_institution = request.GET.get("q_institution", "")
    query_person = request.GET.get("q_person", "")
    query_evidence = request.GET.get("q_evidence", "")
    order_by = request.GET.get("order_by", "id")
    query_set = model.objects.all()

    if query_name:
        query_set = query_set.filter(Q(un_name__icontains=query_name) | Q(name__icontains=query_name))

    if query_watersystem:
        query_set = query_set.filter(Q(watersystem__original_term__icontains=query_watersystem) |
                                     Q(watersystem__un_original_term__icontains=query_watersystem) |
                                     Q(watersystem__type__icontains=query_watersystem))

    if query_constructiondate_l:
        query_set = query_set.filter(
            Q(construction_date_lower__gte=query_constructiondate_l) | Q(
                construction_date_upper__gte=query_constructiondate_l))

    if query_constructiondate_u:
        query_set = query_set.filter(
            Q(construction_date_lower__lte=query_constructiondate_u) | Q(
                construction_date_upper__lte=query_constructiondate_u))

    if query_firstreference_l:
        query_set = query_set.filter(
            Q(first_reference_lower__gte=query_firstreference_l) | Q(first_reference_upper__gte=query_firstreference_l))

    if query_firstreference_u:
        query_set = query_set.filter(
            Q(first_reference_lower__lte=query_firstreference_u) | Q(first_reference_upper__lte=query_firstreference_u))

    if query_enddate_l:
        query_set = query_set.filter(
            Q(end_functioning_year_lower__gte=query_enddate_l) | Q(end_functioning_year_upper__gte=query_enddate_l))

    if query_enddate_u:
        query_set = query_set.filter(
            Q(end_functioning_year_lower__lte=query_enddate_u) | Q(end_functioning_year_upper__lte=query_enddate_u))

    if query_city:
        query_set = query_set.filter(city__name__icontains=query_city)

    if query_neighbourhoodno:
        query_set = query_set.filter(neighbourhood__neighbourhood_number__icontains=query_neighbourhoodno)

    if query_institutionaslocation:
        query_set = query_set.filter(Q(institution_as_location__name__icontains=query_institutionaslocation) |
                                     Q(institution_as_location__un_name__icontains=query_institutionaslocation) |
                                     Q(
                                         institution_as_location__type_many__name__icontains=query_institutionaslocation) |
                                     Q(
                                         institution_as_location__type_many__un_name__icontains=query_institutionaslocation) |
                                     Q(institution_as_location__purpose__name__icontains=query_institutionaslocation))

    if query_comment:
        query_set = query_set.filter(Q(un_comment__icontains=query_comment) | Q(comment__icontains=query_comment))

    if query_institution:
        query_set = query_set.filter(
            Q(institutioninstallationrelation__institution__name__icontains=query_institution) |
            Q(institutioninstallationrelation__institution__un_name__icontains=query_institution) |
            Q(institutioninstallationrelation__type_of_involvement__icontains=query_institution) |
            Q(institutioninstallationrelation__institution__type_many__name__icontains=query_institution) |
            Q(institutioninstallationrelation__institution__type_many__un_name__icontains=query_institution))

    if query_person:
        query_set = query_set.filter(Q(personinstallationrelation__person__name__icontains=query_person) |
                                     Q(personinstallationrelation__person__un_name__icontains=query_person) |
                                     Q(personinstallationrelation__person__role__icontains=query_person) |
                                     Q(personinstallationrelation__person__un_role__icontains=query_person) |
                                     Q(personinstallationrelation__type_of_involvement__icontains=query_person))

    if query_evidence:
        query_set = query_set.filter(Q(evidenceinstallationrelation__evidence__title__icontains=query_evidence) |
                                     Q(evidenceinstallationrelation__evidence__un_title__icontains=query_evidence) |
                                     Q(evidenceinstallationrelation__evidence__author__icontains=query_evidence) |
                                     Q(evidenceinstallationrelation__evidence__un_author__icontains=query_evidence))

    return query_set.order_by(order_by).distinct()


# methods for unaccent the fields for search
def unaccent_installations(request, app_name, model_name):
    """"This method copies unaccented version of the data to a new un_<field name> which will used for search without
    diacritics. For instance, if field <name> has a 
    diacritics then <un_name> field won't.
    Search fields for installation are:
    - name --> un_name
    - comment --> un_comment

    """
    model = apps.get_model(app_name, model_name)
    query_set = model.objects.all()
    for query in query_set:
        if query.name is not None:
            query.un_name = unidecode.unidecode(query.name)
            query.save()
        if query.comment is not None:
            query.un_comment = unidecode.unidecode(query.comment)
            query.save()


def unaccent_institution(request, app_name, model_name):
    """"This method copies unaccented version of the data to a 
        new un_<field name> which will used for search without
        diacritics. For instance, if field <name> has a diacritics 
        then <un_name> field won't.
        Search fields for institution are:
        - name --> un_name
        - comment --> un_comment

        """
    model = apps.get_model(app_name, model_name)
    query_set = model.objects.all()
    for query in query_set:
        if query.name is not None:
            query.un_name = unidecode.unidecode(query.name)
            query.save()
        if query.comment is not None:
            query.un_comment = unidecode.unidecode(query.comment)
            query.save()


def unaccent_person(request, app_name, model_name):
    """"This method copies unaccented version of the data to a new 
        un_<field name> which will used for search without
        diacritics. For instance, if field <name> has a diacritics 
        then <un_name> field won't.
        Search fields for person are:
        - name --> un_name
        - role --> un_role
        - comment --> un_comment

        """
    model = apps.get_model(app_name, model_name)
    query_set = model.objects.all()
    for query in query_set:
        if query.name is not None:
            query.un_name = unidecode.unidecode(query.name)
            query.save()
        if query.role is not None:
            query.un_role = unidecode.unidecode(query.role)
            query.save()
        if query.comment is not None:
            query.un_comment = unidecode.unidecode(query.comment)
            query.save()


def unaccent_evidence(request, app_name, model_name):
    '''This method copies unaccented version of the data to a new 
        un_<field name> which will used for search without
        diacritics. For instance, if field <name> has a diacritics 
        then <un_name> field won't.
        Search fields for evidence are:
        - title --> un_title
        - author --> un_author
        - description --> un_description
    ''' 
    model = apps.get_model(app_name, model_name)
    query_set = model.objects.all()
    for query in query_set:
        if query.title is not None:
            query.un_title = unidecode.unidecode(query.title)
            query.save()
        if query.author is not None:
            query.un_author = unidecode.unidecode(query.author)
            query.save()
        if query.description is not None:
            query.un_description = unidecode.unidecode(query.description)
            query.save()


def unaccent_watersystem(request, app_name, model_name):
    '''This method copies unaccented version of the data to a new 
        un_<field name> which will used for search without
        diacritics. For instance, if field <name> has a diacritics 
        then <un_name> field won't.
        Search fields for water system are:
        - original_term --> un_original_term
    '''

    model = apps.get_model(app_name, model_name)
    query_set = model.objects.all()
    for query in query_set:
        if query.original_term is not None:
            query.un_original_term = unidecode.unidecode(query.original_term)
            query.save()


def unaccent_institutiontype(request, app_name, model_name):
    '''This method copies unaccented version of the data to a 
        new un_<field name> which will used for search without
        diacritics. For instance, if field <name> has a 
        diacritics then <un_name> field won't.
        Search fields for institution type are:
        - name --> un_name
    '''

    model = apps.get_model(app_name, model_name)
    query_set = model.objects.all()
    for query in query_set:
        if query.name is not None:
            query.un_name = unidecode.unidecode(query.name)
            query.save()


# Functions for copy_complete: duplicate an entry -----------------------

def dcopy_complete(instance, commit=True):
    '''copy a model instance completely with all relations.'''
    copy = simple_copy(instance, commit)
    app_name, model_name = instance2names(instance)
    for f in copy._meta.get_fields():
        if f.one_to_many:
            if f.name != "primary" and f.name != "secondary":
                for r in list(getattr(instance, f.name + '_set').all()):
                    rcopy = simple_copy(r, False, False)
                    setattr(rcopy, model_name.lower(), copy)
                    rcopy.save()
        if f.many_to_many:
            getattr(copy, f.name).set(getattr(instance, f.name).all())
    return copy

def simple_copy(instance, commit=True, add_copy_suffix=True):
    '''Copy a model instance and save it to the database.
    m2m and relations are not saved.
    '''
    app_name, model_name = instance2names(instance)
    model = apps.get_model(app_name, model_name)
    copy = model.objects.get(pk=instance.pk)
    copy.pk = None
    print('copying...')
    for name in 'title,name,caption,first_name'.split(','):
        if hasattr(copy, name):
            print('setting', name)
            setattr(copy, name, getattr(copy, name) + ' !copy!')
            break
    if commit:
        copy.save()
    return copy
