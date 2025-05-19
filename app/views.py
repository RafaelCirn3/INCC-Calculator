from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from dateutil.relativedelta import relativedelta

from decimal import Decimal
from .models import Parcela, INCCIndex
from .forms import ParcelaForm, INCCIndexForm
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
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
                #Multa Opcional
                multa = Decimal('0.00')  # Valor padrão
                if parcela.aplicar_multa:
                    if dias_atraso > 0:
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
    # Buscar dados das parcelas
    parcelas = Parcela.objects.all()

    # Criar DataFrame com os dados
    data = []
    for p in parcelas:
        data.append({
            'Data Vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
            'Data Pagamento': p.data_pagamento.strftime('%d/%m/%Y'),
            'Valor Original': float(p.valor_original),
            'Valor Total': float(p.valor_total),
        })

    df = pd.DataFrame(data)

    # Cálculo dos totais
    total_original = df['Valor Original'].sum()
    total_total = df['Valor Total'].sum()

    # Adicionar linhas de totais
    df.loc[len(df.index)] = ['', '', 'Valor Original:', total_original]
    df.loc[len(df.index)] = ['', '', 'Valor Atualizado:', total_total]

    # Criar um arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="parcelas.xlsx"'

    # Gravar no arquivo
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Parcelas', index=False)

        # Estilização com openpyxl
        wb = writer.book
        ws = writer.sheets['Parcelas']

        # Estilo para cabeçalhos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="4F81BD")
        center_align = Alignment(horizontal='center')
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for col_num, column_title in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = border

        # Estilo para dados e ajuste de largura
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=ws.max_column):
            for cell in row:
                cell.border = border
                if isinstance(cell.value, float):
                    cell.number_format = '#,##0.00'

        # Ajustar largura das colunas automaticamente
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 2

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