from rest_framework import serializers
from .models import Ability, Subscription


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = ['id', 'name', 'media', 'price', 'link', 'description', 'additional_description', 'author', 'access_type']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'subscribed_to', 'created_at']
