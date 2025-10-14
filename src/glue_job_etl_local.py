# src/glue_job_etl_local.py
"""
Simulador Local do Glue Job (b3-etl-job)
-------------------------------------------
Este script reproduz localmente as transformações que o AWS Glue faria.
Fluxo:
1. Lê o parquet bruto gerado pelo extract_ibov.py (data/raw/)
2. Aplica transformações (renomeia colunas, cria derivadas, agrega)
3. Salva o resultado em parquet no diretório data/refined/
"""

import pandas as pd
from pathlib import Path

# Caminhos locais
RAW_DIR = Path("data/raw")
REFINED_DIR = Path("data/refined")

# Garante que o diretório de saída existe
REFINED_DIR.mkdir(parents=True, exist_ok=True)

print("🔹 Lendo parquet bruto...")
# Lê todos os arquivos parquet do diretório raw
df = pd.concat(pd.read_parquet(f) for f in RAW_DIR.rglob("*.parquet"))

# Renomeia colunas para padrão de negócio
df = df.rename(columns={
    "Close": "preco_fechamento",
    "High": "preco_maximo",
    "Low": "preco_minimo",
    "Open": "preco_abertura",
    "Volume": "volume_negociado",
    "Date": "data"
})

# Cria colunas derivadas
df["variacao_diaria"] = df["preco_fechamento"] - df["preco_abertura"]
df["percentual_variacao"] = (
    (df["preco_fechamento"] - df["preco_abertura"]) / df["preco_abertura"]
) * 100

# Cria agregações de exemplo (média semanal)
df["semana"] = pd.to_datetime(df["data"]).dt.isocalendar().week
agg = (
    df.groupby("semana")
    .agg({
        "preco_fechamento": "mean",
        "volume_negociado": "sum",
        "variacao_diaria": "mean"
    })
    .reset_index()
)

# Nomeia colunas agregadas
agg = agg.rename(columns={
    "preco_fechamento": "media_preco_fechamento",
    "volume_negociado": "soma_volume_negociado",
    "variacao_diaria": "media_variacao_diaria"
})

# Salva parquet refinado
output_path = REFINED_DIR / "ibov_refined.parquet"
agg.to_parquet(output_path, index=False)

print(f"✅ Transformação concluída e salva em: {output_path}")
print(f"📊 Linhas: {len(agg)} | Colunas: {list(agg.columns)}")
