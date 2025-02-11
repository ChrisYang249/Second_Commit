# Register your models here.

from django.contrib import admin, messages
from .models import Client, Project, Sample, SequencingRun
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .resources import ProjectResource, SampleResource, SeqRunResource
from .forms import SampleAdminForm, BulkStatusForm, BulkProjectForm
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
import logging
from django.urls import reverse
from django.utils.html import format_html

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

bulk_update_status.short_description = "Bulk update status for selected samples"

class ProjectAdmin(ImportExportModelAdmin):
    #form = ProjectAdminForm
    #raw_id_fields = ('client',)
    #CSV Importer
    resource_class = ProjectResource
    #change form edit
    fieldsets = (
        (None, {
            'fields': (('project_id', 'client'), ('due_date','status'))
        }),
        ('Delivery Details', {
            'fields': ('service_type','delivery_method','samples_count', 'analyst' ),
        }),
    )

 # List the fields you want to appear in the admin list view.
    # For example: client, due_date, service_type, and status.
    #readonly_fields = ('client_institution',)
    list_display = ('project_id', 'client_institution', 'due_date', 'display_service_type', 'status')
    list_editable = ('status',)
# Optionally, add search fields, filters, etc.
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
    #readonly_fields = ('project_ids',)
    list_display = ('barcode', 'client_sample_name','project_ids','client_institution', 'sample_type', 'sample_status')
    #list_editable = ('status',)
    list_editable = ()
    search_fields = ('barcode', 'client_sample_name','projects__project_id')
    list_filter = ('sample_status', 'projects')

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
            return obj.client.institution
        return "-"
    client_institution.short_description = "Client"    

    def project_ids(self, obj):
        """Returns a comma-separated list of project IDs associated with the sample."""
        # Ensure each project has a project_id value before including it.
        return ", ".join([p.project_id for p in obj.projects.all() if p.project_id])
    project_ids.short_description = "CP"

    #Adjust CSV Export to selected items only
    def export_action(self, request, queryset=None):
        """
        Export only the selected samples to CSV.
        This action is triggered via the admin actions dropdown (via POST),
        so `queryset` will contain only the selected items.
        """
        resource = self.resource_class()
        dataset = resource.export(queryset)

        # Find the CSV export format (case-insensitive)
        csv_format = None
        for fmt_class in self.get_export_formats():
            fmt = fmt_class()  # instantiate the format
            if fmt.get_title().lower() == "csv":
                csv_format = fmt
                break

        if not csv_format:
            raise ValueError("CSV format not found in available export formats")

        csv_data = csv_format.export_data(dataset)
        response = HttpResponse(csv_data, content_type=csv_format.get_content_type())
        response["Content-Disposition"] = 'attachment; filename="selected_samples.csv"'
        return response

    actions = [bulk_update_status, bulk_update_project,export_action]
    export_action.short_description = "Export Selected to CSV"

class SampleInline(admin.TabularInline):
    model = Project.samples.through  # Use the through model if it's a ManyToManyField
    extra = 1

class SeqRunAdmin(ImportExportModelAdmin):
    resource_class = SeqRunResource
    list_display = ('run_name', 'instrument')

admin.site.register(Project, ProjectAdmin)
#admin.site.register(ClientInstitution)
admin.site.register(Client)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SequencingRun, SeqRunAdmin)

