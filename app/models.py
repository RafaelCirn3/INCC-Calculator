from django.db import models


class Parcela(models.Model):
    id = models.AutoField(primary_key=True)  # ID da parcela
    nome = models.CharField(max_length=255, blank=True, null=True)  # Nome do cliente (opcional)
    valor_original = models.DecimalField(max_digits=10, decimal_places=2)  # Valor da parcela
    data_vencimento = models.DateField()  # Data de vencimento da parcela
    data_pagamento = models.DateField()  # Data de pagamento da parcela

    # INCC
    percentual_incc = models.FloatField(null=True, blank=True, help_text="Percentual do INCC aplicado na parcela") 

    # Campos calculados
    dias_atraso = models.IntegerField(null=True, blank=True)
    multa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    juros_mora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    correcao_incc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxa_boleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Parcela de R$ {self.valor_original} - Venc: {self.data_vencimento}"
