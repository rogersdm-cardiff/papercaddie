from django import forms
from django.forms import ModelForm
from models import Paper, Application, DataSet, Infrastructure, Results


class PaperForm(ModelForm):
    class Meta:
        model = Paper
        widgets = {
            'authors': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'year': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        fields = ['authors', 'title', 'year', 'comments']


class DataSetForm(ModelForm):
    class Meta:
        model = DataSet
        widgets = {
            'type': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'source': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'volume': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'coverage': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['type', 'source', 'volume', 'coverage']


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        widgets = {
            'application': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            'morphological_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'syntax_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'semantic_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'dimensionality_reduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            'supervised_learning': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'unsupervised_learning': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'association': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            'text_mining_program': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'infrastructure': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'data_storage': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['application', 'objective', 'morphological_analysis', 'syntax_analysis',
                  'semantic_analysis', 'dimensionality_reduction', 'supervised_learning',
                  'unsupervised_learning', 'association', 'text_mining_program',
                  'infrastructure', 'data_storage']


class InfrastructureForm(ModelForm):
    class Meta:
        model = Infrastructure
        widgets = {
            'memory': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cores': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'disk_space': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        fields = ['memory', 'cores', 'disk_space']


class ResultsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        paper_id = kwargs.pop('paper_id', None)
        super(ResultsForm, self).__init__(*args, **kwargs)

        if paper_id:
            self.fields['application'].queryset = Application.objects.filter(paper__id=paper_id)
            self.fields['data_set'].queryset = DataSet.objects.filter(paper__id=paper_id)
            self.fields['infrastructure'].queryset = Infrastructure.objects.filter(paper__id=paper_id)

    class Meta:
        model = Results

        application = forms.ModelChoiceField(queryset=Application.objects.all())
        data_set = forms.ModelChoiceField(queryset=DataSet.objects.all())
        infrastructure = forms.ModelChoiceField(queryset=Infrastructure.objects.all())

        widgets = {
            'application': forms.Select(attrs={'class': 'form-control'}),
            'data_set': forms.Select(attrs={'class': 'form-control'}),
            'infrastructure': forms.Select(attrs={'class': 'form-control'}),
            'precision': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'recall': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'f_measure': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'processing_time': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

        fields = ['application', 'data_set', 'infrastructure', 'precision', 'recall',
                  'f_measure', 'processing_time']