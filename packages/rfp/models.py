from django.db import models

class rfp(models.model):
    services = models.manytomanyfield(service, models.do_nothing)
    mda = models.foreignkey(mda, models.do_nothing)

class job(models.model):
    organization = models.foreignkey(organization, models.do_nothing)
    rfp = models.foreignkey(rfp, models.do_nothing)
    rating = models.integerfield()
    review = models.charfield(max_length=256)
    certificate_tag = models.filepathfield()

class proposal(models.model):
    organization = models.foreignkey(organization, models.do_nothing)
    rfp = models.foreignkey(rfp, models.do_nothing)
    industry = models.charfield(64)
    capitalization = models.decimalfield()
    annual_turnover = models.decimalfield()
    tax_clearance_year = models.integerfield()
    nitdev_payment_evidence_amnt = models.filepathfield() #document
    itf_payment_evidence = models.filepathfield()
    pension_certificates = models.filepathfield()
    sector = models.charfield(64)
    relevant_job = models.manytomanyfield(job, models.do_nothing)
    membership_certificates = models.filepathfield()

class billing(models.model):
    job = models.foreignkey(job, models.do_nothing)
    amount = models.decimalfield()
    date_billed = models.datetimefield()
    commission = models.decimalfield()

