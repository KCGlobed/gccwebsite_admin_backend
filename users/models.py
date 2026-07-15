import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager , AbstractBaseUser, PermissionsMixin
import re
import random
import string
from django.core.exceptions import ValidationError
from django.db import models
# from rolepermissions.roles import assign_role
# from gcc_backend.roles import *
# from django_softdelete.models import SoftDeleteModel

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, confirm_password=None, phone=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email.lower()),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_social_user(self, email, name, social_id, social_type):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email.lower()),
            first_name=name,
            last_name='',
        )
        user.social_id = social_id
        user.social_type = social_type
        user.set_password(social_id)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name,last_name, password=None):
        user = self.create_user(
            email.lower(),
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_admin = True
        user.role = User.SuperAdmin
        user.is_active = True
        user.email_verified = 1
        user.superuser_status = True
        user.save(using=self._db)
        # assign_role(user, "SuperAdmin")
        return user


class User(AbstractBaseUser, PermissionsMixin):

    SuperAdmin = 1
    SubAdmin = 2
    Manager = 3
    Student = 4
    Other = 5  ##ET users
    Efos = 6
    Vsl = 7
    AffliateOne = 8
    AffliateTwo = 9
    AffliateThree = 10
    AffliateFour = 11
    AffliateFive = 12
    AffliateSix = 13
    AffliateSeven = 14
    SalesHead = 15
    SalesPerson = 16


    ROLE_CHOICES = (
        (SuperAdmin, 'SuperAdmin'),
        (SubAdmin, 'SubAdmin'),
        (Manager, 'Manager'),
        (Student, 'Student'),
        (Other,'Other'),
        (Efos,'Efos'),
        (Vsl,'Vsl'),
        (AffliateOne, 'AffliateOne'),
        (AffliateTwo, 'AffliateTwo'),
        (AffliateThree, 'AffliateThree'),
        (AffliateFour,'AffliateFour'),
        (AffliateFive,'AffliateFive'),
        (AffliateSix,'AffliateSix'),
        (AffliateSeven,'AffliateSeven'),
        (SalesHead,'SalesHead'),
        (SalesPerson,'SalesPerson'),
    )

    SOCIAL_LOGIN_CHOICES = (
        ('Email', 'Email'),
        ('Google', 'Google'),
        ('Facebook', 'Facebook')
    )
    
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, blank=True, null=True, verbose_name='Public identifier')
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=3)
    reference_id = models.CharField(max_length=100, blank=True,null=True)
    social_id = models.CharField(max_length=255, blank=True,null=True)
    social_type = models.CharField(max_length=20, choices=SOCIAL_LOGIN_CHOICES, default='Email')
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True,null=True)
    last_name = models.CharField(max_length=100 ,blank=True,null=True)
    email = models.EmailField(max_length=255,unique=True)
    phone1 = models.CharField(max_length=100,blank=True,null=True)
    phone2 = models.CharField(max_length=100,blank=True,null=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    city = models.CharField(max_length=120,blank=True,null=True)
    state = models.CharField(max_length=120,blank=True,null=True)
    country = models.CharField(max_length=120,blank=True,null=True)
    pincode = models.CharField(max_length=120,blank=True,null=True)
    dob = models.DateField(blank=True, null=True)
    lastlogin = models.BigIntegerField(default=0)
    current_refresh = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    unlocked_on = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    email_verified = models.IntegerField(blank=True, null=True, default=0)
    image = models.ImageField(blank=True, null=True)
    banner_image = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    #Added
    application_id = models.CharField(max_length=50, blank=True, null=True)
    fee_waiver_category = models.CharField(max_length=200, default="No Waiver")
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    referred_code = models.CharField(max_length=50, null=True, blank=True)
    reporting_to = models.CharField(max_length=50,blank=True,null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'User'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def is_locked(self):
        if self.locked_until:
            return True
        return False

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
    



class ManageReferal(models.Model):
    user = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='referral_owner'
    )

    used_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='referral_used_by'
    )

    referral_code = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.referral_code



# def generate_referral_code(length=20):
#     return ''.join(random.choices(string.ascii_uppercase, k=length))
def generate_referral_code(length=6):
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length
        )
    )

class ManageFreeReferal(models.Model):
    free_referral_code = models.CharField(
        max_length=50,
        unique=True
    )
    code_length = models.IntegerField(default=20)
    non_auto = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.non_auto:
            # If user provides referral name
            if self.free_referral_code:

                # Take first name only
                first_name = self.free_referral_code.strip().split(" ")[0]

                # Remove special characters
                first_name = re.sub(r'[^A-Za-z0-9]', '', first_name)

                base_name = first_name.upper()

                if not base_name:
                    raise ValidationError(
                        "Referral code must contain valid alphabets or numbers."
                    )

                # Validation
                if len(base_name) >= self.code_length:
                    raise ValidationError(
                        f"First name length must be less than {self.code_length}"
                    )

                # Remaining length after "_"
                remaining_length = self.code_length - len(base_name) - 1

                random_code = generate_referral_code(
                    remaining_length
                )

                code = f"{base_name}_{random_code}"

                # Ensure unique code
                while ManageFreeReferal.objects.filter(
                    free_referral_code=code
                ).exclude(id=self.id).exists():

                    random_code = generate_referral_code(
                        remaining_length
                    )

                    code = f"{base_name}_{random_code}"

                self.free_referral_code = code

            else:
                # Fully random code
                code = generate_referral_code(self.code_length)

                while ManageFreeReferal.objects.filter(
                    free_referral_code=code
                ).exclude(id=self.id).exists():

                    code = generate_referral_code(
                        self.code_length
                    )

                self.free_referral_code = code

        super().save(*args, **kwargs)


    def __str__(self):
        return self.free_referral_code


##############################################################################


class ManageLoginForm(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=200, blank=True)
    cred = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ManageStudentExtraDetail(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    cred = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ManageReporting(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reporting_users'
    )

    reporting_to = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reports_received'
    )

    reporting_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reports_created'
    )

    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} -> {self.reporting_to}"


