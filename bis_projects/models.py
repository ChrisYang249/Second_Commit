from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

"""

# Optionally, you can separate client and institution information
class ClientInstitution(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    #contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=255)
    #institution = models.ForeignKey(ClientInstitution, on_delete=models.CASCADE, related_name='clients')

    contact_email = models.EmailField(blank=True, null=True)
    def __str__(self):
        return self.name
"""
class Client(models.Model):
    name = models.CharField(max_length=255)
    institution = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Enter the client institution name (e.g., Example University)"
    )
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.institution or self.name

class Project(models.Model):

    project_id_validator = RegexValidator(
    regex=r'^(?=.*[-_])[A-Za-z0-9_-]+$',
    message=(
        "Project ID must contain only letters, digits, underscores, and dashes, "
        "must include at least one underscore, and cannot contain whitespace. "
        )
    )

    project_id = models.CharField(
        max_length=40, 
        unique=True,
        validators=[project_id_validator],
        help_text="Enter a project ID (e.g., CP00001).",
        null=True,
        blank=True,
        #default="TEMP00000"  # or some default value
    )

    SERVICE_CHOICES = [('16s v1v3','16s v1v3'),
                       ('16s v3v4','16s v3v4'),
                       ('16s v1v8','16s v1v8'),
                       ('WGS','WGS'),
                       ('ITS','ITS'),
                       ('Isolate - SR','Isolate - SR'),
                       ('Isolate - LR','Isolate - LR'),
                       ('Isolate - Hyb','Isolate - Hyb'),
                       ('Raw Data','Raw Data'),
                       ('Kits','Kits'),
                       ('Analysis Only', 'Analysis Only'),
                       ]
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    due_date = models.DateField()
    service_type = models.CharField(max_length=15, choices=SERVICE_CHOICES, null=True, blank=True)
    delivery_method = models.CharField(max_length=100)
    deliverables = models.TextField()
    samples_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default='active')
    analyst = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')

    def __str__(self):
        return f"Project for {self.client.name} due {self.due_date}"

STATUS_CHOICES = [
    ('LAB', 'LAB'),
    ('Sequencing', 'Sequencing'),
    ('RESEQ', 'RESEQ'),
    ('Seq_Complete', 'Seq Complete'),
    ('Ready', 'Ready'),
    ('FAIL', 'FAIL'),
]
class Sample(models.Model):
    projects = models.ManyToManyField(Project, related_name='samples')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='samples')
    barcode = models.CharField(max_length=100, unique=True)
    client_sample_name = models.CharField(max_length=100)
    sample_type = models.CharField(max_length=100)
    
    # Extraction details
    extraction_quant = models.FloatField(help_text="Quantity measured during extraction")
    extraction_kit = models.CharField(max_length=100)
    
    # Library prep details
    library_quant = models.FloatField(help_text="Quantity measured during library prep")
    library_kit = models.CharField(max_length=100)
    
    # Sequencing details
    targeted_depth = models.IntegerField(help_text="Targeted sequencing depth")
    #status = models.CharField(max_length=50, default="pending")
    sample_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='LAB'
    )
    def __str__(self):
        return f"Sample {self.barcode} ({self.client_sample_name})"

SEQUENCER_CHOICES = [
    ('Aviti', 'Aviti'),
    ('Nova_X', 'Nova_X'),
    ('MiSeq', 'MiSeq'),
    ('Nova_6k', 'Nova_6k'),
    ('ONT_GRID', 'ONT_GRID'),
    ('ONT_PRO', 'ONT_PRO'),
]

class SequencingRun(models.Model):
    run_name = models.CharField(max_length=10, unique=True, null=False, default="")
    instrument = models.CharField(max_length=8, choices=SEQUENCER_CHOICES, null=False, blank=False)
    qc_status = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="pending")
    samples = models.ManyToManyField(Sample, related_name='sequencing_runs')
    external_run_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.run_name} ({self.instrument}) - {self.qc_status}"
