from django.db import models

class INCCIndex(models.Model):
    mes_ano = models.DateField()
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    percentual_acumulado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Caso já exista um cadastro com aquele mês e ano, não permitir o cadastro
        if INCCIndex.objects.filter(mes_ano=self.mes_ano.replace(day=1)).exists():
            raise ValueError("Já existe um índice cadastrado para este mês e ano.")
        
        # Definindo o dia como o primeiro do mês
        if self.mes_ano:
            self.mes_ano = self.mes_ano.replace(day=1)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"INCC {self.mes_ano.strftime('%m/%Y')} - {self.percentual}%"
class Parcela(models.Model):
    id = models.AutoField(primary_key=True)  # ID da parcela
    nome = models.CharField(max_length=255, blank=True, null=True)  # Nome do cliente (opcional)
    valor_original = models.DecimalField(max_digits=10, decimal_places=2)  # Valor da parcela
    data_vencimento = models.DateField()  # Data de vencimento da parcela
    data_pagamento = models.DateField()  # Data de pagamento da parcela

    # Campos calculados
    dias_atraso = models.IntegerField(null=True, blank=True)
    multa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    juros_mora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    correcao_incc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxa_boleto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Parcela de R$ {self.valor_original} - Venc: {self.data_vencimento}"
