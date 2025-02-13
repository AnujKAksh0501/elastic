from rest_framework import serializers
from .models import *

class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CompanyLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companylead
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class GroupMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groupmail
        fields = '__all__'

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = '__all__'

class ForgotPasswordSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()

    class Meta:
        model = User
        fields='__all__'

    def updated(self):
        email=self.validated_data['email']
        if User.objects.filter(username=email).exists():
            user=User.objects.get(username=email)
            return user
        else:
            raise serializers.ValidationError({'error':'Please enter valid email'})

