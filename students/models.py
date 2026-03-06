from django.db import models

# Create your models here.



class StudentEnquiries(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20)
    email = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    graduation_program = models.CharField(max_length=255, blank=True, null=True)
    graduation_program_other = models.CharField(max_length=255, blank=True, null=True)
    graduation_status = models.CharField(max_length=255, blank=True, null=True)
    current_cgpa = models.CharField(max_length=255, blank=True, null=True)
    first_division = models.CharField(max_length=255, blank=True, null=True)
    college = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'student_enquiries'




class StudentDocuments(models.Model):
    student_id = models.IntegerField()
    document_type = models.CharField(max_length=50)
    file_name = models.CharField(max_length=255)
    gcs_path = models.TextField()
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'student_documents'



class StudentsData(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_mobile = models.CharField(max_length=20, blank=True, null=True)
    father_email = models.CharField(max_length=150, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_mobile = models.CharField(max_length=20, blank=True, null=True)
    mother_email = models.CharField(max_length=150, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    class10_year = models.IntegerField(blank=True, null=True)
    class10_score = models.FloatField(blank=True, null=True)
    class12_year = models.IntegerField(blank=True, null=True)
    class12_score = models.FloatField(blank=True, null=True)
    medium_of_instruction = models.CharField(max_length=50, blank=True, null=True)
    medium_other = models.CharField(max_length=100, blank=True, null=True)
    ug_status = models.CharField(max_length=20, blank=True, null=True)
    first_division = models.BooleanField(blank=True, null=True)
    ug_cgpa = models.FloatField(blank=True, null=True)
    ug_institution = models.CharField(max_length=200, blank=True, null=True)
    pg_exists = models.BooleanField(blank=True, null=True)
    pg_type = models.CharField(max_length=50, blank=True, null=True)
    pg_other = models.CharField(max_length=100, blank=True, null=True)
    pg_institution = models.CharField(max_length=200, blank=True, null=True)
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    university = models.CharField(max_length=200, blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    work_experience = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'students_data'



class FormType(models.IntegerChoices):
    Payment = 1, 'Payment'
    Dossier = 2, 'Dossier'


class Payments(models.Model):
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    #Added type for form specification
    form_type = models.IntegerField(choices=FormType.choices, default=FormType.Payment)
    form_id   = models.CharField(max_length=50, blank=True, null=True)
    dossier_form = models.ForeignKey('career.DossierData', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'payments'




#### >>>>>>>>>>>>>>>>>>>>>> #### >>>>>>>>>>>>>>>>>>>>>>>> #### >>>>>>>>>>>>>>>>>>>>>>>....




class CampusFaculty(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address = models.TextField()
    institution_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    teaching_experience = models.CharField(max_length=50)
    industrial_experience = models.CharField(max_length=255, blank=True, null=True)
    highest_qualification = models.CharField(max_length=255)
    motivation = models.TextField()
    support_activities = models.JSONField()
    student_reach = models.CharField(max_length=255)
    consent = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'campus_faculty'


class CampusStudent(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address = models.TextField()
    college_name = models.CharField(max_length=255)
    program_of_study = models.CharField(max_length=255)
    program_other = models.CharField(max_length=255, blank=True, null=True)
    semester = models.CharField(max_length=255)
    student_body_member = models.CharField(max_length=255)
    campus_ambassador_history = models.CharField(max_length=255)
    inspiration = models.TextField()
    promotion_channels = models.JSONField()
    student_reach = models.CharField(max_length=255) ## remove field from system using default values
    consent = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    #added
    student_body_description = models.TextField(blank=True)
    campus_ambassador_description = models.TextField(blank=True)


    class Meta:
        db_table = 'campus_student'


class ContactUs(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta:
        verbose_name = 'Quick Contact'
        verbose_name_plural = 'Quick Contact'
        
    def __str__(self):
        return '%s' % self.id