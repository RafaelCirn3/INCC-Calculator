from django.db import models
from decimal import Decimal

class INCCIndex(models.Model):
    mes_ano = models.DateField()
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    percentual_acumulado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if INCCIndex.objects.filter(mes_ano=self.mes_ano.replace(day=1)).exists():
            raise ValueError("Já existe um índice cadastrado para este mês e ano.")

        # Definindo o dia como o primeiro do mês
        if self.mes_ano:
            self.mes_ano = self.mes_ano.replace(day=1)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"INCC {self.mes_ano.strftime('%m/%Y')} - {self.percentual}%"


class Parcela(models.Model):
    id = models.AutoField(primary_key=True) 
    nome = models.CharField(max_length=255, blank=True, null=True)  
    valor_original = models.DecimalField(max_digits=10, decimal_places=2) 
    data_vencimento = models.DateField() 
    data_pagamento = models.DateField()  

    # Campos calculados
    dias_atraso = models.IntegerField(null=True, blank=True)
    multa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    juros_mora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    correcao_incc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxa_boleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    aplicar_incc = models.BooleanField(default=True)
    aplicar_juros = models.BooleanField(default=True)
    aplicar_multa = models.BooleanField(default=True)


    def __str__(self):
        return f"Parcela de R$ {self.valor_original} - Venc: {self.data_vencimento}"


class ConfiguracaoCalculo(models.Model):
    multa_percentual = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0200'))
    juros_percentual_mensal = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0100'))
    taxa_boleto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('3.00'))
    atualizado_em = models.DateTimeField(auto_now=True)

    @classmethod
    def obter_configuracao(cls):
        configuracao, _ = cls.objects.get_or_create(
            id=1,
            defaults={
                'multa_percentual': Decimal('0.0200'),
                'juros_percentual_mensal': Decimal('0.0100'),
                'taxa_boleto': Decimal('3.00'),
            },
        )
        return configuracao

    def save(self, *args, **kwargs):
        # Mantém uma configuração única para simplificar operação no admin.
        self.id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuração de Cálculo"
