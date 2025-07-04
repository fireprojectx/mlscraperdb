from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from scraper import extrair_dados_produto
from db import get_connection
from datetime import datetime
import os

app = FastAPI()

# ------------------------------
# Rota principal de scraping
# ------------------------------
@app.get("/scrape/")
def scrape_product(url: str):
    try:
        data = extrair_dados_produto(url) 
        salvar_no_banco(data, url)         
        return data                         
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# Salva no banco
# ------------------------------

def salvar_no_banco(dados, url):
    conn = get_connection()
    cur = conn.cursor()

    data_agora = datetime.now()  # pega data e hora atual

    cur.execute(
        """
        INSERT INTO consultas (url, titulo, preco, vendidos, data_inicio, data_consulta)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            url,
            dados.get("Título"),
            dados.get("Preço"),
            dados.get("Vendidos"),
            dados.get("DataInicio"),
            data_agora  # nova coluna
        )
    )
    conn.commit()
    cur.close()
    conn.close()

# ------------------------------
# Rota para histórico de produto
# ------------------------------
@app.get("/historico")
def obter_historico(url: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT titulo, preco, vendidos, data_inicio, data_consulta, url
            FROM consultas
            WHERE url = %s
            ORDER BY data_consulta ASC
        """, (url,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return JSONResponse(content=[], status_code=200)

        dados = [
            {
                "titulo": row[0],
                "preco": row[1],
                "vendidos": row[2],
                "data_inicio": row[3],
                "data_consulta": str(row[4]),
                "url": row[5]
            }
            for row in rows
        ]

        return JSONResponse(content=dados)

    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})

# ------------------------------
# consultar urls pesquisadas
# ------------------------------
@app.get("/historico_urls")
def obter_urls_com_datas():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT url, MAX(data_consulta) AS primeira_consulta
            FROM consultas
            GROUP BY url
            ORDER BY primeira_consulta ASC
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        dados = [
            {
                "url": row[0],
                "data_consulta": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else None
            }
            for row in rows
        ]

        return JSONResponse(content=dados)

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)

# --------------------------
# Retorna todas as pesquisas
# --------------------------
@app.get("/historico_todas_consultas")
def obter_todas_consultas():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT url, data_consulta, titulo, vendidos
            FROM consultas
            ORDER BY url, data_consulta ASC
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        dados = [
            {
                "url": row[0],
                "data_inicio": row[1],
                "data_consulta": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else None,
                "titulo": row[3],
                "vendidos": row[4],
                "preco": row[5]                
            }
            for row in rows
        ]

        return JSONResponse(content=dados)

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
        
# ------------------------------
# Servir arquivos estáticos (frontend)
# ------------------------------
app.mount("/", StaticFiles(directory="public", html=True), name="static")
