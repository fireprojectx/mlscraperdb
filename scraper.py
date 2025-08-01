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

    # Data de início do anúncio
    starttime = None
    dias_ativo = 0

    match = re.search(r'"startTime"\s*:\s*"([^"]+)"', resposta.text)
    if match:
        raw_date = match.group(1)
        try:
            # Tenta com milissegundos e Z
            data_obj = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                # Tenta sem milissegundos
                data_obj = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                data_obj = None

        if data_obj:
            starttime = data_obj.strftime("%d/%m/%Y")
            dias_ativo = (datetime.utcnow() - data_obj).days + 1
        else:
            starttime = None

    # Avaliações
    avaliacoes_tag = soup.find("span", class_="ui-pdp-review__amount")
    if avaliacoes_tag:
        avaliacoes_texto = avaliacoes_tag.get_text(strip=True)
        match = re.search(r"\((\d+)\)", avaliacoes_texto)
        avaliacoes = match.group(1) if match else "Não encontrado"
    else:
        avaliacoes = "Não encontrado"

   # Conversão de avaliações para inteiro
    try:
        avaliacoes_int = int(avaliacoes)
    except:
        avaliacoes_int = 0

    # Conversão de vendidos para inteiro (extração do número bruto de "+50 vendidos")
    vendidos_int = 0
    if vendidos != "Não encontrado":
        match = re.search(r"(\d+)", vendidos.replace(".", ""))
        if match:
            vendidos_int = int(match.group(1))

    # Estimativa mais realista de visitas
    visitas_estimadas = vendidos_int * 50 + avaliacoes_int * 100 + dias_ativo

    

    # Nota de avaliação
    nota_tag = soup.find("span", class_="ui-pdp-review__rating")
    nota_avaliacao = nota_tag.get_text(strip=True) if nota_tag else "Não encontrado"

    return {
        "Título": titulo,
        "Preço": preco,
        "Vendidos": vendidos,
        "DataInicio": starttime,
        "Avaliações": avaliacoes,
        "Nota": nota_avaliacao,
        "Visitas": str(visitas_estimadas)
    }
