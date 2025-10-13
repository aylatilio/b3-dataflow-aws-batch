"""
upload_s3.py
---------------------------------
Faz o upload do arquivo Parquet gerado localmente para o bucket S3.
"""

import boto3
import os
from datetime import datetime

# ===== CONFIGURAÇÕES =====
BUCKET_NAME = "b3-dataflow-raw"   # nome do bucket criado
LOCAL_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
LOCAL_BASE_PATH = os.path.abspath(LOCAL_BASE_PATH)

# ===== CONEXÃO AWS =====
s3 = boto3.client("s3")

# ===== LOCALIZA O ARQUIVO MAIS RECENTE =====
today = datetime.now()
partition_path = f"year={today.year}/month={today.month:02d}/day={today.day:02d}"
local_file = os.path.join(LOCAL_BASE_PATH, partition_path, "ibov.parquet")

if not os.path.exists(local_file):
    raise FileNotFoundError(f"Arquivo não encontrado: {local_file}")

# ===== DEFINE CAMINHO DE UPLOAD NO S3 =====
s3_key = f"raw/{partition_path}/ibov.parquet"

print(f"📤 Enviando {local_file} para s3://{BUCKET_NAME}/{s3_key}...")

s3.upload_file(local_file, BUCKET_NAME, s3_key)

print("✅ Upload concluído com sucesso!")
