from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from dateutil.relativedelta import relativedelta

from decimal import Decimal
from .models import Parcela, INCCIndex
from .forms import ParcelaForm, INCCIndexForm
import openpyxl
from django.views.decorators.csrf import csrf_exempt
from .utils.incc_base import carregar_incc_no_banco

def base(request):
    return render(request, 'base.html')

def incc_index_form(request):
    if request.method == 'POST':
        form = INCCIndexForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('incc_create')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = INCCIndexForm()

    incc_indices = INCCIndex.objects.all().order_by('-mes_ano')
    return render(request, 'incc/incc_index_form.html', {'form': form, 'incc_indices': incc_indices})


# Função para calcular o percentual acumulado do INCC entre duas datas
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

# Função para calcular a parcela
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

            if pagto:
                # Tenta buscar o INCC do mês de pagamento. Se não existir, tenta o do mês anterior.
                mes_ref = pagto.replace(day=1)
                try:
                    incc = INCCIndex.objects.get(mes_ano=mes_ref)
                except INCCIndex.DoesNotExist:
                    mes_ref = mes_ref - relativedelta(months=1)
                    try:
                        incc = INCCIndex.objects.get(mes_ano=mes_ref)
                    except INCCIndex.DoesNotExist:
                        form.add_error('data_pagamento', 'Não existe índice de INCC para o mês de pagamento ou mês anterior.')
                        return render(request, 'parcela/form.html', {'form': form})

                dias_atraso = (pagto - venc).days
                dias_atraso = max(dias_atraso, 0)

                # Multa de 2%
                multa = parcela.valor_original * Decimal('0.02')

                # Juros proporcionais (1% ao mês = 0.03333% ao dia, aproximado por 1/30)
                if parcela.aplicar_juros:
                    juros = parcela.valor_original * Decimal('0.01') * Decimal(dias_atraso) / Decimal('30')
                else:
                    juros = Decimal('0.00')
                # Correção opcional pelo INCC
                if parcela.aplicar_incc:
                    percentual_incc = calcular_incc_acumulado(venc, pagto) / Decimal('100')
                    correcao_incc = parcela.valor_original * percentual_incc
                else:
                    correcao_incc = Decimal('0.00')

                # Taxa de boleto fixa
                taxa_boleto = Decimal('3.00')

                # Valor total
                total = parcela.valor_original + multa + juros + correcao_incc + taxa_boleto

                # Preenchendo campos
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

def excluir_varias_parcelas(request):
    if request.method == 'POST':
        ids = request.POST.getlist('parcelas_selecionadas')
        if ids:
            Parcela.objects.filter(id__in=ids).delete()
            messages.success(request, f"{len(ids)} parcela(s) excluída(s) com sucesso.")
        else:
            messages.warning(request, "Nenhuma parcela foi selecionada.")
    return redirect('parcela_list')

def gerar_excel(request):
    # Cria uma planilha Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Parcelas'

    #soma os valores totais e colocar no final da planilha
    total_valor_atualizado = sum(parcela.valor_total for parcela in Parcela.objects.all())
    total_valor_original = sum(parcela.valor_original for parcela in Parcela.objects.all())
    # Definir os cabeçalhos da planilha
    headers = ['Data Vencimento', 'Data Pagamento', 'Valor Original', 'Valor Total']
    ws.append(headers)

    # Adicionar dados das parcelas
    parcelas = Parcela.objects.all()
    for parcela in parcelas:
        ws.append([

            parcela.data_vencimento.strftime('%d/%m/%Y'),
            parcela.data_pagamento.strftime('%d/%m/%Y'),
            str(parcela.valor_original),
            str(parcela.valor_total),
        ])
    # Adicionar a soma total na última linha
    ws.append(['', '', 'Valor Original:', str(total_valor_original)])
    ws.append(['', '', 'Valor Atualizado:', str(total_valor_atualizado)])

    # Criar a resposta HTTP com o arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="parcelas.xlsx"'
    
    # Salvar o arquivo Excel na resposta
    wb.save(response)
    
    return response

@csrf_exempt  # Ação que pode ser acessada sem CSRF para facilitar no exemplo
def alimentar_incc(request):
    if request.method == 'POST':
        # Carregar os dados do INCC no banco de dados
        try:
            carregar_incc_no_banco()  # Chama o código para carregar os dados
            messages.success(request, "Dados do INCC alimentados com sucesso!")
        except Exception as e:
            return HttpResponse(f"Erro ao alimentar os dados INCC: {str(e)}")

    return redirect('incc_index')  # Redireciona de volta para a lista de INCC