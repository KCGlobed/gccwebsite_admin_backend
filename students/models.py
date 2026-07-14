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
    ARC = 14, 'ARC'
    Affiliate7 = 15, 'Affiliate7'
    CPA = 16, 'CPA'
    EA = 17, 'EA'
    EAWebsite = 18, 'EAWebsite'

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
    source = models.IntegerField(choices=SourceType.choices,default=SourceType.Website, null=True)
    re_attempt_status = models.BooleanField(default=False)
    fee_waiver_category = models.CharField(max_length=200, default="No Waiver")

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
    student_body_description = models.TextField(blank=True, null=True)
    campus_ambassador_description = models.TextField(blank=True, null=True)
    mail_status = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)



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
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us'
        
    def __str__(self):
        return '%s' % self.id



class EmployementStatus(models.IntegerChoices):
    FRESHER = 1, 'FRESHER'
    EXPERIENCED = 2, 'EXPERIENCED'

class HigherEducation(models.IntegerChoices):
    YES = 1, 'YES'
    NO = 2, 'NO'

class PGStatus(models.IntegerChoices):
    COMPLETED = 1, 'COMPLETED'
    PURSURING = 2, 'PURSURING'

class Medium(models.IntegerChoices):
    ENGLISH = 1, 'ENGLISH'
    HINDI = 2, 'HINDI'
    OTHER = 3, 'OTHER'

class Gender(models.IntegerChoices):
    MALE = 1, 'MALE'
    FEMALE = 2, 'FEMALE'
    OTHER = 3, 'OTHER'


class AccountingProfession(models.IntegerChoices):
    SELF = 1, 'SELF'
    LOAN = 2, 'LOAN'

class Profession(models.IntegerChoices):
    SALARIED = 1, 'SALARIED'
    SELFEMP = 2, 'SELFEMP'
    AGRICULTURE = 3, 'AGRICULTURE'

class Guardian(models.IntegerChoices):
    SELECT = 0, 'SELECT'
    MOTHER = 1, 'MOTHER'
    FATHER = 2, 'FATHER'
    OTHER  = 3, 'OTHER'


###################


class StudentProfileDraft(models.Model):
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.IntegerField(choices=Gender.choices,default=Gender.MALE, null=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    tenth_passing_year = models.CharField(max_length=255, null=True, blank=True)
    tenth_passing_percentage = models.CharField(max_length=255, null=True, blank=True)
    twelveth_passing_year = models.CharField(max_length=255, null=True, blank=True)
    twelveth_passing_percentage = models.CharField(max_length=255, null=True, blank=True)
    medium_instruction = models.IntegerField(choices=Medium.choices,default=Medium.ENGLISH)
    other_instruction = models.CharField(max_length=255, null=True, blank=True)
    pg_status = models.IntegerField(choices=PGStatus.choices,default=PGStatus.COMPLETED)
    pg_percentage = models.CharField(max_length=255, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    higher_education_status = models.IntegerField(choices=HigherEducation.choices,default=HigherEducation.YES)
    higher_qualification = models.CharField(max_length=255, null=True, blank=True)
    higher_qualification_institution = models.CharField(max_length=255, null=True, blank=True)
    employement_status = models.IntegerField(choices=EmployementStatus.choices,default=EmployementStatus.FRESHER)
    aadhaar = models.FileField(blank=False, null=False)
    dob_certificate = models.FileField(blank=False, null=False)
    photo = models.FileField(blank=False, null=False)
    signature = models.FileField(blank=False, null=False)
    profile_status = models.BooleanField(default=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    #added
    slot_date = models.DateField(null=True, blank=True)
    slot_time = models.CharField(max_length=200, blank=True, null=True)
    slot_update_count = models.IntegerField(default=0)
    tenth_score_type = models.CharField(max_length=20, blank=True, null=True)
    tenth_medium = models.IntegerField(choices=Medium.choices,default=Medium.ENGLISH)
    twelveth_score_type = models.CharField(max_length=20, blank=True, null=True)
    twelveth_medium = models.IntegerField(choices=Medium.choices,default=Medium.ENGLISH)
    ug_score_type = models.CharField(max_length=20, blank=True, null=True)
    mock_test_status = models.IntegerField(default=0, null=True)
    re_attempt = models.IntegerField(default=0, null=True)
    re_attempt_btn = models.IntegerField(default=0, null=True)
    application_id = models.CharField(max_length=200, blank=True, null=True)
    fee_waiver_category = models.CharField(max_length=200, default="No Waiver")
    # Added
    resume = models.FileField(blank=True, null=True)
    resume_key_status = models.BooleanField(default=False)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=100, blank=True, null=True)
    guardian_email = models.CharField(max_length=100, blank=True, null=True)
    guardian_dropdown = models.IntegerField(choices=Guardian.choices, blank=True, null=True)
    guardian_other_reason = models.CharField(max_length=100, blank=True, null=True)
    guardian_key_status = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Student Profile Draft'
        verbose_name_plural = 'Student Profile Draft'
        
    def __str__(self):
        return '%s' % self.id
    

class StudentExperienceDraft(models.Model):
    student_profile = models.ForeignKey('StudentProfileDraft', null=True, blank=True, on_delete=models.CASCADE)
    position = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'User Experience Draft'
        verbose_name_plural = 'User Experience Draft'

    def __str__(self):
        return '%s' % self.id





###################

class StudentProfile(models.Model):
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.IntegerField(choices=Gender.choices,default=Gender.MALE)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    tenth_passing_year = models.CharField(max_length=255, null=True, blank=True)
    tenth_passing_percentage = models.CharField(max_length=255, null=True, blank=True)
    twelveth_passing_year = models.CharField(max_length=255, null=True, blank=True)
    twelveth_passing_percentage = models.CharField(max_length=255, null=True, blank=True)
    medium_instruction = models.IntegerField(choices=Medium.choices,default=Medium.ENGLISH)
    other_instruction = models.CharField(max_length=255, null=True, blank=True)
    pg_status = models.IntegerField(choices=PGStatus.choices,default=PGStatus.COMPLETED)
    pg_percentage = models.CharField(max_length=255, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    higher_education_status = models.IntegerField(choices=HigherEducation.choices,default=HigherEducation.YES)
    higher_qualification = models.CharField(max_length=255, null=True, blank=True)
    higher_qualification_institution = models.CharField(max_length=255, null=True, blank=True)
    employement_status = models.IntegerField(choices=EmployementStatus.choices,default=EmployementStatus.FRESHER)
    aadhaar = models.FileField(blank=False, null=False)
    dob_certificate = models.FileField(blank=False, null=False)
    photo = models.FileField(blank=False, null=False)
    signature = models.FileField(blank=False, null=False)
    profile_status = models.BooleanField(default=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    #added
    slot_date = models.DateField(null=True, blank=True)
    slot_time = models.CharField(max_length=200, blank=True, null=True)
    slot_update_count = models.IntegerField(default=0)
    tenth_score_type = models.CharField(max_length=20, blank=True, null=True)
    tenth_medium = models.IntegerField(choices=Medium.choices,default=Medium.ENGLISH)
    twelveth_score_type = models.CharField(max_length=20, blank=True, null=True)
    twelveth_medium = models.IntegerField(choices=Medium.choices,default=Medium.ENGLISH)
    ug_score_type = models.CharField(max_length=20, blank=True, null=True)
    mock_test_status = models.IntegerField(default=0, null=True)
    re_attempt = models.IntegerField(default=0, null=True)
    re_attempt_btn = models.IntegerField(default=0, null=True)
    application_id = models.CharField(max_length=200, blank=True, null=True)
    fee_waiver_category = models.CharField(max_length=200, default="No Waiver")
    # Added
    resume = models.FileField(blank=True, null=True)
    resume_key_status = models.BooleanField(default=False)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=100, blank=True, null=True)
    guardian_email = models.CharField(max_length=100, blank=True, null=True)
    guardian_dropdown = models.IntegerField(choices=Guardian.choices, blank=True, null=True)
    guardian_other_reason = models.CharField(max_length=100, blank=True, null=True)
    guardian_key_status = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profile'
        
    def __str__(self):
        return '%s' % self.id
    

class StudentExperience(models.Model):
    student_profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    position = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'User Experience'
        verbose_name_plural = 'User Experience'

    def __str__(self):
        return '%s' % self.id



class StudentSlotBooking(models.Model):
    student_profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    slot_date = models.DateField(null=True, blank=True)
    slot_time = models.CharField(max_length=200, blank=True, null=True)
    slot_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'User Slot Booking'
        verbose_name_plural = 'User Slot Booking'

    def __str__(self):
        return '%s' % self.id


class StudentExamResult(models.Model):
    student_profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=250, null=True, blank=True)
    testid = models.CharField(max_length=250, null=True, blank=True)
    starttime = models.CharField(max_length=250, null=True, blank=True)
    endtime = models.CharField(max_length=250, null=True, blank=True)
    timetaken = models.CharField(max_length=250, null=True, blank=True)
    totalscore = models.CharField(max_length=250, null=True, blank=True)
    totalquestionsattempted = models.CharField(max_length=250, null=True, blank=True)
    totalcorrectanswers = models.CharField(max_length=250, null=True, blank=True)
    totalquestions = models.CharField(max_length=250, null=True, blank=True)
    json_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Student Exam Result'
        verbose_name_plural = 'Student Exam Result'

    def __str__(self):
        return '%s' % self.id



class StudentRealExamResult(models.Model):
    student_profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=250, null=True, blank=True)
    testid = models.CharField(max_length=250, null=True, blank=True)
    starttime = models.CharField(max_length=250, null=True, blank=True)
    endtime = models.CharField(max_length=250, null=True, blank=True)
    timetaken = models.CharField(max_length=250, null=True, blank=True)
    totalscore = models.CharField(max_length=250, null=True, blank=True)
    totalquestionsattempted = models.CharField(max_length=250, null=True, blank=True)
    totalcorrectanswers = models.CharField(max_length=250, null=True, blank=True)
    totalquestions = models.CharField(max_length=250, null=True, blank=True)
    json_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Student Real Exam Result'
        verbose_name_plural = 'Student Real Exam Result'

    def __str__(self):
        return '%s' % self.id




class ExamMasterKey(models.Model):
    key = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Exam Master Key'
        verbose_name_plural = 'Exam Master Key'

    def __str__(self):
        return '%s' % self.id
    


class ManageMasterKey(models.Model):
    profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    key  = models.ForeignKey('ExamMasterKey', null=True, blank=True, on_delete=models.CASCADE)
    exam_url   = models.TextField(blank=True, null=True)
    status     = models.BooleanField(default=False)
    reattempt_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Manage Master Key'
        verbose_name_plural = 'Manage Master Key'

    def __str__(self):
        return '%s' % self.id



class ResultStatusType(models.IntegerChoices):
    Selected = 1, 'Selected'
    NotSelected = 2, 'Not Selected'
    
class AttendanceStatusType(models.IntegerChoices):
    Present = 1, 'Present'
    Absent = 2, 'Absent'


class CompanyMaster(models.Model):
    name       = models.TextField(blank=True, null=True)
    status     = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Company Master'
        verbose_name_plural = 'Company Master'

    def __str__(self):
        return '%s' % self.id

class ManageStudentInterview(models.Model):
    profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    company   = models.ForeignKey('CompanyMaster', null=True, blank=True, on_delete=models.CASCADE)
    attempt_status = models.IntegerField(choices=AttendanceStatusType.choices, null=True, blank=True)
    absent_reason = models.TextField(null=True, blank=True)
    result = models.IntegerField(choices=ResultStatusType.choices, null=True, blank=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.CharField(max_length=200, null=True, blank=True)
    package_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    payment_amount = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Manage Student Interview'
        verbose_name_plural = 'Manage Student Interview'

    def __str__(self):
        return '%s' % self.id


class ManageStudentInterviewHistory(models.Model):
    profile = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    company   = models.ForeignKey('CompanyMaster', null=True, blank=True, on_delete=models.CASCADE)
    attempt_status = models.IntegerField(choices=AttendanceStatusType.choices, null=True, blank=True)
    absent_reason = models.TextField(null=True, blank=True)
    result = models.IntegerField(choices=ResultStatusType.choices, null=True, blank=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.CharField(max_length=200, null=True, blank=True)
    package_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    payment_amount = models.CharField(max_length=200, null=True, blank=True)
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Manage Student Interview History'
        verbose_name_plural = 'Manage Student Interview History'

    def __str__(self):
        return '%s' % self.id


class StudentPayment(models.Model):
    student = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    currency = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = 'Student Payment'



##### Logs maintain for appplication #####

class ApplicationLog(models.Model):
    application = models.ForeignKey('StudentProfile', null=True, blank=True, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.IntegerField(default=0)
    activity = models.CharField(max_length=200, null=True, blank=True)
    datas = models.TextField(blank=True, null=True)
    payload_request = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)





