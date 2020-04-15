import re

import math
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
import json

from app.forms import PaperForm, ApplicationForm, DataSetForm, InfrastructureForm, ResultsForm
from app.models import Paper, Application, DataSet, Infrastructure, Results, Person, PaperGroup
from django.shortcuts import render, redirect
from data_extraction import settings
import urllib
import os
from shutil import move
from reportlab.pdfgen import canvas
from django.db.models import Count

import random

from sklearn import cluster
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import adjusted_rand_score


__author__ = 'Dave'


# @login_required()
def index(request):
    completed = Paper.objects.filter(completed=True).all()
    rejected = Paper.objects.filter(completed=False, rejected=True).all()
    background = Paper.objects.filter(completed=False, rejected=False, background=True).all()
    skipped = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=True).all()
    progress = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=True).all()
    incomplete = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=False).all()

    total = len(completed) + len(progress) + len(incomplete) + len(rejected) + len(skipped) + len(background)

    all_papers = Paper.objects.all()

    all_authors = []

    for paper in all_papers:
        if len(paper.person_set.all()) == 0:
            print paper.id
            authors = paper.authors
            author_list = authors.split(' and ')
            for a in author_list:
                forename = None
                surname = None

                m1 = re.match(r"^(?P<surname>.+), (?P<forename>.).+$", a)
                m2 = re.match(r"^(?:[\W]?)*(?P<forename>.)(?:\S)*(?P<surname>(?:[a-z\s])+\S*)$", a)
                m3 = re.match(r"^(?:[\W]?)*(?P<forename>.).* (?P<surname>\S*)$", a)

                if m1 is not None:
                    a_deets = m1.groupdict()
                elif m2 is not None:
                    a_deets = m2.groupdict()
                elif m3 is not None:
                    a_deets = m3.groupdict()

                if a_deets['forename'] is not None and  a_deets['surname'] is not None:
                    forename = a_deets['forename'].strip()
                    surname = a_deets['surname'].strip()

                if forename is not None and surname is not None:
                    print '%s = %s %s' % (a, forename, surname)

                    p, created = Person.objects.get_or_create(
                        forename=forename,
                        surname=surname
                    )

                    paper.person_set.add(p)
                    paper.save()

    for reject in rejected:
        if reject.progress:
            if reject.comments is None:
                print reject.title
                reject.rejected = False
                reject.save()

    totals = {
            'completed': len(completed),
            'progress': len(progress),
            'incomplete': len(incomplete),
            'rejected': len(rejected),
            'skipped': len(skipped),
            'background': len(background)
    }

    if total == 0:
        percentages = {
            'completed': 0,
            'progress': 0,
            'incomplete': 0,
            'background': 0,
            'rejected': 0,
            'skipped': 0
        }
    else:
        percentages = {
            'completed': 100 * len(completed) / total,
            'progress': 100 * len(progress) / total,
            'incomplete': 100 * len(incomplete) / total,
            'rejected': 100 * len(rejected) / total,
            'skipped': 100 * len(skipped) / total,
            'background': 100 * len(background) / total
        }

    return render(request, 'index.html', {'request': request,
                                          'completed': completed,
                                          'progress': progress,
                                          'incomplete': incomplete,
                                          'rejected': rejected,
                                          'skipped': skipped,
                                          'background': background,
                                          'percentages': percentages,
                                          'totals': totals,
                                          'total': total})


# @login_required
def pdf(request, pk):
    folder = 'papers'

    try:
        os.mkdir(os.path.join(settings.MEDIA_ROOT, folder))
    except:
        pass

    uploaded_filename = 'paper-%s.pdf' % pk
    full_filename = os.path.join(settings.MEDIA_ROOT, folder, uploaded_filename)

    file = open(full_filename, 'rb')
    content = file.read()
    file.close

    # serve the file
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=%s' % uploaded_filename

    return response


# @login_required
def extract(request, pk):
    paper = Paper.objects.filter(id=pk).first()

    next_pk = None
    last_pk = None

    state_colours = ['#d9534f', '#5cb85c', '#337ab7', 'skyblue', 'gray', '#f0ad4e']

    paper_list = Paper.objects.filter(id__gt=pk).all()

    if paper.get_state() == 2:
        paper_list = sorted(Paper.objects.all(), key=lambda x: random.random())

    for sibling in paper_list:
        if sibling.get_state() == paper.get_state() and paper.pk != sibling.pk:
            next_pk = sibling.pk
            break

    paper_list = Paper.objects.filter(id__lt=pk).all()
    for sibling in reversed(paper_list):
        if sibling.get_state() == paper.get_state():
            last_pk = sibling.pk
            break

    completed = Paper.objects.filter(completed=True).all()
    rejected = Paper.objects.filter(completed=False, rejected=True).all()
    background = Paper.objects.filter(completed=False, rejected=False, background=True).all()
    skipped = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=True).all()
    progress = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=True).all()
    incomplete = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=False).all()

    total = len(completed) + len(progress) + len(incomplete) + len(rejected) + len(skipped) + len(background)

    totals = {
            'completed': len(completed),
            'progress': len(progress),
            'incomplete': len(incomplete),
            'rejected': len(rejected),
            'skipped': len(skipped),
            'background': len(background)
    }

    if total == 0:
        percentages = {
            'completed': 0,
            'progress': 0,
            'incomplete': 0,
            'background': 0,
            'rejected': 0,
            'skipped': 0
        }
    else:
        percentages = {
            'completed': 100 * len(completed) / total,
            'progress': 100 * len(progress) / total,
            'incomplete': 100 * len(incomplete) / total,
            'rejected': 100 * len(rejected) / total,
            'skipped': 100 * len(skipped) / total,
            'background': 100 * len(background) / total
        }

    form = PaperForm(instance=paper, prefix='paper')

    app_forms = []

    for application in paper.application.all():
        prefix = 'app_%s' % application.pk
        app_form = ApplicationForm(instance=application, prefix=prefix)
        app_forms.append(app_form)

    data_forms = []

    for data in paper.data_set.all():
        prefix = 'data_%s' % data.pk
        data_form = DataSetForm(instance=data, prefix=prefix)
        data_forms.append(data_form)

    results_forms = []

    for result in paper.results.all():
        prefix = 'results_%s' % result.pk
        results_form = ResultsForm(paper_id=paper.id, instance=result, prefix=prefix)
        results_forms.append(results_form)

    if len(app_forms)> 0:
        app_col = int(math.floor(12/len(app_forms)))
    else:
        app_col = 12
        prefix = 'app_0'
        app_form = ApplicationForm(instance=None, prefix=prefix)
        app_forms.append(app_form)

    if len(data_forms)> 0:
        data_col = int(math.floor(12/len(data_forms)))
    else:
        data_col = 12
        prefix = 'data_0'
        data_form = DataSetForm(instance=None, prefix=prefix)
        data_forms.append(data_form)

    if len(results_forms)> 0:
        results_col = int(math.floor(12/len(results_forms)))
    else:
        results_col = 12
        prefix = 'results_0'
        results_form = ResultsForm(paper_id=paper.id, instance=None, prefix=prefix)
        results_forms.append(results_form)

    return render(request, 'extract_paper.html', {'request': request, 'paper': paper,
                                      'next_pk': next_pk,
                                      'last_pk': last_pk,
                                      'form': form,
                                      'app_forms': app_forms,
                                      'data_forms': data_forms,
                                      'results_forms': results_forms,
                                      'percentages': percentages,
                                      'app_col': app_col,
                                      'data_col': data_col,
                                      'results_col': results_col,
                                      'paper_colour': state_colours[paper.get_state()],
                                      'totals': totals})

# @login_required
def edit(request, pk):
    paper = Paper.objects.filter(id=pk).first()

    next_pk = None
    last_pk = None

    state_colours = ['#d9534f', '#5cb85c', '#337ab7', 'skyblue', 'gray', '#f0ad4e']

    paper_list = Paper.objects.filter(id__gt=pk).all()

    if paper.get_state() == 2:
        paper_list = sorted(Paper.objects.all(), key=lambda x: random.random())

    for sibling in paper_list:
        if sibling.get_state() == paper.get_state() and paper.pk != sibling.pk:
            next_pk = sibling.pk
            break

    paper_list = Paper.objects.filter(id__lt=pk).all()
    for sibling in reversed(paper_list):
        if sibling.get_state() == paper.get_state():
            last_pk = sibling.pk
            break

    details_in = 'in'
    apps_in = ''
    data_sets_in = ''
    infra_in = ''
    results_in = ''

    endpoint = 'edit_paper.html'

    if request.method == 'POST':

        endpoint = 'edit_paper_ajax.html'

        form = PaperForm(request.POST, instance=paper, prefix='paper')
        if form.is_valid():
            form.save()

        for application in paper.application.all():
            prefix = 'app_%s' % application.pk
            form = ApplicationForm(request.POST, instance=application, prefix=prefix)
            if form.is_valid():
                form.save()

                apps = Application.objects.filter(paper__pk=paper.pk).all()
                for app in apps:
                    methods = []

                    if app.supervised_learning is not None:
                        for item in app.supervised_learning.split(","):
                            if item.strip() != '':
                                methods.append(item.strip())
                    if app.unsupervised_learning is not None:
                        for item in app.unsupervised_learning.split(","):
                            if item.strip() != '':
                                methods.append(item.strip())

                    print methods

                    if len(methods) > 1:
                        orig_pk = app.pk

                        for method in methods:
                            app.pk = None
                            app.application = '%s classifier' % method
                            if method in app.unsupervised_learning:
                                app.unsupervised_learning = method
                                app.supervised_learning = ''
                            elif method in app.supervised_learning:
                                app.supervised_learning = method
                                app.unsupervised_learning = ''
                            app.save()
                            app = Application.objects.filter(pk=orig_pk).first()

                        app.delete()

        for data in paper.data_set.all():
            prefix = 'data_%s' % data.pk
            form = DataSetForm(request.POST, instance=data, prefix=prefix)
            if form.is_valid():
                form.save()

        for infra in paper.infrastructure.all():
            prefix = 'infra_%s' % infra.pk
            form = InfrastructureForm(request.POST, instance=infra, prefix=prefix)
            if form.is_valid():
                form.save()

        for result in paper.results.all():
            prefix = 'results_%s' % result.pk
            form = ResultsForm(request.POST, instance=result, prefix=prefix)
            if form.is_valid():
                form.save()

        if 'btn-submit' in request.POST:

            submit = request.POST.get('btn-submit')

            if submit == 'accept':
                paper.completed = True
                paper.rejected = False
                paper.background = False
                paper.skipped = False
                paper.save()
            elif submit == 'skip':
                paper.completed = False
                paper.rejected = False
                paper.background = False
                paper.skipped = True
                paper.save()
            elif submit == 'background':
                paper.completed = False
                paper.rejected = False
                paper.background = True
                paper.skipped = False
                paper.save()
            elif submit == 'reject':
                paper.completed = False
                paper.rejected = True
                paper.background = False
                paper.skipped = False
                paper.save()
            elif submit == 'add-data-set':
                data = DataSet.objects.create(paper=paper)
                data.save()
                submit = 'save'
                details_in = ''
                data_sets_in = 'in'
            elif submit == 'add-app':
                application = Application.objects.create(paper=paper)
                application.save()
                submit = 'save'
                details_in = ''
                apps_in = 'in'
            elif submit == 'add-infra':
                infra = Infrastructure.objects.create(paper=paper)
                infra.save()
                submit = 'save'
                details_in = ''
                infra_in = 'in'
            elif submit == 'add-result':
                result = Results.objects.create(paper=paper)
                result.save()
                submit = 'save'
                details_in = ''
                results_in = 'in'

            if submit == 'save':
                pass
            elif next_pk is not None:
                return redirect('edit', pk=next_pk)
            else:
                return redirect('index')

    folder = 'papers'

    completed = Paper.objects.filter(completed=True).all()
    rejected = Paper.objects.filter(completed=False, rejected=True).all()
    background = Paper.objects.filter(completed=False, rejected=False, background=True).all()
    skipped = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=True).all()
    progress = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=True).all()
    incomplete = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=False).all()

    total = len(completed) + len(progress) + len(incomplete) + len(rejected) + len(skipped) + len(background)

    totals = {
            'completed': len(completed),
            'progress': len(progress),
            'incomplete': len(incomplete),
            'rejected': len(rejected),
            'skipped': len(skipped),
            'background': len(background)
    }

    if total == 0:
        percentages = {
            'completed': 0,
            'progress': 0,
            'incomplete': 0,
            'background': 0,
            'rejected': 0,
            'skipped': 0
        }
    else:
        percentages = {
            'completed': 100 * len(completed) / total,
            'progress': 100 * len(progress) / total,
            'incomplete': 100 * len(incomplete) / total,
            'rejected': 100 * len(rejected) / total,
            'skipped': 100 * len(skipped) / total,
            'background': 100 * len(background) / total
        }

    try:
        os.mkdir(os.path.join(settings.MEDIA_ROOT, folder))
    except:
        pass

    form = PaperForm(instance=paper, prefix='paper')

    app_forms = []

    for application in paper.application.all():
        prefix = 'app_%s' % application.pk
        app_form = ApplicationForm(instance=application, prefix=prefix)
        app_forms.append(app_form)

    data_forms = []

    for data in paper.data_set.all():
        prefix = 'data_%s' % data.pk
        data_form = DataSetForm(instance=data, prefix=prefix)
        data_forms.append(data_form)

    infra_forms = []

    for infra in paper.infrastructure.all():
        prefix = 'infra_%s' % infra.pk
        infra_form = InfrastructureForm(instance=infra, prefix=prefix)
        infra_forms.append(infra_form)

    results_forms = []

    for result in paper.results.all():
        prefix = 'results_%s' % result.pk
        results_form = ResultsForm(paper_id=paper.id, instance=result, prefix=prefix)
        results_forms.append(results_form)

    uploaded_filename = 'paper-%s.pdf' % pk
    full_filename = os.path.join(settings.MEDIA_ROOT, folder, uploaded_filename)

    note_length = len(app_forms) + len(data_forms) + len(infra_forms) + len(results_forms)

    return render(request, endpoint, {'request': request,
                                      'paper': paper,
                                      'form': form,
                                      'note_length': note_length,
                                      'app_forms': app_forms,
                                      'data_forms': data_forms,
                                      'infra_forms': infra_forms,
                                      'results_forms': results_forms,
                                      'next_pk': next_pk,
                                      'last_pk': last_pk,
                                      'full_filename': full_filename,
                                      'details_in': details_in,
                                      'apps_in': apps_in,
                                      'data_sets_in': data_sets_in,
                                      'infra_in': infra_in,
                                      'results_in': results_in,
                                      'percentages': percentages,
                                      'paper_colour': state_colours[paper.get_state()],
                                      'totals': totals})


# @login_required
def add(request, pk, action=None):
    completed = Paper.objects.filter(completed=True).all()
    rejected = Paper.objects.filter(completed=False, rejected=True).all()
    background = Paper.objects.filter(completed=False, rejected=False, background=True).all()
    skipped = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=True).all()
    progress = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=True).all()
    incomplete = Paper.objects.filter(completed=False, rejected=False, background=False, skipped=False, progress=False).all()

    total = len(completed) + len(progress) + len(incomplete) + len(rejected) + len(skipped) + len(background)

    totals = {
            'completed': len(completed),
            'progress': len(progress),
            'incomplete': len(incomplete),
            'rejected': len(rejected),
            'skipped': len(skipped),
            'background': len(background)
    }

    if total == 0:
        percentages = {
            'completed': 0,
            'progress': 0,
            'incomplete': 0,
            'background': 0,
            'rejected': 0,
            'skipped': 0
        }
    else:
        percentages = {
            'completed': 100 * len(completed) / total,
            'progress': 100 * len(progress) / total,
            'incomplete': 100 * len(incomplete) / total,
            'rejected': 100 * len(rejected) / total,
            'skipped': 100 * len(skipped) / total,
            'background': 100 * len(background) / total
        }

    paper = Paper.objects.filter(id=pk).first()

    next_pk = None
    last_pk = None

    paper_list = Paper.objects.filter(id__gt=pk).all()
    for sibling in paper_list:
        if sibling.get_state() == paper.get_state():
            next_pk = sibling.pk
            break

    paper_list = Paper.objects.filter(id__lt=pk).all()
    for sibling in reversed(paper_list):
        if sibling.get_state() == paper.get_state():
            last_pk = sibling.pk
            break

    if action == 'skip':
        paper.rejected = True
        paper.save()
        return redirect('add', pk=next_pk)

    if request.method == 'POST':
        paper_link = request.POST.get('paper_link', None)
        paper_location = request.POST.get('paper_location', None)

        folder = 'papers'

        try:
            os.mkdir(os.path.join(settings.MEDIA_ROOT, folder))
        except:
            pass

        uploaded_filename = 'paper-%s.pdf' % pk
        full_filename = os.path.join(settings.MEDIA_ROOT, folder, uploaded_filename)

        if paper_link is not None and paper_link != '':
            web_file = urllib.urlopen(paper_link)
            local_file = open(full_filename, 'w')
            local_file.write(web_file.read())
            web_file.close()
            local_file.close()

            paper.progress = True
            paper.save()

            next_pk = pk + 1

            return redirect('add', pk=next_pk)

        elif paper_location is not None and paper_location != '':
            full_sourcename = os.path.join(settings.MEDIA_ROOT, folder, paper_location)
            move(full_sourcename, full_filename)

            paper.progress = True
            paper.save()

            return redirect('add', pk=next_pk)

    links = paper.link.split(';')
    search = paper.title.replace(' ', '+')

    return render(request, 'add_paper.html', {'request': request,
                                              'paper': paper,
                                              'links': links,
                                              'search': search,
                                              'next_pk': next_pk,
                                              'last_pk': last_pk,
                                              'percentages': percentages,
                                              'totals': totals})


# @login_required
def authors(request):
    authors = Person.objects.annotate(p_count=Count('papers')).order_by('-p_count')

    return render(request, 'authors.html', {'request': request,
                                              'authors': authors})


# @login_required
def groups(request, pk=None):

    if pk is None:
        groups = PaperGroup.objects.annotate(p_count=Count('papers')).order_by('-p_count')
    else:
        groups = PaperGroup.objects.filter(id=pk).annotate(p_count=Count('papers')).order_by('-p_count')

    return render(request, 'groups.html', {'request': request, 'groups': groups})


# @login_required
def table(request, state=1):

    papers = []
    papers_all = Paper.objects.all().order_by('year')

    for paper in papers_all:
        if int(paper.get_state()) == int(state):
            papers.append(paper)

    return render(request, 'table.html', {'request': request, 'papers': papers})


# @login_required
def applications(request, state=1):

    applications = []
    papers_all = Paper.objects.all().order_by('year')

    for paper in papers_all:
        if int(paper.get_state()) == int(state):
            app_group = {'pk': paper.pk, 'authors': paper.citation, 'supervised_learning': [],
                         'unsupervised_learning': [], 'association': []}

            for app in paper.application.all():
                if 'objective' not in app_group:
                    app_group['objective'] = app.objective
                    app_group['morphological_analysis'] = app.morphological_analysis
                    app_group['syntax_analysis'] = app.syntax_analysis
                    app_group['semantic_analysis'] = app.semantic_analysis
                    app_group['dimensionality_reduction'] = app.dimensionality_reduction
                elif app_group['objective'] != app.objective:
                    applications.append(app_group)
                    app_group = {'pk': paper.pk,
                                 'authors': paper.citation, 'objective': app.objective,
                                 'morphological_analysis': app.morphological_analysis,
                                 'syntax_analysis': app.syntax_analysis,
                                 'semantic_analysis': app.semantic_analysis,
                                 'dimensionality_reduction': app.dimensionality_reduction,
                                 'supervised_learning': [], 'unsupervised_learning': [], 'association': []}

                if app.supervised_learning != '':
                    app_group['supervised_learning'].append(app.supervised_learning)
                if app.unsupervised_learning != '':
                    app_group['unsupervised_learning'].append(app.unsupervised_learning)
                if app.association != '':
                    app_group['association'].append(app.association)

            app_group['supervised_learning'] = json.dumps(app_group['supervised_learning'])
            app_group['unsupervised_learning'] = json.dumps(app_group['unsupervised_learning'])
            app_group['association'] = json.dumps(app_group['association'])

            applications.append(app_group)

    return render(request, 'applications.html', {'request': request, 'applications': applications})


# @login_required
def data_sets(request, state=1):

    data_sets = []
    papers_all = Paper.objects.all().order_by('year')

    for paper in papers_all:
        if int(paper.get_state()) == int(state):
            data_set_group = {'pk': paper.pk, 'authors': paper.citation}

            for data_set in paper.data_set.all():
                if 'type' not in data_set_group:
                    data_set_group['type'] = data_set.type
                    data_set_group['source'] = data_set.source
                    data_set_group['volume'] = data_set.volume
                    data_set_group['coverage'] = data_set.coverage
                elif data_set_group['type'] != data_set.type:
                    data_sets.append(data_set_group)
                    data_set_group = {'pk': paper.pk,
                                      'authors': paper.citation,
                                      'type': data_set.type,
                                      'source': data_set.source,
                                      'volume': data_set.volume,
                                      'coverage': data_set.coverage}

            data_sets.append(data_set_group)

    return render(request, 'data_sets.html', {'request': request, 'data_sets': data_sets})


# @login_required
def results(request, state=1):

    results = []
    papers_all = Paper.objects.all().order_by('year')

    for paper in papers_all:
        if int(paper.get_state()) == int(state):

            for result in paper.results.all():
                result_group = {'pk': paper.pk, 'title': paper.title, 'citation': paper.citation, 'authors': paper.authors, 'learning': []}
                data_set = result.data_set
                app = result.application

                if app is not None:
                    result_group['objective'] = app.objective
                    result_group['morphological_analysis'] = app.morphological_analysis
                    result_group['syntax_analysis'] = app.syntax_analysis
                    result_group['semantic_analysis'] = app.semantic_analysis
                    result_group['dimensionality_reduction'] = app.dimensionality_reduction

                    if app.supervised_learning != '':
                        result_group['learning'].append(app.supervised_learning)
                    if app.unsupervised_learning != '':
                        result_group['learning'].append(app.unsupervised_learning)
                    if app.association != '':
                        result_group['learning'].append(app.association)

                    result_group['learning'] = json.dumps(result_group['learning'])

                if data_set is not None:
                    result_group['type'] = data_set.type
                    result_group['source'] = data_set.source
                    result_group['volume'] = data_set.volume
                    result_group['coverage'] = data_set.coverage

                results.append(result_group)

    return render(request, 'results.html', {'request': request, 'results': results})