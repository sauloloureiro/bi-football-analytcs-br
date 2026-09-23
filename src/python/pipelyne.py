import os
import requests
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# ⚙️ SUAS CONFIGURAÇÕES DO GOOGLE CLOUD
PROJETO_ID = "bi-health-analytics-br-509417"
DATASET_ID = "NOME_DO_SUA_PASTA_NO_BIGQUERY"  # Mude para o seu dataset
TABELA_ID  = "tabela_futebol_bruta"

# ⚽ CONFIGURAÇÃO DA API DE FUTEBOL
URL_API = "https://rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": "SUA_CHAVE_DA_API_AQUI",
    "X-RapidAPI-Host": "://rapidapi.com"
}

def executar_pipeline():
    print("1. Buscando dados na API de futebol...")
    resposta = requests.get(URL_API, headers=HEADERS)
    dados_json = resposta.json()

    print("2. Organizando os dados em linhas e colunas...")
    df = pd.json_normalize(dados_json.get("response", dados_json))

    # Limpeza rápida para o BigQuery aceitar textos complexos
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)

    print("3. Conectando e enviando para o BigQuery Sandbox...")
    # Como o ambiente é online e fora do Google, ele vai ler o arquivo de credenciais
    cliente_bq = bigquery.Client(project=PROJETO_ID)

    configuracao = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True
    )

    caminho_destino = f"{PROJETO_ID}.{DATASET_ID}.{TABELA_ID}"
    tarefa = cliente_bq.load_table_from_dataframe(df, caminho_destino, job_config=configuracao)
    tarefa.result() 

    print(f"✅ Sucesso! Tabela criada no BigQuery Sandbox: {caminho_destino}")

if __name__ == "__main__":
    executar_pipeline()
