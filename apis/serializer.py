from rest_framework import serializers
from .models import *

class SiteVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitevisitor
        fields = '__all__'

class SiteVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitevisit
        fields = '__all__'

        