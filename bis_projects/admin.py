# Register your models here.

from django.contrib import admin, messages
from .models import Client, Project, Sample, SequencingRun, LogEntry
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .resources import ProjectResource, SampleResource, SeqRunResource
from .forms import SampleAdminForm, BulkStatusForm, BulkProjectForm, ProjectSampleInlineForm
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
import logging
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.forms import Textarea

logger = logging.getLogger(__name__)


class LogEntryInline(GenericTabularInline):
    model = LogEntry
    ct_field = "content_type"
    ct_fk_field = "object_id"
    extra = 1
    can_delete = True  # Allow deletion if user has permission
    # Explicitly list the fields you want to display:
    fields = ('comment', 'display_author', 'created_at',)
    readonly_fields = ('display_author', 'created_at',)
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 3, 'cols': 40})
        },
    }

    def has_delete_permission(self, request, obj=None):
        # Only allow deletion if the user is a superuser.
        return request.user.is_superuser

    def display_author(self, obj):
        """Safely display the author of a log entry.
        For unsaved entries with no author, show a placeholder.
        """
        return obj.author if obj.author else "Not set"
    display_author.short_description = "Author"

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        # Define a custom formset that automatically sets the author.
        class RequestFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # For each form, if it’s a new instance without an author, set the initial value.
                for form in self.forms:
                    if not form.instance.pk and not getattr(form.instance, 'author', None):
                        form.initial['author'] = request.user.pk

            def save_new(self, form, commit=True):
                instance = super().save_new(form, commit=False)
                if not instance.author:
                    instance.author = request.user
                if commit:
                    instance.save()
                return instance

            def save_existing(self, form, instance, commit=True):
                if not instance.author:
                    instance.author = request.user
                return super().save_existing(form, instance, commit=commit)
        return RequestFormSet

class SampleInline(admin.TabularInline):
    model = Project.samples.through  # The auto-created through model for the ManyToManyField
    form = ProjectSampleInlineForm
    extra = 1

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
        ('Samples', {
            'fields' : ('view_samples_link',)
        }),
        ('Log', {'fields':()})
    )
    readonly_fields = ('view_samples_link',)

 # List the fields you want to appear in the admin list view.
    # For example: client, due_date, service_type, and status.
    #readonly_fields = ('client_institution')
    inlines = [SampleInline,LogEntryInline]
    #list_display = ('project_id', 'client_institution', 'due_date', 'display_service_type', 'status')
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

    #Make View Samples Link in projects page
    def view_samples_link(self, obj):
        # Replace 'yourapp' with your actual app label.
        url = reverse("admin:bis_projects_sample_changelist") + f"?projects__id__exact={obj.id}"
        return format_html('<a href="{}">View Samples</a>', url)

    view_samples_link.short_description = "Samples"
    # Then include this method in your list_display or as a read-only field in your change form.
    list_display = ('project_id', 'client', 'due_date', 'service_type', 'status', 'view_samples_link')

class SampleAdmin(ImportExportModelAdmin):
    #CSV Importer
    confirm_import = True
    resource_class = SampleResource
    change_list_template = "admin/bis_projects/sample/change_list.html"
    form = SampleAdminForm
    list_per_page = 25
    #Sample page change form rearrange
    fieldsets = (
        (None, {
            # This tuple puts these two fields on the same line$
            # Include the client field here along with projects and barcode.
            'fields': (('client', 'project_ids', 'barcode'), ('client_sample_name', 'sample_type'))
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
    list_display = ('barcode', 'truncated_sample_name','project_ids','client_institution', 'sample_type', 'sample_status','sequencing_run_info')
    #list_editable = ('status',)
    list_editable = ()
    search_fields = ('barcode', 'client_sample_name','projects__project_id')
    list_filter = ('sample_status', 'projects')
    inlines = [LogEntryInline]

    #change number of pages on sample list view
    def get_list_per_page(self, request):
        page_size_param = request.GET.get('page_size')
        print("DEBUG: page_size =", page_size_param)
        if page_size_param:
            try:
                num_results = int(page_size_param)
                # Enforce limits: minimum 25, maximum 500.
                num_results = max(25, min(num_results, 500))
                print("DEBUG: Returning per_page =", num_results)
                return num_results
            except ValueError:
                print("DEBUG: ValueError converting page_size:", page_size_param)
        default_value = super().get_list_per_page(request)
        print("DEBUG: Returning default_value =", default_value)
        return default_value

    # Method to display the sequencing run info.
    def sequencing_run_info(self, obj):
        runs = obj.sequencing_runs.all()  # using the related_name from SequencingRun.samples
        if runs.exists():
            first_run = runs.first().run_name  # Here you could sort by a date field if available.
            count = runs.count()
            if count > 1:
                return f"{first_run} (+{count - 1} more)"
            return first_run
        return ""
    sequencing_run_info.short_description = "Sequencing Run"

    def get_changelist_instance(self, request):
        # When a bulk action is triggered, disable list_editable so that
        # the POST data does not include formset management keys.
        if request.POST.get('action'):
            self.list_editable = ()
        return super().get_changelist_instance(request)
    
    def client_institution(self, obj):
        """Returns the Client Institution name for the sample, if available."""
        if obj.client and obj.client.institution:
            # Return the institution's
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
    #alter changelist in sample
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Check if the view is filtered by a specific project.
        project_id = request.GET.get('projects__id__exact')
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                # Build your custom header string. Adjust as needed.
                header = f"Project {project.project_id} - {project.client.institution} - Sample Information"
            except Project.DoesNotExist:
                header = "Sample Information"
            extra_context['custom_header'] = header
        return super().changelist_view(request, extra_context=extra_context)

    def get_import_context_data(self, **kwargs):
        context = super().get_import_context_data(**kwargs)
        dataset = context.get('dataset')
        if dataset is not None:
            print("dataset size:", len(dataset))
            context['sample_count'] = len(dataset)
        else:
            print("dataset is None")
        print("DEBUG: (Import):", context)
        return context

    def get_confirm_context_data(self, **kwargs):
        print(">>> ENTERING get_confirm_context_data()")
        context = super().get_confirm_context_data(**kwargs)
        dataset = context.get('dataset')
        if dataset is not None:
            context['sample_count'] = len(dataset)
        else:
            context['sample_count'] = 0
        print("DEBUG (confirm):", context)
        return context

    def truncated_sample_name(self, obj):
        """
        Returns a truncated version of the sample name (client_sample_name),
        limited to 25 characters, with an ellipsis if longer.
        """
        name = obj.client_sample_name or ""
        max_length = 25  # adjust as needed
        if len(name) > max_length:
            return name[:max_length] + "..."
        return name

    truncated_sample_name.short_description = "Sample Name"
"""
class SampleInline(admin.TabularInline):
    model = Project.samples.through  # Use the through model if it's a ManyToManyField
    extra = 1
"""
class SeqRunAdmin(ImportExportModelAdmin):
    resource_class = SeqRunResource
    list_display = ('run_name', 'instrument')

admin.site.register(Project, ProjectAdmin)
#admin.site.register(ClientInstitution)
admin.site.register(Client)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SequencingRun, SeqRunAdmin)

