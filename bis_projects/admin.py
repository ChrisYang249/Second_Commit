# Register your models here.

from django.contrib import admin, messages
from .models import ClientInstitution, Client, Project, Sample, SequencingRun
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .resources import ProjectResource, SampleResource
from .forms import SampleAdminForm, BulkStatusForm, BulkProjectForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
import logging


logger = logging.getLogger(__name__)

def bulk_update_project(modeladmin, request, queryset):

    if 'apply' in request.POST:
        form = BulkProjectForm(request.POST)

        if form.is_valid():
            new_project = form.cleaned_data['project']
            for sample in queryset:
                # Replace existing associations with the new project.
                sample.projects.clear()
                sample.projects.add(new_project)
            modeladmin.message_user(request, "Project associations updated successfully.", messages.SUCCESS)
            return
    else:
        form = BulkProjectForm(initial={'_selected_action': request.POST.getlist("action_checkbox")})

    return render(request, 'admin/bulk_project_update.html', {
        'samples': queryset,
        'form': form,
        'title': "Bulk Update Project for Selected Samples",
    })
bulk_update_project.short_description = "Bulk update project for selected samples"

def bulk_update_status(modeladmin, request, queryset):
    logger.info("Bulk update status POST data: %s", request.POST)

    if request.method == "POST":  # ✅ Check if form was submitted
        print("🔍 Full request.POST data:", request.POST)

        form = BulkStatusForm(request.POST)
        print("📌 Form received:", form)

        if form.is_valid():
            new_status = form.cleaned_data['sample_status']  # ✅ Ensure correct field name
            print("✅ New status:", new_status)

            # Update the status for all selected samples
            updated_count = queryset.update(sample_status=new_status)  # ✅ Make sure `sample_status` is correct
            modeladmin.message_user(
                request,
                f"{updated_count} samples updated to status '{new_status}'.",
                messages.SUCCESS
            )
            return HttpResponseRedirect(request.get_full_path())

    else:
        form = BulkStatusForm()

    return render(request, 'admin/bulk_status_update.html', {
        'samples': queryset,
        'form': form,
        'title': "Bulk Update Status for Selected Samples",
    })
"""

def bulk_update_status(modeladmin, request, queryset):

    if "bulk_update_status" in request.POST:  # Form submission check
        form = BulkStatusForm(request.POST)
        if "sample_status" not in request.POST:
            print("❌ ERROR: `sample_status` is missing from request.POST!")

        if form.is_valid():
            new_status = form.cleaned_data["sample_status"]
            selected_sample_ids = request.POST.getlist("_selected_action")
            updated_count = Sample.objects.filter(id__in=selected_sample_ids).update(sample_status=new_status)
            modeladmin.message_user(
                request, f"{updated_count} samples updated to status '{new_status}'.", messages.SUCCESS
            )

            return HttpResponseRedirect(request.get_full_path())

        else:
            print("❌ DEBUG: Form errors:", form.errors)

    else:
        form = BulkStatusForm()

    return render(request, "admin/bulk_status_update.html", {
        "samples": queryset,
        "form": form,
        "title": "Bulk Update Status for Selected Samples",
    })


def bulk_update_status(modeladmin, request, queryset):
    print("🔍 DEBUG: Full request.POST:", request.POST)

    selected_sample_ids = request.POST.getlist("_selected_action")
    sample_status_value = request.POST.get("sample_status")

    print("🔍 DEBUG: Selected Sample IDs:", selected_sample_ids)
    print("🔍 DEBUG: Received Status Value:", sample_status_value)

    if not sample_status_value:
        print("❌ ERROR: 'sample_status' field is missing from POST request!")

    form = BulkStatusForm(request.POST)
    print("🔍 DEBUG: Form choices:", form.fields["sample_status"].choices)

    if form.is_valid():
        new_status = form.cleaned_data["sample_status"]
        print("✅ DEBUG: New Status:", new_status)

        updated_count = Sample.objects.filter(id__in=selected_sample_ids).update(sample_status=new_status)
        print("✅ DEBUG: Updated Count:", updated_count)

        modeladmin.message_user(
            request, f"{updated_count} samples updated to status '{new_status}'.", messages.SUCCESS
        )

        return HttpResponseRedirect(request.get_full_path())

    else:
        print("❌ DEBUG: Form errors:", form.errors)

    return render(request, 'admin/bulk_status_update.html', {
        'samples': queryset,
        'form': form,
        'title': "Bulk Update Status for Selected Samples",
    })


def bulk_update_status(modeladmin, request, queryset):
    print("🔍 DEBUG: Full request.POST:", request.POST)  # Ensure "status" exists in POST

    bulk_update_value = request.POST.get("bulk_update_status")
    selected_sample_ids = request.POST.getlist("_selected_action")

    print("🔍 DEBUG: Full request.POST:", request.POST)  # Shows all POST data

    print("🔍 DEBUG: request.POST keys:", list(request.POST.keys()))  # Shows all available keys

    print("🔍 DEBUG: request.POST items:", request.POST.items())  # Shows key-value pairs

    #print("🔍 DEBUG: request.body:", request.body)  # Shows raw body data (if any)
    #print("🔍 DEBUG: Selected Sample IDs:", selected_sample_ids, bulk_update_value)
    #print("Full Request", request)
    if request.method == "POST" and bulk_update_value == "1":
        form = BulkStatusForm(request.POST)

        print("🔍 DEBUG: Form received:", form)

        if form.is_valid():
            new_status = form.cleaned_data['status']
            print("✅ DEBUG: New status:", new_status)

            # Apply update
            updated_count = Sample.objects.filter(id__in=selected_sample_ids).update(status=new_status)
            print("✅ DEBUG: Updated count:", updated_count)

            modeladmin.message_user(
                request,
                f"{updated_count} samples updated to status '{new_status}'.",
                messages.SUCCESS
            )
            return HttpResponseRedirect(request.get_full_path())

        else:
            print("❌ DEBUG: Form is INVALID")
            print("❌ DEBUG: Form errors:", form.errors)

    else:
        print("❌ DEBUG: Missing 'status' field in POST")

    form = BulkStatusForm(initial={'_selected_action': request.POST.getlist("_selected_action")})

    return render(request, 'admin/bulk_status_update.html', {
        'samples': queryset,
        'form': form,
        'title': "Bulk Update Status for Selected Samples",
    })

def bulk_update_status(modeladmin, request, queryset):
    logger.info("Bulk update status POST data: %s", request.POST)
    Custom admin action to update the status of selected Sample records.

    cleaned_post = {k: v for k, v in request.POST.items() if not k.startswith("form-")}
    print("request.POST:", request.POST)
    print("Cleaned POST Data:", cleaned_post.values())
    print(queryset) 

    #if cleaned_post.get('bulk_update_status') == '1':
    #if 'bulk_update_status' in cleaned_post.values():
    #if 'apply' in request.POST:
    #if request.method == "POST" :and "bulk_update_status" in cleaned_post:
    if request.method == "POST":
        print("full debug:", request.POST)
        form = BulkStatusForm(request.POST)
        print("Form received:", form)
        logger.info("Submit triggered: 'apply' found in POST")
        if form.is_valid():
            new_status = form.cleaned_data['status']
            logger.info("New status: %s", new_status)            
            print("New status:", new_status)
            # Update the status for all selected samples.
            updated_count = queryset.update(status=new_status)
            modeladmin.message_user(
                request,
                f"{updated_count} samples updated to status '{new_status}'.",
                messages.SUCCESS
            )
            # Redirect back to the change list.
            return HttpResponseRedirect(request.get_full_path())
    else:
        print("FAIL")
        logger.info("No 'apply' in POST; rendering form")
        form = BulkStatusForm(initial={
            '_selected_action': request.POST.getlist("action_checkbox")
        })
    print("here")
    return render(request, 'admin/bulk_status_update.html', {
        'samples': queryset,
        'form': form,
        'title': "Bulk Update Status for Selected Samples",
    })
""" 
bulk_update_status.short_description = "Bulk update status for selected samples"



class ProjectAdmin(ImportExportModelAdmin):
    #CSV Importer
    resource_class = ProjectResource   
 # List the fields you want to appear in the admin list view.
    # For example: client, due_date, service_type, and status.
    list_display = ('project_id', 'client_institution', 'due_date', 'display_service_type', 'status')
    #list_display = ('client', 'due_date', 'service_type', 'status')
    list_editable = ('status',)
    
# Optionally, add search fields, filters, etc.
    #search_fields = ('client__name', 'service_type')
    search_fields = ('project_id', 'client__name', 'client__institution', 'service_type') 
    list_filter = ('status', ('due_date', DateRangeFilter))

    def client_institution(self, obj):
        # Assuming the Client model has a field called "institution"
        return obj.client.institution
    client_institution.short_description = 'Institution'

    def display_service_type(self, obj):
        # This returns the service_type field, but we use a custom header.
        return obj.service_type
    display_service_type.short_description = 'Type'

class SampleAdmin(ImportExportModelAdmin):
    #CSV Importer
    resource_class = SampleResource
    form = SampleAdminForm
    #Sample page change form edit

    fieldsets = (
        (None, {
            # This tuple puts these two fields on the same line$
            # Include the client field here along with projects and barcode.
            'fields': (('client', 'projects','project_ids', 'barcode'), ('client_sample_name', 'sample_type'))
        }),
        ('Extraction Details', {
            'fields': (('extraction_quant', 'extraction_kit'),)
        }),
        ('Library Details', {
            'fields': (('library_quant', 'library_kit'),)
        }),
        ('Sequencing Details', {
            'fields': (('targeted_depth', 'sample_status'),)
        }),
    )
    readonly_fields = ('project_ids',)
    list_display = ('barcode', 'client_sample_name','project_ids','client_institution', 'sample_type', 'sample_status')
    #list_editable = ('status',)
    list_editable = ()
    search_fields = ('barcode', 'client_sample_name')
    actions = [bulk_update_status, bulk_update_project]
    
    def get_changelist_instance(self, request):
        # When a bulk action is triggered, disable list_editable so that
        # the POST data does not include formset management keys.
        if request.POST.get('action'):
            self.list_editable = ()
        return super().get_changelist_instance(request)
    
    def client_institution(self, obj):
        """Returns the Client Institution name for the sample, if available."""
        if obj.client and obj.client.institution:
            # Return the institution's name (ClientInstitution.__str__ returns name,
            # but explicitly returning .name may be clearer)
            return obj.client.institution.name
        return "-"
    client_institution.short_description = "Client"    

    def project_ids(self, obj):
        """Returns a comma-separated list of project IDs associated with the sample."""
        # Ensure each project has a project_id value before including it.
        return ", ".join([p.project_id for p in obj.projects.all() if p.project_id])
    project_ids.short_description = "CP"

class SampleInline(admin.TabularInline):
    model = Project.samples.through  # Use the through model if it's a ManyToManyField
    extra = 1

admin.site.register(ClientInstitution)
admin.site.register(Client)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SequencingRun)

