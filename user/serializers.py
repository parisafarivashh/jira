from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Member


class MemberDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'title', 'email', 'phone']


class MemberRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'title', 'email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        member = Member.objects.create_user(
            title=validated_data['title'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password'],
        )
        return member


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, member):
        token = super().get_token(member)

        token['id'] = member.id
        token['title'] = member.title
        token['email'] = member.email
        token['phone'] = member.phone
        token['role'] = member.role
        return token

