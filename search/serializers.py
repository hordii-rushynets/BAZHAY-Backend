from django.db.models import Q
from rest_framework import serializers
from user.serializers import ReturnBazhayUserSerializer, BazhayUser
from ability.serializers import Wish, WishSerializer


class CombinedSearchSerializer(serializers.Serializer):
    query = serializers.CharField()

    def to_representation(self, instance):
        query = instance.get('query', '')

        bazhay_user_results = BazhayUser.objects.filter(Q(email__icontains=query) | Q(username__icontains=query)
                                                        | Q(about_user__icontains=query))

        wish_results = Wish.objects.filter(Q(name__icontains=query)
                                           | Q(description__icontains=query)
                                           | Q(additional_description__icontains=query)
                                           | Q(author__username__icontains=query)
                                           | Q(brand_author__name__icontains=query)
                                           | Q(brand_author__nickname__icontains=query)
                                           | Q(news_author__title__icontains=query)
                                           | Q(news_author__description__icontains=query))

        bazhay_user_data = ReturnBazhayUserSerializer(bazhay_user_results, many=True).data
        wish_data = WishSerializer(wish_results, many=True).data

        return {
            'bazhay_user_results': bazhay_user_data,
            'wish_results': wish_data
        }