"""
lambda_trigger.py
---------------------------------
Função AWS Lambda que monitora o bucket RAW.
- É acionada automaticamente via evento S3 (ObjectCreated).
- Ao detectar novo arquivo Parquet em 'raw/', dispara o Glue Job 'b3-etl-job'.
- Passa como argumento o caminho de origem (RAW_PATH) e destino (REFINED_PATH).
- Ignora arquivos que não sejam .parquet ou fora da camada raw.
"""

import boto3
import urllib.parse
import json

def lambda_handler(event, context):
    """Lambda Trigger para iniciar o Glue Job ao detectar novo arquivo no S3 (camada raw)."""

    glue = boto3.client('glue')

    for record in event['Records']:
        # Extrai informações do evento S3
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        print(f"Novo arquivo detectado: s3://{bucket}/{key}")

        # Verifica se é um parquet da camada raw
        if 'raw/' in key and key.endswith('.parquet'):
            print("Arquivo válido — iniciando Glue Job...")

            try:
                response = glue.start_job_run(
                    JobName='b3-etl-job',
                    Arguments={
                        '--RAW_PATH': f's3://{bucket}/{key}',
                        '--REFINED_PATH': key.replace('raw', 'refined')
                    }
                )
                print(f"Glue Job iniciado com sucesso! Run ID: {response['JobRunId']}")

            except Exception as e:
                print("Erro ao iniciar o Glue Job:", e)

        else:
            print("Arquivo ignorado (não é parquet da camada raw).")

    return {
        'statusCode': 200,
        'body': json.dumps('Lambda executado com sucesso!')
    }
