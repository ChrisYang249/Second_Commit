from import_export import resources
from .models import Project, Sample, SequencingRun

class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project

class SampleResource(resources.ModelResource):
    class Meta:
        model = Sample 

class SeqRunResource(resources.ModelResource):
    class Meta:
        model = SequencingRun