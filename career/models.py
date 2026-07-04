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
    VslOptin = 12, 'VslOptin'
    VslFinal = 13, 'VslFinal'
    Affiliate6 = 14, 'Affiliate6'
    Affiliate7 = 15, 'Affiliate7'  ##akshay landing 2
    CPA = 16, 'CPA'
    EA = 17, 'EA'

class SourceFormType(models.IntegerChoices):
    ApplyNow = 1, 'ApplyNow'
    Dossier = 2, 'Dossier'
    Program = 3, 'Program'


class DocumentStatusType(models.IntegerChoices):
    Pending = 1, 'Pending'
    Approved = 2, 'Approved'
    Rejected = 3, 'Rejected'




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
    fbc_id = models.CharField(max_length=250, blank=True, null=True)
    utm_source = models.CharField(max_length=250, blank=True, null=True)
    utm_medium = models.CharField(max_length=250, blank=True, null=True)
    utm_content = models.CharField(max_length=250, blank=True, null=True)
    utm_campaign = models.CharField(max_length=250, blank=True, null=True)
    campaign_id = models.CharField(max_length=100, blank=True, null=True)
    utm_adname = models.CharField(max_length=250, blank=True, null=True)
    adset_id = models.CharField(max_length=250, blank=True, null=True)
    fbclid = models.CharField(max_length=250, blank=True, null=True)
    ad_source = models.CharField(max_length=250, blank=True, null=True)
    ad_id = models.CharField(max_length=250, blank=True, null=True)
    ## Added for university dropdown
    university = models.CharField(max_length=250, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    document_status = models.IntegerField(choices=DocumentStatusType.choices,default=DocumentStatusType.Pending)
    remarks_timestamp = models.DateTimeField(null=True, blank=True)
    fee_waiver_category = models.CharField(max_length=200, default="No Waiver")
    referred_code = models.CharField(max_length=50, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    #added for affliate 7
    interview_date = models.DateField(null=True, blank=True)

class DossierDocument(models.Model):
    dossier = models.ForeignKey('DossierData',on_delete=models.CASCADE,null=True,blank=True,related_name='documents')
    file = models.FileField(upload_to="career/images/",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document {self.id} - {self.dossier}"


## 
class VslDetail(models.Model):
    dossier = models.ForeignKey('DossierData', null=True, blank=True, on_delete=models.CASCADE)
    video_playback = models.IntegerField(default=0)  ## Seconds
    specialist_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


class SupportForm(models.Model):
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


class DossierAbondant(models.Model):
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    source = models.IntegerField(choices=SourceType.choices,default=SourceType.Website)
    source_form = models.IntegerField(choices=SourceFormType.choices,default=SourceFormType.ApplyNow)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    ## Added
    utm_source = models.CharField(max_length=250, blank=True, null=True)
    utm_medium = models.CharField(max_length=250, blank=True, null=True)
    utm_campaign = models.CharField(max_length=250, blank=True, null=True)
    




##### Logs maintain for dossier #####

class DossierLog(models.Model):
    dossier = models.ForeignKey('DossierData', null=True, blank=True, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.IntegerField(default=0)
    activity = models.CharField(max_length=200, null=True, blank=True)
    datas = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


