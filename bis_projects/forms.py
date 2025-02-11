from django import forms
from .models import Sample, Project, STATUS_CHOICES
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

class BulkStatusForm(forms.Form):
    # This hidden field will store the IDs of the selected objects.
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    # A choice field for the new status.
    sample_status = forms.ChoiceField(choices=STATUS_CHOICES, label="New Status", help_text="Select the new status for the selected samples.",initial="LAB", widget=forms.Select(attrs={'class': 'vSelect', 'data-default': 'LAB'})
    )

    def __init__(self, *args, **kwargs):
        # If the form is unbound or no 'status' value is provided in initial data,
        # force the initial value to 'LAB'.
        if 'data' not in kwargs or not kwargs['data']:
            initial = kwargs.get('initial', {})
            if 'status' not in initial:
                initial['status'] = 'LAB'
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

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
    """
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=FilteredSelectMultiple("Projects", is_stacked=False)
    )
    """
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
