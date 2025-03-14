from django import forms
from .models import Sample, Project, STATUS_CHOICES, SequencingRun
from django.contrib.admin.widgets import FilteredSelectMultiple #, AutocompleteSelect
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.forms.fields import DateField
from rangefilter.filters import DateRangeFilter
from django.forms.widgets import DateInput
from django.urls import reverse
from django.contrib import admin
from dal import autocomplete

#### part of making project dropdown work" #####
from django.db.models.fields.related import ManyToManyRel
if not hasattr(ManyToManyRel, 'get_limit_choices_to'):
    def get_limit_choices_to(self):
        return self.limit_choices_to or {}
    ManyToManyRel.get_limit_choices_to = get_limit_choices_to

#### part of making project dropdown work" #####
"""class CustomDateField(forms.DateField):
    def to_python(self, value):
        print("DEBUG: CustomDateField received:", value, type(value))  # Debugging

        # If value is a list, extract the first non-empty element
        if isinstance(value, list):
            value = next((v for v in value if v.strip()), None)

        # If the value is empty, return None
        if value in [None, '']:
            return None

        return super().to_python(value)

class CustomDateInput(DateInput):
    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        # If the value is a list, return the first element.
        if isinstance(value, list):
            return value[0] if value else ''
        return value"""

"""class CustomDateRangeFilter(DateRangeFilter):
    @property
    def form_class(self):
        # Define a custom form that uses CustomDateField for both endpoints.
        class CustomDateRangeForm(forms.Form):
            gte = CustomDateField(required=False, input_formats=['%Y-%m-%d'])
            lte = CustomDateField(required=False, input_formats=['%Y-%m-%d'])
        return CustomDateRangeForm"""

class BulkStatusForm(forms.Form):
    # This hidden field will store the IDs of the selected objects.
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    # A choice field for the new status.
    sample_status = forms.ChoiceField(choices=STATUS_CHOICES, label="New Status",
                                      help_text="Select the new status for the selected samples.",
                                      required=True,)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Set default value for sample_status properly
        if not self.is_bound:
            self.fields["sample_status"].initial = "LAB"

class BulkProjectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),  # you can filter by active status if needed
        label="New Project",
        help_text="Select the project to associate with the selected samples."
    )

class SingleProjectChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.project_id

class SampleAdminForm(forms.ModelForm):
    # New field for a single project selection
    """project = SingleProjectChoiceField(
        queryset=Project.objects.all(),
        required=False,
        label="Project"
        #help_text="Select a project for this sample."
    )"""
    project = SingleProjectChoiceField(
        queryset=Project.objects.all().order_by("project_id"),
        required=False,
        label="Project",
        widget=autocomplete.ModelSelect2(url='project-autocomplete')
    )

    class Meta:
        model = Sample
        #fields = '__all__'
        exclude = ['projects']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select the first related project if one exists.
        if self.instance.pk and self.instance.projects.exists():
            self.fields['project'].initial = self.instance.projects.first()

    """def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.projects.exists():
            print("True here")
            self.fields['project'].initial = self.instance.projects.first()
        self.fields['project'].widget = AutocompleteSelect(
            Sample._meta.get_field('projects').remote_field,
            admin.site,
        )
        # Ensure the widget's choices are in the correct format
        self.fields['project'].widget.choices = self.fields['project'].choices"""

    """    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select the first related project if one exists
        if self.instance.pk and self.instance.projects.exists():
            self.fields['project'].initial = self.instance.projects.first()
        # Use the AutocompleteSelect widget for the "project" field.
        # We use the remote_field from the underlying 'projects' field.
        self.fields['project'].widget = AutocompleteSelect(
            Sample._meta.get_field('projects').remote_field,
            admin.site,
        )"""

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Optionally, auto-populate client from the selected project if not already set.
        if not instance.client:
            selected_project = self.cleaned_data.get('project')
            if selected_project:
                instance.client = selected_project.client
        if commit:
            instance.save()
        # Update the many-to-many field based on the selected project.
        selected_project = self.cleaned_data.get('project')
        if selected_project:
            instance.projects.set([selected_project])
        else:
            instance.projects.clear()
        return instance

    """    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # If the client is not set, auto-populate it from the selected project(s)
        # For example, if you want to use the client from the first selected project:
        if not instance.client:
            projects = instance.projects.all()
            if projects.exists():
                instance.client = projects.first().client
        if commit:
            instance.save()
            # For many-to-many fields, save them after saving the instance
            self.save_m2m()
        return instance
    """

class ProjectSampleInlineForm(forms.ModelForm):
    # Add a field for sample_status that isn't part of the through model.
    sample_status = forms.CharField(label="Status", required=False)

    class Meta:
        # The model here is the through model of Project.samples.
        model = Sample.projects.through  # or Project.samples.through; they are equivalent.
        # Use all fields from the through model (typically project and sample)
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the sample_status field from the related Sample if it exists.
        if self.instance and self.instance.pk and self.instance.sample:
            self.fields['sample_status'].initial = self.instance.sample.sample_status

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Get the cleaned data for sample_status
        new_status = self.cleaned_data.get('sample_status', None)
        # If the related Sample exists and its status differs, update it.
        if instance.sample and new_status is not None:
            if instance.sample.sample_status != new_status:
                instance.sample.sample_status = new_status
                instance.sample.save()
        if commit:
            instance.save()
        return instance
"""

class ProjectAdminForm(forms.ModelForm):
    # This field is not on the Project model; it's a proxy for client.institution.
    client_institution = forms.CharField(
        label="Client Institution",
        required=False,
        help_text="Enter the client institution name."
    )

    class Meta:
        model = Project
        # List all the fields you want on the form.
        # Notice we include 'client_institution' even though it's not a model field.
        fields = [
            'project_id',
            'client',
            'due_date',
            'service_type',
            'delivery_method',
            'deliverables',
            'samples_count',
            'status',
            'analyst',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If an instance exists and has a related client, pre-populate our field.
        if self.instance and self.instance.pk and self.instance.client:
            # Use .get() to avoid KeyError.
            if 'client_institution' in self.fields:
                self.fields['client_institution'].initial = self.instance.client.institution


    def save(self, commit=True):
        instance = super().save(commit=False)
        # Update the related client's institution field.
        if instance.client:
            new_institution = self.cleaned_data.get('client_institution', '')
            if instance.client.institution != new_institution:
                instance.client.institution = new_institution
                instance.client.save()
        if commit:
            instance.save()
        return instance
"""

class SequencingRunForm(forms.ModelForm):
    class Meta:
        model = SequencingRun
        fields = '__all__'
        widgets = {
            'samples': forms.SelectMultiple(attrs={
                'class': 'samples-select',
                'style': 'width: 100%; min-height: 200px;'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['samples'].queryset = Sample.objects.all().order_by('barcode')
            self.fields['samples'].label_from_instance = lambda obj: f"{obj.barcode} - {obj.client_sample_name} ({obj.sample_status})"