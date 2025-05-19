from django import forms
from .models import Parcela
from .models import INCCIndex

class INCCIndexForm(forms.ModelForm):
    class Meta:
        model = INCCIndex
        fields = ['mes_ano', 'percentual', 'percentual_acumulado']
        widgets = {
            'mes_ano': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'percentual': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }


class ParcelaForm(forms.ModelForm):
    class Meta:
        model = Parcela
        fields = ['nome', 'valor_original', 'data_vencimento', 'data_pagamento', 'aplicar_incc', 'aplicar_juros', 'aplicar_multa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Cliente'}),
            'valor_original': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'aplicar_incc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aplicar_juros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aplicar_multa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Cliente',
            'valor_original': 'Valor Original',
            'data_vencimento': 'Data de Vencimento',
            'data_pagamento': 'Data de Pagamento',
            'aplicar_incc': 'Aplicar correção pelo INCC',
            'aplicar_juros': 'Aplicar juros de mora',
            'aplicar_multa': 'Aplicar multa',
        }
        help_texts = {
            'nome': 'Informe o nome do cliente (opcional).',
            'valor_original': 'Informe o valor original da parcela.',
            'data_vencimento': 'Selecione a data de vencimento da parcela.',
            'data_pagamento': 'Selecione a data de pagamento da parcela.',
            'aplicar_incc': 'Marque se deseja aplicar correção pelo INCC.',
            'aplicar_juros': 'Marque se deseja aplicar juros de mora.',
            'aplicar_multa': 'Marque se deseja aplicar multa.',
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
        }
