from django.db import models


# Create your models here.
class Paper(models.Model):
    completed = models.BooleanField(blank=True, default=False)
    progress = models.BooleanField(blank=True, default=False)
    skipped = models.BooleanField(blank=True, default=False)
    background = models.BooleanField(blank=True, default=False)
    rejected = models.BooleanField(blank=True, default=False)

    authors = models.CharField(max_length=512L, blank=True)
    title = models.CharField(max_length=512L, blank=True)
    citation = models.CharField(max_length=512L, blank=True)
    year = models.CharField(max_length=512L, blank=True)
    link = models.CharField(max_length=512L, blank=True)

    comments = models.TextField(blank=True)

    group = models.ForeignKey('PaperGroup', null=True, blank=True, related_name='papers')

    def get_state(self):
        if self.completed:
            return 1
        elif self.rejected:
            return 0
        elif self.background:
            return 5
        elif self.skipped:
            return 3
        elif self.progress:
            return 2
        else:
            return 4


class Person(models.Model):
    forename = models.CharField(max_length=512L, blank=True)
    surname = models.CharField(max_length=512L, blank=True)
    papers = models.ManyToManyField(Paper)


class PaperGroup(models.Model):
    title = models.CharField(max_length=512L, blank=True)


class Application(models.Model):
    paper = models.ForeignKey('Paper', null=True, blank=True, related_name='application')
    application = models.CharField(max_length=512L, blank=True)
    objective = models.CharField(max_length=512L, blank=True)

    morphological_analysis = models.CharField(max_length=512L, blank=True)
    syntax_analysis = models.CharField(max_length=512L, blank=True)
    semantic_analysis = models.CharField(max_length=512L, blank=True)
    dimensionality_reduction = models.CharField(max_length=512L, blank=True)

    supervised_learning = models.CharField(max_length=512L, blank=True)
    unsupervised_learning = models.CharField(max_length=512L, blank=True)
    association = models.CharField(max_length=512L, blank=True)

    text_mining_program = models.CharField(max_length=512L, blank=True)
    infrastructure = models.CharField(max_length=512L, blank=True)
    data_storage = models.CharField(max_length=512L, blank=True)

    def __unicode__(self):
        if not self.application:
            siblings = self.paper.application.all()
            i = 1
            for item in siblings:
                if item == self:
                    break
                i += 1

            return 'Application ' + str(i)
        else:
            return self.application


class DataSet(models.Model):
    paper = models.ForeignKey('Paper', null=True, blank=True, related_name='data_set')
    type = models.CharField(max_length=512L, blank=True)
    source = models.CharField(max_length=512L, blank=True)
    volume = models.CharField(max_length=512L, blank=True)
    coverage = models.CharField(max_length=512L, blank=True)

    def __unicode__(self):
        if not self.type:
            siblings = self.paper.data_set.all()
            i = 1
            for item in siblings:
                if item == self:
                    break
                i += 1

            return 'Data Set ' + str(i)
        else:
            return self.type


class Results(models.Model):
    paper = models.ForeignKey('Paper', null=True, blank=True, related_name='results')
    application = models.ForeignKey('Application', null=True, blank=True, related_name='results')
    data_set = models.ForeignKey('DataSet', null=True, blank=True, related_name='results')
    infrastructure = models.ForeignKey('Infrastructure', null=True, blank=True, related_name='results')
    precision = models.CharField(max_length=512L, blank=True)
    recall = models.CharField(max_length=512L, blank=True)
    f_measure = models.CharField(max_length=512L, blank=True)
    processing_time = models.CharField(max_length=512L, blank=True)


class Infrastructure(models.Model):
    paper = models.ForeignKey('Paper', null=True, blank=True, related_name='infrastructure')
    memory = models.CharField(max_length=512L, blank=True)
    cores = models.CharField(max_length=512L, blank=True)
    disk_space = models.CharField(max_length=512L, blank=True)

    def __unicode__(self):
        siblings = self.paper.infrastructure.all()
        i = 1
        for item in siblings:
            if item == self:
                break
            i += 1

        return 'Infrastructure ' + str(i)
