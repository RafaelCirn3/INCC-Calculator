# 🧮 Sistema de Cálculo de Parcelas com INCC, Juros e Multa

Esta aplicação em **Django** tem como objetivo calcular o valor atualizado de parcelas em atraso, considerando:

- Correção monetária pelo **INCC**
- **Multa de 2%**
- **Juros de 1% ao mês**
- **Taxa de emissão de novo boleto**
- Geração de **relatório Excel**

---

## 📌 Visão Geral

A aplicação permite que o usuário insira:
- O **valor original da parcela**
- A **data de vencimento**
- A **data de pagamento**
- Uma **tabela com os índices INCC mensais**

Com essas informações, a aplicação calcula:
- Dias de atraso
- Multa
- Juros
- Correção pelo INCC
- Valor total a receber
- Exportação dos dados em **formato Excel**

---

## 🧾 Fórmulas Utilizadas

### 📈 Atualização pelo INCC
```python
valor_corrigido = valor_original × (1 + índice_acumulado_INCC)
```

O índice acumulado é a soma dos índices mensais do INCC desde o mês do vencimento até o mês anterior ao pagamento.

### ⚠️ Multa
```python
multa = valor_original × 0.02
```

### 💰 Juros de Mora
```python
juros_mora = valor_original × (0.01 × (dias_atraso / 30))
```

### 🗂️ Exemplo de Entrada

Valor Parcela |	Vencimento	| Pagamento 

R$ 654,05 |	01/04/2024| 05/04/2025

- Índices INCC mensais de 04/2024 a 03/2025

## 🧾 Exemplo de Saída
- A aplicação gera uma planilha .xlsx com as colunas:

###  Valor Original

- Vencimento

- Data de Pagamento

- Dias de Atraso

- Multa (R$)

- Juros de Mora (R$)

- Correção INCC (R$)

- Taxa Boleto (R$)

- Total a Receber (R$)

