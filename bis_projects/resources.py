from import_export import resources, fields
from .models import Project, Sample, SequencingRun
import re
from django.core.exceptions import ValidationError
from import_export.widgets import ManyToManyWidget

def get_project_from_code(project_code):
    """
    Look up a Project instance by its project_id.
    Raises a ValidationError if not found.
    """
    try:
        return Project.objects.get(project_id=project_code)
    except Project.DoesNotExist:
        raise ValidationError(f"Project with code '{project_code}' does not exist.")

def sanitize_sample_name(name):
    """
    Sanitize the sample name by replacing any non-alphanumeric character
    (excluding underscores) with an underscore. Then, compress multiple underscores.
    """
    # Replace one or more non-word characters with an underscore.
    sanitized = re.sub(r'\W+', '_', name)
    # Compress multiple underscores to one.
    sanitized = re.sub(r'_+', '_', sanitized)
    # Optionally remove leading/trailing underscores.
    sanitized = sanitized.strip('_')
    return sanitized

class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project

"""class SampleResource(resources.ModelResource):
    class Meta:
        model = Sample """

class SeqRunResource(resources.ModelResource):
    class Meta:
        model = SequencingRun

"""class SampleResource(resources.ModelResource):
    class Meta:
        model = Sample"""

class SampleResource(resources.ModelResource):
    # Override the field for the many-to-many relationship.
    # Assume the CSV header is 'project' (singular) even though the model field is 'projects'.
    projects = fields.Field(
        column_name='project',  # change this to 'projects' if your CSV header is 'projects'
        attribute='projects',
        widget=ManyToManyWidget(Project, field='project_id', separator=',')
    )

    class Meta:
        model = Sample
        # Specify the fields you want to import/export if needed.
        # For example:
        # fields = ('id', 'client_sample_name', 'projects', 'barcode', ...)

    def before_import_row(self, row, **kwargs):
        # If you want to additionally sanitize the sample name, do it here.
        client_sample_name = row.get('client_sample_name')
        if client_sample_name:
            row['client_sample_name'] = sanitize_sample_name(client_sample_name)

"""def before_import_row(self, row, **kwargs):
    # Process the project field.
    project_codes = row.get('projects')  # Ensure this key matches your CSV header.
    if project_codes:
        try:
            codes = [code.strip() for code in project_codes.split(',')]
            pks = []
            for code in codes:
                try:
                    project = get_project_from_code(code)
                except ValidationError as e:
                    raise e  # You can handle this differently if needed
                pks.append(str(project.pk))
            # ManyToMany fields in django-import-export expect a comma‐separated list of IDs
            row['projects'] = ','.join(pks)
        except Exception as e:
            # Optionally handle or log the error
            raise e

    # Process and sanitize the client sample name.
    client_sample_name = row.get('client_sample_name')
    if client_sample_name:
        row['client_sample_name'] = sanitize_sample_name(client_sample_name)"""

"""def before_import_row(self, row, **kwargs):
    # Process the project field.
    project_codes = row.get('projects')  # Ensure this key matches your CSV header.
    if project_codes:
        try:
            codes = [code.strip() for code in project_codes.split(',')]
            pks = []
            for code in codes:
                try:
                    project = get_project_from_code(code)
                except ValidationError as e:
                    raise e
                pks.append(str(project.pk))
            # ManyToMany fields in django-import-export expect a comma‐separated list of IDs
            row['projects'] = ','.join(pks)

        client_sample_name = row.get('client_sample_name')
        if client_sample_name:
            row['client_sample_name'] = sanitize_sample_name(client_sample_name)"""

"""class SampleResource(resources.ModelResource):
    class Meta:
        model = Sample
        # list the fields you want to import/export or let it default.
        # For example:
        # fields = ('id', 'client_sample_name', 'project', ...)

    def before_import_row(self, row, **kwargs):

        This method is called for each row before it is imported.
        Use it to validate and clean the data.

        # Process the project field.
        # Adjust the key ('project') to match the CSV header name.
        project_code = row.get('project')
        if project_code:
            try:
                project = get_project_from_code(project_code)
            except ValidationError as e:
                # You can either raise an error to stop the import
                # or handle it (e.g., log it, skip the row, etc.).
                raise e
            # Replace the project code with the project primary key (or whatever is needed).
            row['project'] = project.pk

        # Process and sanitize the client sample name.
        # Adjust 'client_sample_name' to the CSV header as needed.
        client_sample_name = row.get('client_sample_name')
        if client_sample_name:
            row['client_sample_name'] = sanitize_sample_name(client_sample_name)"""