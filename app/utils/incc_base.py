# utils/incc_base.py
from datetime import datetime
from app.models import INCCIndex

dados_incc = [
    {"mes_ano": "2023-12-01", "percentual": 0.26},
    {"mes_ano": "2024-01-01", "percentual": 0.23},
    {"mes_ano": "2024-02-01", "percentual": 0.20},
    {"mes_ano": "2024-03-01", "percentual": 0.24},
    {"mes_ano": "2024-04-01", "percentual": 0.41},
    {"mes_ano": "2024-05-01", "percentual": 0.59},
    {"mes_ano": "2024-06-01", "percentual": 0.93},
    {"mes_ano": "2024-07-01", "percentual": 0.69},
    {"mes_ano": "2024-08-01", "percentual": 0.64},
    {"mes_ano": "2024-09-01", "percentual": 0.61},
    {"mes_ano": "2024-10-01", "percentual": 0.67},
    {"mes_ano": "2024-11-01", "percentual": 0.44},
    {"mes_ano": "2024-12-01", "percentual": 0.51},
    {"mes_ano": "2025-01-01", "percentual": 0.71},
    {"mes_ano": "2025-02-01", "percentual": 0.51},
    {"mes_ano": "2025-03-01", "percentual": 0.38},
    {"mes_ano": "2025-04-01", "percentual": 0.44},
]

def carregar_incc_no_banco():
    objetos_incc = []

    for dado in dados_incc:
        # Verifica se o índice já existe
        if not INCCIndex.objects.filter(mes_ano=datetime.strptime(dado['mes_ano'], "%Y-%m-%d").date()).exists():
            # Se não existe, cria o objeto
            objetos_incc.append(
                INCCIndex(
                    mes_ano=datetime.strptime(dado['mes_ano'], "%Y-%m-%d").date(),
                    percentual=dado['percentual']
                )
            )

    # Insere em massa os objetos que não existem
    if objetos_incc:
        INCCIndex.objects.bulk_create(objetos_incc)
