from rest_framework import serializers
from django.conf import settings


class MediaURLSerializer(serializers.Serializer):

    def to_representation(self, obj):
        request = self.context['request']
        try:
            return request.build_absolute_uri(obj.file.url)
        except:
            return settings.HOST + obj.file.url