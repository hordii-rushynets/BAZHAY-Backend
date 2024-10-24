import requests

from rest_framework import serializers
from datetime import datetime

from .models import Premium

from google.oauth2 import service_account
from google.auth.transport.requests import Request


class GoogleValidateSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField()
    product_id = serializers.CharField()
    purchase_token = serializers.CharField()

    class Meta:
        model = Premium
        fields = ['id', 'end_date', 'is_used_trial', 'is_an_annual_payment', 'is_trial_period']
        read_only_fields = ['id', 'end_date']

    def create(self, validated_data):
        user = self.context['request'].user

        SERVICE_ACCOUNT_FILE = 'meta-tracker-304410-8b1ff946e12e.json'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )

        credentials.refresh(Request())

        PACKAGE_NAME = validated_data.get('package_name')
        PRODUCT_ID = validated_data.get('product_id')
        PURCHASE_TOKEN = validated_data.get('purchase_token')

        headers = {'Authorization': f'Bearer {credentials.token}'}
        url = f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{PACKAGE_NAME}/purchases/subscriptions/{PRODUCT_ID}/tokens/{PURCHASE_TOKEN}'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            premium = Premium.objects.get_or_create(bazhay_user=user)
            purchase_data = response.json()
            match purchase_data.get('paymentState'):
                case 0:
                    serializers.ValidationError(detail='Purchase is invalid.')
                case 1:
                    seconds = purchase_data.get('expiryTimeMillis') / 1000.
                    premium.end_date = datetime.fromtimestamp(seconds)
                    premium.save()
                case 2:
                    seconds = purchase_data.get('expiryTimeMillis') / 1000.
                    premium.end_date = datetime.fromtimestamp(seconds)
        else:
            serializers.ValidationError(detail="Google service error.")

