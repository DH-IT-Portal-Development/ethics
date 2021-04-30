from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'fullname', 'first_name', 'last_name', 'email']

    fullname = serializers.CharField(source='get_full_name')
