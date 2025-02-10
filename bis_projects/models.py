from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

# Optionally, you can separate client and institution information
class ClientInstitution(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=255)
    institution = models.ForeignKey(ClientInstitution, on_delete=models.CASCADE, related_name='clients')

    def __str__(self):
        return self.name

class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    due_date = models.DateField()
    service_type = models.CharField(max_length=100)
    delivery_method = models.CharField(max_length=100)
    deliverables = models.TextField()
    samples_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default='active')
    analyst = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')

    def __str__(self):
        return f"Project for {self.client.name} due {self.due_date}"

class Sample(models.Model):
    projects = models.ManyToManyField(Project, related_name='samples')
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
    status = models.CharField(max_length=50, default="pending")

    def __str__(self):
        return f"Sample {self.barcode} ({self.client_sample_name})"

class SequencingRun(models.Model):
    instrument = models.CharField(max_length=100)
    qc_status = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="pending")
    samples = models.ManyToManyField(Sample, related_name='sequencing_runs')

    def __str__(self):
        return f"Sequencing Run on {self.instrument}"
