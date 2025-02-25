from django.db import models
from django.utils.translation import gettext as _
import random
import string

def code_generator():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    if Sitevisitor.objects.filter(visitor_id=key).exists():
        key = code_generator()
    elif Sitevisit.objects.filter(visit_id=key).exists():
        key = code_generator()
    return key

class Sitevisitor(models.Model):
    visitor_ip = models.CharField(max_length=255, null=True, blank=True)
    visitor_id = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    device = models.CharField(max_length=255, null=True, blank=True)
    device_brand = models.CharField(max_length=255, null=True, blank=True)
    device_model = models.CharField(max_length=255, null=True, blank=True)
    device_screen = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, null=True, blank=True)
    platform_version = models.CharField(max_length=255, null=True, blank=True)
    browser = models.CharField(max_length=255, null=True, blank=True)
    browser_engine = models.CharField(max_length=255, null=True, blank=True)
    browser_configuration = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    continent = models.CharField(max_length=255, null=True, blank=True)
    continent_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    region_code = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    lat = models.CharField(max_length=255, null=True, blank=True)
    lon = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    dialing_code = models.CharField(max_length=10, blank=True, null=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

class Sitevisit(models.Model):
    visitor = models.ForeignKey(Sitevisitor, on_delete=models.CASCADE, null=True, blank=True)
    visitor_ip = models.CharField(max_length=255, null=True, blank=True)
    visit_id = models.CharField(max_length=255, unique=True, default = code_generator, editable=False)
    visited_url = models.TextField(null=True, blank=True)
    visit_time_spent = models.EmailField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)
