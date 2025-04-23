from django import forms
from .models import Parcela
from decimal import Decimal

class ParcelaForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = ['nome', 'valor_original', 'data_vencimento', 'data_pagamento', 'percentual_incc']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Cliente'}),
            'valor_original': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'percentual_incc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 3.5'}),
        }
        labels = {
            'nome': 'Nome do Cliente',
            'valor_original': 'Valor Original',
            'data_vencimento': 'Data de Vencimento',
            'data_pagamento': 'Data de Pagamento',
            'percentual_incc': 'INCC acumulado (%)',
        }
        help_texts = {
            'nome': 'Informe o nome do cliente (opcional).',
            'valor_original': 'Informe o valor original da parcela.',
            'data_vencimento': 'Selecione a data de vencimento da parcela.',
            'data_pagamento': 'Selecione a data de pagamento da parcela.',
            'percentual_incc': 'Informe o percentual acumulado de INCC entre o vencimento e o pagamento (ex: 3.5 para 3,5%).',
        }
        error_messages = {
            'valor_original': {
                'required': 'Este campo é obrigatório.',
                'invalid': 'Informe um valor válido.',
            },
            'data_vencimento': {
                'required': 'Este campo é obrigatório.',
                'invalid': 'Informe uma data válida.',
            },
            'data_pagamento': {
                'required': 'Este campo é obrigatório.',
                'invalid': 'Informe uma data válida.',
            },
            'percentual_incc': {
                'required': 'Informe o valor percentual do INCC.',
                'invalid': 'Informe um número válido (ex: 3.5).',
            },
        }
