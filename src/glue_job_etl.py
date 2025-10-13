"""
glue_job_etl.py
---------------------------------
Simula um job AWS Glue ETL localmente:
- Lê dados do S3 (parquet bruto)
- Aplica transformações (ex: média móvel)
- Grava resultado em outro bucket
"""

import pandas as pd
import boto3
import os
from io import BytesIO

# ==============================
# CONFIGURAÇÕES
# ==============================
REGION = "sa-east-1"
RAW_BUCKET = "b3-dataflow-raw"
REFINED_BUCKET = "b3-dataflow-refined"
RAW_PREFIX = "raw/"
REFINED_PREFIX = "refined/"

s3 = boto3.client("s3", region_name=REGION)

# ==============================
# ETAPA 1 — Localizar arquivo parquet mais recente no bucket RAW
# ==============================
response = s3.list_objects_v2(Bucket=RAW_BUCKET, Prefix=RAW_PREFIX)
objects = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".parquet")]

if not objects:
    raise FileNotFoundError("Nenhum arquivo parquet encontrado no bucket RAW.")

latest_key = sorted(objects)[-1]
print(f"📦 Arquivo encontrado: {latest_key}")

# ==============================
# ETAPA 2 — Ler parquet direto do S3
# ==============================
buffer = BytesIO()
s3.download_fileobj(RAW_BUCKET, latest_key, buffer)
buffer.seek(0)
df = pd.read_parquet(buffer)

print(f"✅ Dados carregados — {len(df)} linhas")

# ==============================
# ETAPA 3 — Transformações simples
# ==============================
df["media_movel_3d"] = df["preco_fechamento"].rolling(window=3).mean()

# ==============================
# ETAPA 4 — Gravar no bucket REFINED
# ==============================
refined_key = latest_key.replace(RAW_PREFIX, REFINED_PREFIX)
output = BytesIO()
df.to_parquet(output, index=False)
output.seek(0)

s3.put_object(Bucket=REFINED_BUCKET, Key=refined_key, Body=output.getvalue())

print(f"🚀 Transformação concluída e salva em: s3://{REFINED_BUCKET}/{refined_key}")
