from rest_framework import serializers
from .models import Master,Pos,SeasonalTrend
from datetime import datetime
import json
class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ('title','jan','manufucturer','mpn','category','subcategory')

class PosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pos
        fields = ('jan','datetime','price','sales','amount')

class SeasonalTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonalTrend
        fields = ('subcategory','sales')

class SampleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)