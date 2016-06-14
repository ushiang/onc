from django.db import models

from packages.organizations.models import Organization
from packages.products_services.models import Service
from packages.mda.models import Mda
from packages.rfp.models import Rfp, Job

class Rfp(models.Model):
    services = models.ManyToManyField(Service, models.DO_NOTHING)
    mda = models.ForeignKey(Mda, models.DO_NOTHING)

class Job(models.Model):
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    rfp = models.ForeignKey(Rfp, models.DO_NOTHING)
    rating = models.IntegerField()
    review = models.CharField(max_length=256)
    certificate_tag = models.FilePathField()

class Proposal(models.Model):
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    rfp = models.ForeignKey(Rfp, models.DO_NOTHING)
    industry = models.CharField(64)
    capitalization = models.DecimalField()
    annual_turnover = models.DecimalField()
    tax_clearance_year = models.IntegerField()
    nitdev_payment_evidence_amnt = models.FilePathField() #document
    itf_payment_evidence = models.FilePathField()
    pension_certificates = models.FilePathField()
    sector = models.CharField(64)
    relevant_job = models.ManyToManyField(Job, models.DO_NOTHING)
    membership_certificates = models.FilePathField()

class Billing(models.Model):
    job = models.ForeignKey(Job, models.DO_NOTHING)
    amount = models.DecimalField()
    date_billed = models.DateTimeField()
    commission = models.DecimalField()

