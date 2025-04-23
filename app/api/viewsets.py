# app/views.py

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..models import INCCIndex
from .serializers import INCCIndexSerializer

class INCCIndexViewSet(viewsets.ModelViewSet):
    queryset = INCCIndex.objects.all()
    serializer_class = INCCIndexSerializer
    
    def perform_create(self, serializer):
        # Verificar se já existe um índice para o mês e ano
        if INCCIndex.objects.filter(mes_ano=serializer.validated_data['mes_ano'].replace(day=1)).exists():
            raise ValidationError("Já existe um índice cadastrado para este mês e ano.")
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Sobrescrever o método create para garantir que a validação ocorra
        return super().create(request, *args, **kwargs)
