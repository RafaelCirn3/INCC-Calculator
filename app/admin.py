from django.contrib import admin
from .models import Parcela, INCCIndex, ConfiguracaoCalculo

admin.site.register(INCCIndex)  
admin.site.register(Parcela)


@admin.register(ConfiguracaoCalculo)
class ConfiguracaoCalculoAdmin(admin.ModelAdmin):
	list_display = ('multa_percentual', 'juros_percentual_mensal', 'taxa_boleto', 'atualizado_em')

	def has_add_permission(self, request):
		if ConfiguracaoCalculo.objects.exists():
			return False
		return super().has_add_permission(request)
