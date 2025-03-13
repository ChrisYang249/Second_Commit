from django.shortcuts import render, get_object_or_404
from .models import Project
from dal import autocomplete
# Create your views here.


class ProjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Project.objects.all().order_by('project_id')
        print(qs)
        if self.q:
            qs = qs.filter(project_id__icontains=self.q)
        return qs

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Assuming Sample has a ForeignKey to Project or a many-to-many relationship
    samples = project.samples.all()  # Adjust the relation accordingly
    context = {
        'project': project,
        'samples': samples,
    }
    return render(request, 'projects/project_detail.html', context)

from django.http import JsonResponse

def csrf_failure_debug(request, reason=""):
    print("🔴 CSRF ERROR: ", reason)
    print("🔴 Full request.POST:", request.POST)
    return JsonResponse({'error': 'CSRF Failed', 'reason': reason}, status=403)

def project_datatable(request):
    # Retrieve all projects (or use a filtered queryset if needed)
    projects = Project.objects.all().order_by('project_id')
    return render(request, 'project_datatable.html', {'projects': projects})