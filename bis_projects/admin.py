# Register your models here.

from django.contrib import admin
from .models import ClientInstitution, Client, Project, Sample, SequencingRun
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .resources import ProjectResource

#class ProjectAdmin(admin.ModelAdmin):
class ProjectAdmin(ImportExportModelAdmin):
    #CSV Importer
    resource_class = ProjectResource   
 # List the fields you want to appear in the admin list view.
    # For example: client, due_date, service_type, and status.
    list_display = ('client', 'due_date', 'service_type', 'status')
    list_editable = ('status',)
    
# Optionally, add search fields, filters, etc.
    search_fields = ('client__name', 'service_type')
    list_filter = ('status', ('due_date', DateRangeFilter))

class SampleAdmin(admin.ModelAdmin):

    #Sample page change form edit
    fieldsets = (
        (None, {
            # This tuple puts these two fields on the same line
            'fields': (('projects', 'barcode'), ('client_sample_name', 'sample_type'))
        }),
        ('Extraction Details', {
            'fields': (('extraction_quant', 'extraction_kit'),)
        }),
        ('Library Details', {
            'fields': (('library_quant', 'library_kit'),)
        }),
        # add additional groups as needed
    )
    list_display = ('barcode', 'client_sample_name', 'sample_type', 'status')
    list_editable = ('status',)
    search_fields = ('barcode', 'client_sample_name')

class SampleInline(admin.TabularInline):
    model = Project.samples.through  # Use the through model if it's a ManyToManyField
    extra = 1

#class ProjectAdmin(admin.ModelAdmin):
#    list_display = ('client', 'due_date', 'service_type', 'status')
#    inlines = [SampleInline]

admin.site.register(ClientInstitution)
admin.site.register(Client)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SequencingRun)

