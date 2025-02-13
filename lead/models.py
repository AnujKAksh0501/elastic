from django.db import models
from django.utils.translation import gettext as _
import random
import string
from core.models import *

def code_generator():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    if Lead.objects.filter(unique_code=key).exists():
        key = code_generator()
    elif Contact.objects.filter(unique_code=key).exists():
        key = code_generator()
    return key

class Lead(models.Model):
    visitor_ip = models.CharField(max_length=255, null=True, blank=True)
    visitor_id = models.CharField(max_length=255, null=True, blank=True)
    visit_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    part = models.CharField(max_length=255, null=True, blank=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    type = models.CharField(max_length=255, default="Inbound")
    is_premium = models.CharField(max_length=255, default="No")
    status = models.CharField(max_length=255, default="New")
    date = models.CharField(max_length=255, null=True, blank=True)
    time = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    unique_code = models.CharField(max_length=255, default = code_generator, editable=False)
    status = models.CharField(max_length=255, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Sent(models.Model):
    message_id = models.CharField(max_length=255, null=True, blank=True)
    lead_id = models.CharField(max_length=255, null=True, blank=True)
    to_email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    time = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

