
FROM python:3.13


WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todos os arquivos do projeto para o container
COPY . .

# Expõe a porta padrão do Django
EXPOSE 8000

# Comando para rodar o servidor de desenvolvimento
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
