from rest_framework import serializers
from django.utils import timezone

from user.serializers import ReturnBazhayUserSerializer

from .models import Premium


class PremiumSerializers(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    code = serializers.CharField(write_only=True)

    class Meta:
        model = Premium
        fields = ['id', 'date_of_payment', 'is_active', 'is_an_annual_payment', 'expiration_date', 'code']
        read_only_fields = ['id', 'date_of_payment', 'is_active', 'expiration_date']

    def get_is_active(self, obj):
        return obj.is_active

    def validate_code(self, value):
        # Code validation logic will be added later
        return value

    def validate(self, attrs):
        instance = self.context.get('instance')

        if instance and instance.is_active:
            raise serializers.ValidationError('Subscription has expired')
        return attrs

    def create(self, validated_data):
        bazhay_user = self.context['request'].user
        is_an_annual_payment = validated_data.get('is_an_annual_payment', False)

        instance, created = Premium.objects.get_or_create(
            bazhay_user=bazhay_user,
            defaults={
                'date_of_payment': timezone.now(),
                'is_an_annual_payment': is_an_annual_payment,
                'is_used_trial': True,
            }
        )

        if not created:
            instance.date_of_payment = timezone.now()
            instance.is_an_annual_payment = is_an_annual_payment
            instance.save()

        return instance


class TrialSubscriptionSerializer(serializers.Serializer):
    def create(self, validated_data):
        bazhay_user = self.context['request'].user

        instance, created = Premium.objects.get_or_create(
            bazhay_user=bazhay_user,
            defaults={
                'date_of_payment': timezone.now(),
                'is_used_trial': False,
                'is_trial_period': True,
            }
        )

        if not created:
            raise serializers.ValidationError()
        return instance
