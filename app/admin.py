from django.contrib import admin
from .models import Parcela, INCCIndex

admin.site.register(INCCIndex)  # Registra o modelo INCCIndex no painel administrativo
admin.site.register(Parcela)
