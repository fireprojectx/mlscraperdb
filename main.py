from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from scraper import extrair_dados_produto

app = FastAPI()

@app.get("/scrape/")
def scrape_product(url: str):
    try:
        return extrair_dados_produto(url)
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
