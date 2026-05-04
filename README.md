
# ▶️ Como Executar

Siga os passos abaixo para rodar o projeto localmente:

### 1. Clone o repositório

```bash
git clone https://github.com/RafaelCirn3/INCC-Calculator
cd INCC-Calculator
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute as migrações do banco de dados

```bash
python manage.py migrate
```

### 5. Popule o banco com os índices INCC

```bash
python manage.py carregar_incc
```

### 6. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse a aplicação em `http://127.0.0.1:8000`


# Executando com Docker Desktop

No Windows, basta dar duplo clique em [iniciar_projeto.bat](iniciar_projeto.bat). O script verifica o Docker Desktop, executa o `docker compose` e abre a aplicação em `http://localhost:8000`.

Se preferir executar manualmente, use:

```bash
docker compose up --build -d
```

```bash
docker compose down
```

---
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

---

## 🗂️ Exemplo de Entrada

Valor Parcela |	Vencimento	| Pagamento 

R$ 654,05 |	01/04/2024| 05/04/2025

- Índices INCC mensais de 04/2024 a 03/2025

## 🧾 Exemplo de Saída
- A aplicação gera uma planilha .xlsx com as colunas:

- Valor Original
- Vencimento
- Data de Pagamento
- Dias de Atraso
- Multa (R$)
- Juros de Mora (R$)
- Correção INCC (R$)
- Taxa Boleto (R$)
- Total a Receber (R$)

---
