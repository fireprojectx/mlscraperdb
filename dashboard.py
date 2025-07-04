
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Baixar dados da API
url = "https://mlscraperdb-production.up.railway.app/historico_todas_consultas"
response = requests.get(url)
data = response.json()

# Criar DataFrame
df = pd.DataFrame(data)

# Converter colunas de data
df["data_consulta"] = pd.to_datetime(df["data_consulta"], errors="coerce")
df["data_inicio"] = pd.to_datetime(df["data_inicio"], errors="coerce")

# Remover dados incompletos
df = df.dropna(subset=["data_consulta", "vendidos", "titulo"])

# Agrupar por produto (exibir os 3 mais consultados)
top_titulos = df["titulo"].value_counts().head(3).index
df_top = df[df["titulo"].isin(top_titulos)]

# Plotar
plt.figure(figsize=(12, 6))
for titulo in top_titulos:
    produto_df = df_top[df_top["titulo"] == titulo]
    plt.plot(produto_df["data_consulta"], produto_df["vendidos"], marker='o', label=titulo)

plt.xlabel("Data da Consulta")
plt.ylabel("Quantidade Vendida")
plt.title("Evolução de Vendas - Produtos Mais Consultados")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("public/dashboard.png")
