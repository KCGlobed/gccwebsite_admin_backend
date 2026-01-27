# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


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
        managed = False
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
    student_reach = models.CharField(max_length=255)
    consent = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'campus_student'


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
        managed = False
        db_table = 'career_application'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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
        managed = False
        db_table = 'partner_with_us'


class Payments(models.Model):
    student = models.ForeignKey('StudentsData', models.DO_NOTHING)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'


class StudentDocuments(models.Model):
    student_id = models.IntegerField()
    document_type = models.CharField(max_length=50)
    file_name = models.CharField(max_length=255)
    gcs_path = models.TextField()
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    status2 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_documents'


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
        managed = False
        db_table = 'student_enquiries'


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
        managed = False
        db_table = 'students_data'


class UsersUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    uid = models.UUIDField(unique=True, blank=True, null=True)
    role = models.SmallIntegerField(blank=True, null=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    social_id = models.CharField(max_length=255, blank=True, null=True)
    social_type = models.CharField(max_length=20)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255)
    phone1 = models.CharField(max_length=100, blank=True, null=True)
    phone2 = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    pincode = models.CharField(max_length=120, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    lastlogin = models.BigIntegerField()
    current_refresh = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()
    is_admin = models.BooleanField()
    date_joined = models.DateTimeField()
    failed_login_attempts = models.IntegerField()
    locked_until = models.DateTimeField(blank=True, null=True)
    unlocked_on = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField()
    email_verified = models.IntegerField(blank=True, null=True)
    image = models.CharField(max_length=100, blank=True, null=True)
    banner_image = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users_user'


class UsersUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_groups'
        unique_together = (('user', 'group'),)


class UsersUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_user_permissions'
        unique_together = (('user', 'permission'),)



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
    student_reach = models.CharField(max_length=255)
    consent = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'campus_student'


