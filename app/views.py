from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParcelaForm
from django.http import HttpResponse
import openpyxl

from .models import Parcela
from dateutil.relativedelta import relativedelta
from decimal import Decimal

def parcela_list(request):
    parcelas = Parcela.objects.all().order_by('-id')  # Ordena do mais recente pro mais antigo
    return render(request, 'parcela/list.html', {'parcelas': parcelas})

def calcular_parcela(request):
    if request.method == 'POST':
        form = ParcelaForm(request.POST)
        if form.is_valid():
            parcela = form.save(commit=False)
            venc = parcela.data_vencimento
            pagto = parcela.data_pagamento

            if venc and pagto:
                if venc > pagto:
                    form.add_error('data_pagamento', 'Data de pagamento não pode ser anterior ao vencimento.')
                    return render(request, 'parcela/form.html', {'form': form})

                dias_atraso = (pagto - venc).days

                # Multa de 2% sobre o valor original
                multa = parcela.valor_original * Decimal('0.02')

                # Juros de mora de 1% ao mês (proporcional aos dias)
                juros = parcela.valor_original * Decimal('0.01') * Decimal(dias_atraso) / Decimal('30')

                # Correção pelo INCC informado diretamente pelo usuário (percentual_incc)
                percentual_incc = Decimal(parcela.percentual_incc) / Decimal('100')  # converter para fator
                correcao_incc = parcela.valor_original * percentual_incc

                # Taxa fixa do boleto
                taxa_boleto = Decimal('3.00')

                # Valor total com todos os acréscimos
                total = parcela.valor_original + multa + juros + correcao_incc + taxa_boleto

                # Preenchendo os campos calculados
                parcela.dias_atraso = dias_atraso
                parcela.multa = multa
                parcela.juros_mora = juros
                parcela.correcao_incc = correcao_incc
                parcela.taxa_boleto = taxa_boleto
                parcela.valor_total = total

                parcela.save()

                return redirect('parcela_detalhe', parcela_id=parcela.id)
    else:
        form = ParcelaForm()

    return render(request, 'parcela/form.html', {'form': form})

def parcela_detalhe(request, parcela_id):
    parcela = get_object_or_404(Parcela, id=parcela_id)
    return render(request, 'parcela/detail.html', {'parcela': parcela})


def base(request):
    return render(request, 'base.html')

def gerar_excel(request):
    # Cria uma planilha Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Parcelas'

    # Definir os cabeçalhos da planilha
    headers = ['ID', 'Data Vencimento', 'Data Pagamento', 'Valor Original', 'Dias de Atraso', 'Multa', 'Juros', 'Correção INCC', 'Taxa Boleto', 'Valor Total']
    ws.append(headers)

    # Adicionar dados das parcelas
    parcelas = Parcela.objects.all()
    for parcela in parcelas:
        ws.append([
            parcela.id,
            parcela.data_vencimento.strftime('%d/%m/%Y'),
            parcela.data_pagamento.strftime('%d/%m/%Y'),
            str(parcela.valor_original),
            parcela.dias_atraso,
            str(parcela.multa),
            str(parcela.juros_mora),
            str(parcela.correcao_incc),
            str(parcela.taxa_boleto),
            str(parcela.valor_total),
        ])

    # Criar a resposta HTTP com o arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="parcelas.xlsx"'
    
    # Salvar o arquivo Excel na resposta
    wb.save(response)
    
    return response