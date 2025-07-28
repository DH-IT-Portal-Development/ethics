from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["pk", "fullname", "first_name", "last_name", "email"]

    fullname = serializers.CharField(source="get_full_name")


# redundant text with above, is it possible to override thhe fields?
class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["fullname", "first_name", "last_name"]

    fullname = serializers.CharField(source="get_full_name")
