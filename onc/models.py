from django.db import models

class authuser(models.model):
    password = models.charfield(max_length=128)
    last_login = models.datetimefield()
    is_superuser = models.booleanfield()
    # username = models.charfield(unique=true, max_length=30)
    first_name = models.charfield(max_length=30)
    last_name = models.charfield(max_length=30)
    email = models.charfield(unique=True, max_length=75)
    is_active = models.booleanfield()
    date_joined = models.datetimefield()


class service(models.model):
    title = models.charfield(unique=True, max_length=75)

class skill(models.model):
    title = models.charfield(unique=True, max_length=75)

class organization(models.model):
    name = models.charfield(max_length=128)
    address = models.charfield(max_length=200)
    tin_number = models.charfield(max_length=64) #tax number
    number_of_staff = models.integerfield()
    phone_number = models.charfield(32)
    services = models.manytomanyfield(service, models.do_nothing)


class professional(models.model):
    user = models.onetoonefield(authuser, models.do_nothing)
    organizations = models.manytomanyfield(organization, models.do_nothing)
    skills = models.manytomanyfield(skill, models.do_nothing)
    location = models.charfield(max_length=64) # one of 36 states
    phone_number = models.charfield(32)
    institution =  models.charfield(64)


class mda(models.model):
    name = models.charfield(unique=True, max_length=75)
    user = models.onetoonefield(authuser, models.do_nothing)
    phone_number = models.charfield(32)

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

