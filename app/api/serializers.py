# app/serializers.py

from rest_framework import serializers
from ..models import INCCIndex

class INCCIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = INCCIndex
        fields = ['id', 'mes_ano', 'percentual', 'percentual_acumulado']
