from django.db import models
from django.utils.translation import gettext as _
import random
import string

def id_generator():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    if Site_visitor.objects.filter(unique_code=key).exists():
        key = id_generator()
    return key

class Site_visitor(models.Model):
    url = models.CharField(max_length=255, null=True, blank=True)
    visitor_id = models.CharField(max_length=255, unique=True, default = id_generator, editable=False)
    visitor_ip = models.CharField(max_length=255, null=True, blank=True)
    visitor_local_time = models.CharField(max_length=255, null=True, blank=True)
    visitor_time_spent = models.CharField(max_length=255, null=True, blank=True)
    visitor_visit_count = models.CharField(max_length=255, null=True, blank=True)
    visitor_call_action = models.CharField(max_length=255, null=True, blank=True)
    visitor_form_action = models.CharField(max_length=255, null=True, blank=True)
    visitor_returning = models.CharField(max_length=255, null=True, blank=True)
    visitor_browser_name = models.CharField(max_length=255, null=True, blank=True)
    visitor_client_type = models.CharField(max_length=255, null=True, blank=True)
    visitor_device_brand = models.CharField(max_length=255, null=True, blank=True)
    visitor_device_model = models.CharField(max_length=255, null=True, blank=True)
    visitor_device_type = models.CharField(max_length=255, null=True, blank=True)
    visitor_city = models.CharField(max_length=255, null=True, blank=True)
    visitor_country = models.CharField(max_length=255, null=True, blank=True)
    visitor_latitude = models.CharField(max_length=255, null=True, blank=True)
    visitor_longitude = models.CharField(max_length=255, null=True, blank=True)
    visitor_region = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)