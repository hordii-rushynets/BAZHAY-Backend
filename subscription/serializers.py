from rest_framework import serializers
from .models import Subscription
from user.serializers import UpdateUserSerializers
from user.models import BazhayUser


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UpdateUserSerializers(read_only=True)
    subscribed_to = UpdateUserSerializers(read_only=True)
    subscribed_to_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Subscription
        fields = ['user', 'subscribed_to', 'subscribed_to_email', 'created_at']

    def validate(self, data):
        subscribed_to_email = data.get('subscribed_to_email')
        request_user = self.context['request'].user

        try:
            subscribed_to_user = BazhayUser.objects.get(email=subscribed_to_email)
        except BazhayUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "Користувач не знайдений."})

        if subscribed_to_user == request_user:
            raise serializers.ValidationError({"detail": "Ви не можете підписатися на себе."})

        data['subscribed_to'] = subscribed_to_user
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        subscribed_to = validated_data['subscribed_to']
        subscription, created = Subscription.objects.get_or_create(user=user, subscribed_to=subscribed_to)

        if not created:
            raise serializers.ValidationError({"detail": "Ви вже підписані на цього користувача."})

        return subscription
