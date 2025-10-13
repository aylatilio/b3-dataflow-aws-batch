"""
extract_ibov.py
---------------------------------
Script responsável por extrair dados do índice IBOVESPA via yfinance,
salvar em formato Parquet particionado por data (simulando o S3 localmente).
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# ========== CONFIGURAÇÕES ==========
TICKER = "^BVSP"  # IBOVESPA

# Caminho absoluto para .../b3-dataflow-aws-batch/data/raw
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)
print(f"📁 Salvando em: {DATA_DIR}")

# ========== EXTRAÇÃO ==========
print("🔹 Baixando dados do IBOVESPA...")
df = yf.download(TICKER, period="1mo", interval="1d")

# Adiciona coluna de ticker
df["ticker"] = "IBOV"

# ========== TRANSFORMAÇÃO ==========
# Correção para retornos do yfinance que vêm com colunas em MultiIndex (tuplas).
df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
df.columns = [c.lower() for c in df.columns]  # força lowercase
# Mostra colunas pra debug
print("Colunas retornadas:", df.columns.tolist())
# Renomeia colunas principais
df = df.rename(columns={
    "open": "preco_abertura",
    "close": "preco_fechamento",
    "volume": "volume_negociado"
})

# Reseta índice para ter a data como coluna
df.reset_index(inplace=True)

# ========== SALVAMENTO ==========
today = datetime.now()
partition_path = f"year={today.year}/month={today.month:02d}/day={today.day:02d}"

save_path = os.path.join(DATA_DIR, partition_path)
os.makedirs(save_path, exist_ok=True)

file_path = os.path.join(save_path, "ibov.parquet")

df.to_parquet(file_path, index=False)
print(f"✅ Arquivo salvo em: {file_path}")
print(f"Linhas: {len(df)}")
