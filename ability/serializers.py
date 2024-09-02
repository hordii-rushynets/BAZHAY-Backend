from rest_framework import serializers

from .models import Wish, Reservation

from user.serializers import UpdateUserSerializers
from base64_conversion import conversion


class WishSerializer(serializers.ModelSerializer):
    """Wish Serializer"""
    media = conversion.Base64MediaField(required=False)
    author = UpdateUserSerializers(read_only=True)
    is_reservation = serializers.SerializerMethodField()

    class Meta:
        model = Wish
        fields = ['id', 'name', 'media', 'price', 'link', 'description','additional_description', 'access_type',
                  'currency', 'created_at', 'is_fully_created', 'is_reservation', 'author']
        read_only_fields = ['id', 'author', 'created_at']

    def get_is_reservation(self, obj: Wish) -> bool:
        return Reservation.objects.filter(wish=obj).exists()


class ReservationSerializer(serializers.Serializer):
    """Reservation serializer"""
    bazhay_user = UpdateUserSerializers(read_only=True)
    wish = WishSerializer(read_only=True)
    wish_id = serializers.PrimaryKeyRelatedField(queryset=Wish.objects.all(), write_only=True, source='wish')

    class Meta:
        model = Reservation
        fields = ['id', 'bazhay_user', 'wish']
        read_only_fields = ['id']

    def validate(self, attrs: dict) -> dict:
        """Validate data"""
        user = self.context['request'].user
        wish = attrs.get('wish')

        if wish.author == user:
            raise serializers.ValidationError("You can't reserve your wishes")

        if Reservation.objects.filter(wish=wish).exists():
            raise serializers.ValidationError("This wish is already reserved.")

        return attrs

    def create(self, validated_data: dict) -> Reservation:
        """Create new wish reservation"""
        user = self.context['request'].user
        reservation = Reservation.objects.create(bazhay_user=user, **validated_data)
        return reservation

