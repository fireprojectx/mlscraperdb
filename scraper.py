import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extrair_dados_produto(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resposta = requests.get(url, headers=headers)
    if resposta.status_code != 200:
        return {"Erro": f"Erro ao acessar a página: {resposta.status_code}"}

    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Título
    titulo_tag = soup.find("h1", class_="ui-pdp-title")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Não encontrado"

    # Preço
    meta_price_tag = soup.find("meta", itemprop="price")
    preco = f'R${meta_price_tag["content"]}' if meta_price_tag else "Não encontrado"

    # Vendidos
    vendidos_tag = soup.find("span", string=re.compile(r"[0-9].*vendid", re.I))
    vendidos = vendidos_tag.get_text(strip=True) if vendidos_tag else "Não encontrado"

    # startTime no script da página
    starttime = "Não encontrado"
    match = re.search(r'"startTime"\s*:\s*"([^"]+)"', resposta.text)
    if match:
        raw_date = match.group(1)
        try:
            data_obj = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
            starttime = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            starttime = raw_date

    return {
        "Título": titulo,
        "Preço": preco,
        "Vendidos": vendidos,
        "DataInicio": starttime
    }
