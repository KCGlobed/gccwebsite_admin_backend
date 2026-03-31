from django.db import models

# Create your models here.



class CareerApplication(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    highest_qualification = models.CharField(max_length=255)
    employment_status = models.CharField(max_length=255)
    experience_years = models.CharField(max_length=50)
    area_of_interest = models.CharField(max_length=255)
    area_of_interest_other = models.CharField(max_length=255, blank=True, null=True)
    contribution_summary = models.TextField(blank=True, null=True)
    resume_path = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile = models.CharField(max_length=255, blank=True, null=True)
    notice_period = models.CharField(max_length=50)
    consent = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'career_application'



class PartnerWithUs(models.Model):
    organization_name = models.CharField(max_length=255)
    year_of_establishment = models.CharField(max_length=10)
    organization_type = models.CharField(max_length=255)
    organization_type_other = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    interests = models.JSONField()
    description = models.TextField()
    value_add = models.TextField()
    declaration = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'partner_with_us'




class NewsletterSubscribers(models.Model):
    email = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'newsletter_subscribers'


class SourceType(models.IntegerChoices):
    Website = 1, 'Website'
    Efos = 2, 'Efos'
    Affiliate1 = 3, 'Affiliate1'
    Affiliate2 = 4, 'Affiliate2'
    Affiliate3 = 5, 'Affiliate3'
    Affiliate4 = 6, 'Affiliate4'
    Affiliate5 = 7, 'Affiliate5'
    IPUniversity = 8, 'IPUniversity'
    DelhiUniversity = 9, 'DelhiUniversity'
    CCS = 10, 'CCS'
    Kuk = 11, 'Kuk'
    Vsl = 12, 'Vsl'

class SourceFormType(models.IntegerChoices):
    ApplyNow = 1, 'ApplyNow'
    Dossier = 2, 'Dossier'
    Program = 3, 'Program'




class DossierData(models.Model):
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    source = models.IntegerField(choices=SourceType.choices,default=SourceType.Website)
    source_form = models.IntegerField(choices=SourceFormType.choices,default=SourceFormType.ApplyNow)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    # Added for VSL
    degree = models.CharField(max_length=50, blank=True, null=True)
    degree_stage = models.CharField(max_length=50, blank=True, null=True)


class SupportForm(models.Model):
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

