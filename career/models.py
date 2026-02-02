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


