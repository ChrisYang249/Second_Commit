from import_export import resources
from .models import Project
from .models import Sample

class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project

class SampleResource(resources.ModelResource):
    class Meta:
        model = Sample 
