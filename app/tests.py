from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import INCCIndex, Parcela, ConfiguracaoCalculo
from .views import calcular_incc_acumulado


class RegrasCalculoTests(TestCase):
	def setUp(self):
		ConfiguracaoCalculo.obter_configuracao()

	def test_calcular_incc_acumulado_nao_inclui_mes_pagamento(self):
		INCCIndex.objects.create(mes_ano=date(2026, 1, 1), percentual=Decimal('0.10'))
		INCCIndex.objects.create(mes_ano=date(2026, 2, 1), percentual=Decimal('0.20'))
		INCCIndex.objects.create(mes_ano=date(2026, 3, 1), percentual=Decimal('0.30'))

		acumulado = calcular_incc_acumulado(date(2026, 1, 15), date(2026, 3, 10))

		self.assertEqual(acumulado, Decimal('0.30'))

	def test_calcular_parcela_usa_parametros_configurados(self):
		configuracao = ConfiguracaoCalculo.obter_configuracao()
		configuracao.multa_percentual = Decimal('0.0500')
		configuracao.juros_percentual_mensal = Decimal('0.0200')
		configuracao.taxa_boleto = Decimal('10.00')
		configuracao.save()

		INCCIndex.objects.create(mes_ano=date(2026, 1, 1), percentual=Decimal('0.20'))

		response = self.client.post(
			reverse('calcular_parcela'),
			{
				'nome': 'Cliente Teste',
				'valor_original': '100.00',
				'data_vencimento': '2026-01-01',
				'data_pagamento': '2026-01-31',
				'aplicar_incc': '',
				'aplicar_juros': 'on',
				'aplicar_multa': 'on',
			},
		)

		self.assertEqual(response.status_code, 302)
		parcela = Parcela.objects.get(nome='Cliente Teste')
		self.assertEqual(parcela.multa, Decimal('5.00'))
		self.assertEqual(parcela.juros_mora, Decimal('2.00'))
		self.assertEqual(parcela.taxa_boleto, Decimal('10.00'))
		self.assertEqual(parcela.valor_total, Decimal('117.00'))

	def test_calcular_parcela_com_configuracao_padrao_nao_quebra_decimal(self):
		INCCIndex.objects.create(mes_ano=date(2026, 1, 1), percentual=Decimal('0.10'))

		response = self.client.post(
			reverse('calcular_parcela'),
			{
				'nome': 'Sem Float Error',
				'valor_original': '100.00',
				'data_vencimento': '2026-01-01',
				'data_pagamento': '2026-01-15',
				'aplicar_incc': '',
				'aplicar_juros': 'on',
				'aplicar_multa': 'on',
			},
		)

		self.assertEqual(response.status_code, 302)
		parcela = Parcela.objects.get(nome='Sem Float Error')
		self.assertIsInstance(parcela.multa, Decimal)
		self.assertIsInstance(parcela.juros_mora, Decimal)
		self.assertIsInstance(parcela.taxa_boleto, Decimal)


class ViewsFluxoTests(TestCase):
	def test_alimentar_incc_bloqueia_get(self):
		response = self.client.get(reverse('alimentar_incc'))
		self.assertEqual(response.status_code, 405)

	def test_gerar_excel_sem_parcelas(self):
		response = self.client.get(reverse('gerar_excel'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response['Content-Type'],
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		)

	def test_parcela_list_filtra_por_nome_e_atraso(self):
		Parcela.objects.create(
			nome='Alice',
			valor_original=Decimal('100.00'),
			data_vencimento=date(2026, 1, 1),
			data_pagamento=date(2026, 1, 10),
			dias_atraso=9,
			multa=Decimal('2.00'),
			juros_mora=Decimal('0.30'),
			correcao_incc=Decimal('0.00'),
			taxa_boleto=Decimal('3.00'),
			valor_total=Decimal('105.30'),
		)
		Parcela.objects.create(
			nome='Bruno',
			valor_original=Decimal('200.00'),
			data_vencimento=date(2026, 1, 1),
			data_pagamento=date(2026, 1, 1),
			dias_atraso=0,
			multa=Decimal('0.00'),
			juros_mora=Decimal('0.00'),
			correcao_incc=Decimal('0.00'),
			taxa_boleto=Decimal('3.00'),
			valor_total=Decimal('203.00'),
		)

		response = self.client.get(reverse('parcela_list'), {'nome': 'ali', 'atraso_min': '1'})

		self.assertEqual(response.status_code, 200)
		parcelas = response.context['parcelas']
		self.assertEqual(parcelas.count(), 1)
		self.assertEqual(parcelas.first().nome, 'Alice')
