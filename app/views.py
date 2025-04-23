from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParcelaForm, INCCIndexForm
from django.urls import reverse_lazy
from django.http import HttpResponse
import openpyxl
from django.contrib import messages
from .models import Parcela, INCCIndex
from dateutil.relativedelta import relativedelta
from decimal import Decimal


def incc_index_form(request):
    if request.method == 'POST':
        form = INCCIndexForm(request.POST)
        if form.is_valid():
            try:
                # Tenta salvar o índice no banco de dados
                form.save()
                return redirect('incc_create')
            except ValueError as e:
                # Caso a exceção seja gerada (índice já existe), exibe a mensagem de erro
                messages.error(request, str(e))
    else:
        form = INCCIndexForm()

    incc_indices = INCCIndex.objects.all().order_by('-mes_ano')
    return render(request, 'incc/incc_index_form.html', {'form': form, 'incc_indices': incc_indices})


def calcular_incc_acumulado(data_inicio, data_fim):
    """ Retorna o percentual acumulado do INCC entre dois meses """
    if data_fim < data_inicio:
        return Decimal('0')

    acumulado = Decimal('0.00')
    atual = data_inicio.replace(day=1)

    while atual <= data_fim:
        try:
            indice = INCCIndex.objects.get(mes_ano=atual)
            acumulado += indice.percentual
        except INCCIndex.DoesNotExist:
            pass

        atual += relativedelta(months=1)

    return acumulado
def calcular_parcela(request):
    if request.method == 'POST':
        form = ParcelaForm(request.POST)
        if form.is_valid():
            parcela = form.save(commit=False)
            venc = parcela.data_vencimento
            pagto = parcela.data_pagamento

            # se a data de pagamento for anterior ao vencimento, exibe erro
            if venc and pagto:
                if venc > pagto:
                    form.add_error('data_pagamento', 'Data de pagamento não pode ser anterior ao vencimento.')
                    return render(request, 'parcela/form.html', {'form': form})

            #se data de pagamento for definida em um mês que não existe indice de incc, exibe erro
            if pagto:
                try:
                    incc = INCCIndex.objects.get(mes_ano=pagto.replace(day=1))
                except INCCIndex.DoesNotExist:
                    form.add_error('data_pagamento', 'Não existe índice de INCC para o mês de pagamento informado.')
                    return render(request, 'parcela/form.html', {'form': form})
                dias_atraso = (pagto - venc).days

                # Multa de 2% sobre o valor original
                multa = parcela.valor_original * Decimal('0.02')

                # Juros de mora de 1% ao mês (proporcional aos dias)
                juros = parcela.valor_original * Decimal('0.01') * Decimal(dias_atraso) / Decimal('30')

                # Correção pelo INCC informado diretamente pelo usuário (percentual_incc)
                percentual_incc = calcular_incc_acumulado(venc, pagto) / Decimal('100')
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

def parcela_list(request):
    parcelas = Parcela.objects.all()
    incc_indices = INCCIndex.objects.all().order_by('-mes_ano')
    form = INCCIndexForm()
    return render(request, 'parcela/list.html', {
        'parcelas': parcelas,
        'incc_indices': incc_indices,
        'incc_form': form,
    })

def parcela_delete(request, parcela_id):
    parcela = get_object_or_404(Parcela, id=parcela_id)
    if request.method == 'POST':
        parcela.delete()
        return redirect('parcela_list')
    return render(request, 'parcela/list.html', {'parcela': parcela})

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