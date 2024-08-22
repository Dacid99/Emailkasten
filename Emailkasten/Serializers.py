from rest_framework import serializers
from django.contrib.auth.models import User
from .Models.AccountModel import AccountModel
from .Models.MailboxModel import MailboxModel
from .Models.EMailModel import EMailModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .Models.AttachmentModel import AttachmentModel

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'is_staff']

        def create(self, validated_data):
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                is_staff=validated_data.get('is_staff', False) 
            )
            return user

class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = AccountModel
        fields = '__all__'
        read_only_fields = ['is_healthy']

    def validate_email(self, value):
        return value.lower()

class MailboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailboxModel
        fields = '__all__'
        read_only_fields = ['name', 'account' ,'is_fetched']


class EMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailModel
        fields = '__all__'


class CorrespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrespondentModel
        fields = '__all__'


class EMailCorrespondentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailCorrespondentsModel
        fields = '__all__'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentModel
        fields = '__all__'
        read_only_fields = []