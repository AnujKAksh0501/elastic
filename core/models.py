from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext as _
import random
import string
import os
from uuid import uuid4

def code_generator():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    if User.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Company.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Companyemail.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Companylead.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Otp.objects.filter(code=key).exists():
        key = code_generator()
    elif Group.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Groupmail.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Website.objects.filter(unique_code=key).exists():
        key = code_generator()
    return key

def company_logo_rename(instance, filename):
    upload_to = 'companies'
    ext = filename.split('.')[-1]
    # get filename
    filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

class Otp(models.Model):
    email = models.EmailField(max_length=255, null=True, blank=True)
    mobile = models.EmailField(max_length=255, null=True, blank=True)
    otp = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    status = models.CharField(max_length=255, default='Unverified')
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class CustomUserManager(BaseUserManager):
    def create(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Account must have an email address'))

        email = self.normalize_email(email)

        user = self.model(
            email = email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_staffuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_online", False)
        return self.create(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_online", True)
        return self.create(email=email, password=password, **extra_fields)
    
class User(AbstractBaseUser):
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255, unique=True)
    unique_code = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    otp_enabled = models.CharField(max_length=255, default='Disabled')
    role = models.CharField(max_length=255, default='Admin')
    password_reset_code = models.CharField(max_length=255, null=True, blank=True)
    admin = models.EmailField(null=True, blank=True) # Admin
    added_by = models.EmailField(null=True, blank=True) # Added by
    updated_by = models.EmailField(null=True, blank=True) # Updated by
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
    
class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Owner
    group = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to=company_logo_rename, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    admin = models.EmailField(null=True, blank=True) # Admin
    added_by = models.EmailField(null=True, blank=True) # Added by
    updated_by = models.EmailField(null=True, blank=True) # Updated by
    status = models.CharField(max_length=255, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Companylead(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    assign = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Assign
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    part = models.CharField(max_length=255, null=True, blank=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    type = models.CharField(max_length=255, default="Inbound")
    is_premium = models.CharField(max_length=255, default="No")
    status = models.CharField(max_length=255, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Companyemail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    is_premium = models.CharField(max_length=255, default="No")
    status = models.CharField(max_length=255, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Country(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    short_code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    short_code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Group(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    filter = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    rule = models.JSONField(null=True, blank=True)
    unique_code = models.CharField(max_length=255, default = code_generator, editable=False)
    status = models.CharField(max_length=255, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Groupmail(models.Model):
    group = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, default = code_generator, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Website(models.Model):
    domain = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, default = code_generator, editable=False)
    status = models.CharField(max_length=255, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)
