from rest_framework import serializers
from .models import Rig, Well

class RigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rig
        fields = ('__all__')
        
        
class WellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Well
        fields = ('__all__')