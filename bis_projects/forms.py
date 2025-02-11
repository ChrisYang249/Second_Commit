from django import forms
from .models import Sample, Project, STATUS_CHOICES
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

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

class SampleAdminForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the label_from_instance to return just the project_id.
        self.fields["projects"].label_from_instance = lambda obj: obj.project_id
    
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
        # Notice we include 'client_institution' even though it’s not a model field.
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