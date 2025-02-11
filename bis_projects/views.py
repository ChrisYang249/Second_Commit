from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404
from .models import Project

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
