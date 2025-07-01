from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from scraper import extrair_dados_produto
import os
from fastapi.responses import JSONResponse
from db import get_connection

app = FastAPI()

@app.get("/scrape/")
def scrape_product(url: str):
    try:
        data = extrair_dados_produto(url) 
        salvar_no_banco(data, url)         
        return data                         
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
app.mount("/", StaticFiles(directory="public", html=True), name="static")



# Inserção no banco após scraping
from db import get_connection

def salvar_no_banco(dados, url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO consultas (url, titulo, preco, vendidos, data_inicio)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            url,
            dados.get("Título"),
            dados.get("Preço"),
            dados.get("Vendidos"),
            dados.get("DataInicio")
        )
    )
    conn.commit()
    cur.close()
    conn.close()



@app.get("/historico")
def obter_historico():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT titulo, preco, vendidos, data_inicio, data_consulta, url
            FROM consultas
            ORDER BY data_consulta DESC
        """)
        rows = cur.fetchall()

        colunas = [desc[0] for desc in cur.description]
        dados = [dict(zip(colunas, linha)) for linha in rows]

        cur.close()
        conn.close()

        return JSONResponse(content=dados)
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})



