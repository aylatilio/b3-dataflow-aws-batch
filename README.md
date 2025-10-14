🔗 Repositório: [github.com/aylatilio/b3-dataflow-aws-batch](https://github.com/aylatilio/b3-dataflow-aws-batch.git)

# 🏦 b3-dataflow-aws-batch
Pipeline de dados batch na AWS para ingestão, transformação e análise do índice IBOVESPA, com automação via S3, Lambda, Glue e Athena.

---

## 👩‍💻 Autoria
**Ayla Atilio**  
📚 Pós-graduação em Machine Learning Engineering — FIAP  
🐍 Python | ☁️ AWS | 📊 Data Engineering  
🔗 [linkedin.com/in/aylaatilio](https://linkedin.com/in/aylaatilio)  
🔗 [github.com/aylatilio](https://github.com/aylatilio)

---

## 📘 Visão Geral
Este projeto demonstra a implementação de um **pipeline batch de engenharia de dados** na **AWS**, utilizando dados públicos da **B3 (Bolsa de Valores do Brasil)**.  

O fluxo realiza **ingestão, transformação, catalogação e análise** de dados históricos do **índice IBOVESPA**, com automação baseada em eventos no S3 e consultas via Athena.  
Projeto desenvolvido como parte do **Tech Challenge 2 — FIAP (Machine Learning Engineering)**.

---

### 🚀 Objetivo
Demonstrar um pipeline de **dados escalável, modular e automatizado**, que conecta serviços da AWS em um fluxo **end-to-end**:

**S3 (armazenamento) → Lambda (orquestração) → Glue (ETL) → Athena (análise)**

---

## 🧱 Arquitetura

```mermaid
flowchart TD
    A["📈 yfinance API (IBOV data)"] --> B(["🪣 S3 Bucket raw/ parquet partitioned"])
    B -->|⚡ S3 Event Trigger| C(["⚙️ AWS Lambda"])
    C --> D(("🧩 AWS Glue Job ETL Transformation"))
    D --> E(["💾 S3 Bucket refined/ parquet + partitions"])
    E --> F{{"📚 AWS Glue Crawler & Data Catalog"}}
    F --> G["🔍 Amazon Athena SQL Queries & Analytics"]
```

📈 Fonte de dados: API Yahoo Finance (yfinance)  
💾 Armazenamento: AWS S3 (camadas raw e refined)  
⚙️ Orquestração: AWS Lambda + Glue Job ETL  
📚 Catálogo e Consulta: AWS Glue Catalog + Amazon Athena

---

## 🗂️ Estrutura
```plaintext
b3-dataflow-aws-batch/
│
├── data/
│   ├── raw/               		 # dados brutos (Parquet)
│   └── refined/           		 # dados transformados localmente
│
├── src/
│   ├── extract_ibov.py          # extração e ingestão de dados do IBOV via yfinance
│   ├── upload_s3.py             # upload automático para o S3 bucket raw/
│   ├── lambda_trigger.py        # função Lambda (dispara o Glue Job)
│   ├── glue_job_etl.py          # ETL rodando no AWS Glue
│   └── glue_job_etl_local.py    # Simulação local do Glue Job
│
├── notebooks/ 
│   └── athena_queries.ipynb  	 # consultas Athena e análises
│
├── docs/                        # documentação e diagramas
│   └── diagrams/
│       ├── architecture.mmd
│       └── architecture.png
│
├── requirements.txt
├──.env.example   
└── README.md
```
---

## 📘 Notebook Overview — athena_queries.ipynb

O notebook consolida a etapa final do pipeline analítico, validando a integração entre as camadas do AWS Data Lake (S3, Glue, Athena) e o consumo analítico em Python. 

🧩 Bloco 1 — Query de preview via boto3
Executa uma consulta simples no serviço Amazon Athena, mas a partir do código Python (boto3), retornando o QueryExecutionId e validando a comunicação programática entre o Glue Catalog e o Athena. 
A mesma query é usada para exibir uma amostra dos 10 registros mais recentes da camada refined, permitindo validar o schema, as partições e a integridade dos dados transformados pelo AWS Glue Job.

💡 Esse bloco garante que o pipeline consegue acionar o Athena via API. 

⚙️ Bloco 2 — Query analítica (volatilidade e amplitude)
Envia uma consulta ao Athena via awswrangler, retornando um DataFrame pandas enriquecido com features derivadas (amplitude, volatilidade_pct). 
Identifica os dias com maior volatilidade (diferença entre high e low) e volume negociado, destacando potenciais eventos de pico no índice IBOVESPA em 2025. 
Essa análise é base para estudos exploratórios e criação de features temporais (rolling mean, z-score) ou integração com modelos de detecção de anomalias (Isolation Forest, Autoencoders).

💡 Esse bloco comprova que o dataset refinado está pronto para análises quantitativas.

📊 Bloco 3 — Query agregada de estatísticas
Calcula medidas de resumo (média, máximo e mínimo) sobre os preços do IBOVESPA na camada refined, filtrando o ano de 2025. 
Serve como checagem de consistência pós-ETL, garantindo que os valores numéricos transformados no Glue Job mantêm coerência com o comportamento esperado do índice.

💡 Bloco de verificação — assegura que a transformação no Glue não alterou escalas ou integridade dos dados.

🧠 Bloco 4 — Feature Engineering / Isolation Forest Prep
Realiza cálculos de média móvel, desvio padrão móvel e z-score a partir da coluna volatilidade_pct, derivada no bloco anterior. Com esses indicadores, é criada a variável volatilidade_pico, 
que recebe valor 1 quando o z-score ultrapassa 1.5 desvios padrão acima da média, sinalizando períodos de alta volatilidade, potenciais outliers do comportamento normal do índice.

💡 Essa etapa prepara o dataset para uso em algoritmos de detecção de anomalias, como Isolation Forest, Autoencoders ou DBSCAN, permitindo identificar variações extremas e regimes de mercado atípicos. 

Raw → Refined → Glue → Athena → Python → Feature Engineering

Raw: dados ingeridos e armazenados em S3 (parquet bruto)
Glue: ETL transforma e grava camada refined 
Athena: consulta SQL no catálogo do Glue
Python: acesso programático e análise via boto3/awswrangler
Feature Engineering: cálculo de métricas e preparação para ML

---

## 🧩 Lambda Trigger — Glue Orchestration
A função `lambda_trigger_glue_job` monitora o bucket *Raw* (`b3-dataflow-raw/raw/`) e,
ao detectar um novo arquivo `.parquet`, dispara automaticamente o Glue Job `b3-etl-job`.
Essa automação conecta as camadas do pipeline S3 → Lambda → Glue → S3 Refined,
eliminando a necessidade de execução manual.

🔄 Pipeline de Execução — End-to-End Flow
O projeto implementa um pipeline totalmente automatizado que vai da extração local à análise via Athena, integrando componentes locais e serviços AWS: 

# S3 (raw) → Lambda Trigger → Glue Job → S3 (refined)

| Etapa                          | Ambiente                 | Descrição                                                                                                                                              |
| :----------------------------- | :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🐍 **extract_ibov.py**         | Local (VS Code)          | Extrai dados do índice IBOVESPA via `yfinance` e gera o arquivo parquet bruto (`data/raw/`).                                                           |
| ☁️ **upload_s3.py**            | Local                    | Faz o upload automático do parquet gerado para o bucket S3 `b3-dataflow-raw/raw/`.                                                                     |
| ⚡ **lambda_trigger.py**        | AWS Lambda               | Monitora o bucket `raw/` e, ao detectar um novo arquivo `.parquet`, dispara o Glue Job automaticamente.                                                |
| 🧩 **Glue Job (`b3-etl-job`)** | AWS Glue                 | Executa o processo ETL: transforma, particiona e grava o dataset refinado em `b3-dataflow-refined/`.                                                   |
| 📊 **athena_queries.ipynb**    | Local (Jupyter Notebook) | Conecta-se ao Athena via `boto3` e `awswrangler` para consultar e analisar os dados refinados (volatilidade, amplitude, estatísticas agregadas, etc.). |

💡 Esse fluxo garante rastreabilidade completa entre a ingestão, transformação e análise dos dados na nuvem.

| Componente                | Função                                                    |
| ------------------------- | --------------------------------------------------------- |
| **extract_ibov.py**       | Gera parquet local com sucesso                            |
| **upload_s3.py**          | Upload validado via AWS CLI                               |
| **lambda_trigger.py**     | Dispara Glue Job após upload                              |
| **glue_job_etl.py**       | Roda com sucesso no AWS Glue                              |
| **glue_job_etl_local.py** | Gera `ibov_refined.parquet` localmente                    |
| **Bucket Raw**            | Contém parquet do dia 13/10                               |
| **Bucket Refined**        | Contém parquet refinado gerado                            |
| **Glue Catalog / Athena** | Tabela `ibov_refined` disponível e consultável via Athena |

---

## ⚙️ Requisitos e Execução do Pipeline
```plaintext
🧩 Pré-requisitos
	Python 3.11.9 (recomendado pela estabilidade com awswrangler, pandas e boto3)
	Conta AWS com permissões nos serviços:
		S3 (leitura e escrita)
		Glue (job, crawler e catalog)
		Lambda (execução e logs)
		Athena (consultas)
	Credenciais AWS configuradas localmente (aws configure)
	Ambiente virtual Python ativo (venv)
	
🚀 Etapas de Execução
1. Configuração do ambiente
	Crie e ative o ambiente virtual:
		python -m venv venv
		source venv/bin/activate      # Linux/Mac
		venv\Scripts\activate         # Windows
		
	Instale as dependências:
		pip install -r requirements.txt
		
2. Ingestão e extração de dados:
		python src/extract_ibov.py
	
	Baixa as cotações recentes do IBOVESPA a partir da API Yahoo Finance e salva em formato Parquet particionado:
		python src/extract_ibov.py
	Arquivo Parquet salvo localmente em data/raw/year=YYYY/month=MM/day=DD/ibov.parquet
	
3. Upload para o Amazon S3
	Envie os dados gerados para o bucket S3 (camada raw):
		python src/upload_s3.py
	Arquivo Parquet disponível em s3://b3-dataflow-raw/raw/year=YYYY/month=MM/day=DD/ibov.parquet
	
4. Orquestração automática via Lambda
	O AWS Lambda Trigger detecta automaticamente o novo arquivo na camada raw e executa o Glue Job ETL configurado no console AWS:
		Transforma os dados (média móvel, amplitude, volatilidade etc.)
		Salva o resultado em s3://b3-dataflow-refined/refined/...
		Atualiza o Glue Catalog via Crawler
	Logs no CloudWatch (b3-etl-job)
	
5. Consulta e análise
	Após a conclusão do ETL, as consultas podem ser feitas:
		Diretamente no Amazon Athena (console web), ou
		Localmente via notebook notebooks/athena_queries.ipynb
	Execute localmente para validar a leitura do Glue Catalog e gerar análises:
		python -m notebook
	
	Resultados esperados:
		Query de preview (boto3) → valida a conectividade
		Query analítica (awswrangler) → gera amplitude e volatilidade_pct
		Query agregada → valida consistência
		Feature engineering (pandas) → prepara para Isolation Forest

6. Visualização e Validação
	Verifique no S3 as pastas raw e refined
	Confirme a tabela b3_refined_db no Glue Catalog
	Execute queries no Athena
	Visualize o DataFrame enriquecido e as features criadas no notebook

* Para testes rápidos, também é possível executar o Glue Job manualmente no console e validar o output no Athena antes de ativar o trigger Lambda.
```

---

🔍 Consulta SQL no Amazon Athena

Após o crawler atualizar o catálogo (b3_refined_db.ibov_refined), as consultas podem ser executadas diretamente no Athena.
Exemplo de query analítica validada durante os testes:
```sql
SELECT
    data,
    preco_abertura,
    preco_fechamento,
    (preco_fechamento - preco_abertura) AS variacao_diaria,
    ROUND(((preco_fechamento - preco_abertura) / preco_abertura) * 100, 2) AS variacao_pct,
    volume_negociado
FROM "b3_refined_db"."ibov_refined"
WHERE year = 2025 AND month = 10
ORDER BY data DESC
LIMIT 10;
```

📊 Resultado esperado (amostra):
| data       | preco_abertura | preco_fechamento | variacao_diaria | variacao_pct | volume_negociado |
| ---------- | -------------- | ---------------- | --------------- | ------------ | ---------------- |
| 2025-10-13 | 127.845,00     | 128.430,00       | 585,00          | 0.46 %       | 13 245 200       |
| 2025-10-10 | 128.290,00     | 127.845,00       | −445,00         | −0.35 %      | 12 988 500       |
| …          | …              | …                | …               | …            | …                |

💡 Resultado do Pipeline: dados transformados acessíveis no Athena, com colunas renomeadas e cálculos derivados gerados pelo Glue Job.

---

## 🧠 Conclusão
O pipeline demonstra a integração completa de serviços AWS para ingestão, transformação e análise de dados de mercado.
A arquitetura implementa boas práticas de Data Lake (camadas raw/refined), ETL automatizado via Glue e análise com Athena, garantindo escalabilidade e rastreabilidade.
As features geradas (volatilidade, amplitude, z-score) servem como base para futuras aplicações de Machine Learning, como detecção de anomalias com Isolation Forest.

---

## 🔗 Referências
- [Yahoo Finance API (yfinance)](https://pypi.org/project/yfinance/)
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/index.html)
- [Amazon Athena Documentation](https://docs.aws.amazon.com/athena/)
- [Mermaid Live Editor](https://mermaid.live)
