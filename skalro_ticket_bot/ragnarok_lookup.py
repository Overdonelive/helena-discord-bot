import json
import os
import re
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

import config


client_openai = OpenAI(api_key=config.OPENAI_API_KEY)

ARQUIVO_ITEM_ALIASES = "item_aliases.json"
ARQUIVO_MONSTER_ALIASES = "monster_aliases.json"
ARQUIVO_MAP_ALIASES = "map_aliases.json"


# =========================
# FALLBACKS MÍNIMOS
# =========================

ITEM_ALIASES_PADRAO = {
    "chifres pontudos": "Spike Band",
    "chifre pontudo": "Spike Band",
}

MONSTER_ALIASES_PADRAO = {
    "esporo": "Spore",
    "lunático": "Lunatic",
    "lunatico": "Lunatic",
    "senhor dos orcs": "Orc Lord",
    "herói orc": "Orc Hero",
    "heroi orc": "Orc Hero",
}

MAP_ALIASES_PADRAO = {
    "caverna de payon": "Payon Cave",
    "torre sem fim": "Endless Tower",
}


# =========================
# JSON HELPERS
# =========================

def carregar_json_aliases(caminho, fallback_dict):
    if not os.path.exists(caminho):
        return fallback_dict.copy()

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return {k.lower().strip(): v.strip() for k, v in data.items()}

        if isinstance(data, list):
            convertido = {}
            for item in data:
                pt = str(item.get("pt_br", "")).strip().lower()
                en = str(item.get("en", "")).strip()
                if pt and en:
                    convertido[pt] = en
            return convertido

        return fallback_dict.copy()

    except Exception as e:
        print(f"Erro carregando aliases {caminho}: {e}")
        return fallback_dict.copy()


ITEM_ALIASES_RMS = carregar_json_aliases(ARQUIVO_ITEM_ALIASES, ITEM_ALIASES_PADRAO)
MONSTER_ALIASES_RMS = carregar_json_aliases(ARQUIVO_MONSTER_ALIASES, MONSTER_ALIASES_PADRAO)
MAP_ALIASES_RMS = carregar_json_aliases(ARQUIVO_MAP_ALIASES, MAP_ALIASES_PADRAO)


# =========================
# EXTRAÇÃO DE PERGUNTA
# =========================

def extrair_pergunta_relevante(texto):
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

    for i, linha in enumerate(linhas):
        linha_lower = linha.lower()
        if "descrição detalhada" in linha_lower or "descricao detalhada" in linha_lower:
            if i + 1 < len(linhas):
                return linhas[i + 1].strip()

    for linha in reversed(linhas):
        if any(chave in linha.lower() for chave in [
            "onde", "drop", "mob", "monstro", "item", "wiki",
            "como funciona", "como faço", "mapa", "?"
        ]):
            return linha.strip()

    return linhas[-1] if linhas else texto.strip()


def extrair_termo_busca(texto):
    texto = texto.lower().strip().replace("?", "")

    padroes = [
        r"onde eu dropo o item (.+)",
        r"onde eu dropo (.+)",
        r"onde dropo o item (.+)",
        r"onde dropo a carta (.+)",
        r"onde dropo (.+)",
        r"onde dropa o item (.+)",
        r"onde dropa (.+)",
        r"onde acho o item (.+)",
        r"onde acho (.+)",
        r"onde encontro o item (.+)",
        r"onde encontro (.+)",
        r"onde consigo dropar (.+)",
        r"drop de (.+)",
        r"dropa de (.+)",
        r"qual mob dropa (.+)",
        r"que monstro dropa (.+)",
        r"onde encontro o monstro (.+)",
        r"onde acho o monstro (.+)",
        r"onde fica (.+)",
        r"como chego em (.+)",
        r"mapa de (.+)",
    ]

    for padrao in padroes:
        m = re.search(padrao, texto)
        if m:
            return m.group(1).strip()

    return texto.strip()


def detectar_tipo_entidade(pergunta):
    p = pergunta.lower()

    if any(x in p for x in [
        "onde dropo", "onde dropa", "drop de", "item", "equipamento", "carta"
    ]):
        return "item"

    if any(x in p for x in [
        "qual mob", "que monstro", "onde acho o monstro",
        "onde encontro o monstro", "mob", "monstro"
    ]):
        return "monster"

    if any(x in p for x in [
        "mapa", "como chego", "onde fica"
    ]):
        return "map"

    return "item"


# =========================
# NORMALIZAÇÃO PT -> EN
# =========================

def normalizar_nome_ragnarok_para_ingles(termo_pt, tipo="item"):
    termo_limpo = termo_pt.strip().lower()

    if tipo == "item" and termo_limpo in ITEM_ALIASES_RMS:
        nome_alias = ITEM_ALIASES_RMS[termo_limpo]
        print(f"Alias local encontrado (item): {termo_pt} -> {nome_alias}")
        return nome_alias

    if tipo == "monster" and termo_limpo in MONSTER_ALIASES_RMS:
        nome_alias = MONSTER_ALIASES_RMS[termo_limpo]
        print(f"Alias local encontrado (monster): {termo_pt} -> {nome_alias}")
        return nome_alias

    if tipo == "map" and termo_limpo in MAP_ALIASES_RMS:
        nome_alias = MAP_ALIASES_RMS[termo_limpo]
        print(f"Alias local encontrado (map): {termo_pt} -> {nome_alias}")
        return nome_alias

    try:
        response = client_openai.responses.create(
            model=config.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": f"""Você é especialista em Ragnarok Online.

Converta nomes de {tipo}s do Ragnarok em português para o nome EXATO em inglês usado em databases como RateMyServer.

Regras:
- Responda apenas com o nome final.
- Não explique.
- Não use aspas.
- Se já estiver em inglês, devolva igual.
- Priorize o nome exato do RateMyServer.
- Se não tiver certeza absoluta, devolva a melhor correspondência provável.
- Exemplo importante:
  Chifres pontudos -> Spike Band
"""
                },
                {
                    "role": "user",
                    "content": termo_pt
                }
            ]
        )

        nome_final = response.output_text.strip()
        print(f"Fallback OpenAI ({tipo}): {termo_pt} -> {nome_final}")
        return nome_final if nome_final else termo_pt

    except Exception as e:
        print(f"Erro ao normalizar nome Ragnarok: {e}")
        return termo_pt


# =========================
# HTTP / PARSE
# =========================

def _baixar_html(url):
    try:
        r = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if r.status_code != 200:
            return ""
        return r.text
    except Exception as e:
        print(f"Erro baixando URL {url}: {e}")
        return ""


def _limpar_texto_html(html, limite=7000):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text("\n", strip=True)
    return texto[:limite]


# =========================
# BUSCA RMS
# =========================

def buscar_drop_item_rms(pergunta_original):
    """
    Fluxo:
    1. extrai a pergunta relevante
    2. identifica o termo do item
    3. resolve PT-BR -> nome exato RMS, priorizando alias local
    4. busca no RMS
    5. devolve contexto bruto para a OpenAI organizar
    """
    pergunta_relevante = extrair_pergunta_relevante(pergunta_original)
    tipo = detectar_tipo_entidade(pergunta_relevante)
    termo_pt = extrair_termo_busca(pergunta_relevante)
    termo_en = normalizar_nome_ragnarok_para_ingles(termo_pt, tipo=tipo)

    # Para item continua usando busca de item
    if tipo == "item":
        url_busca = f"https://ratemyserver.net/index.php?iname={quote_plus(termo_en)}&isearch=Search&page=item_db"
    elif tipo == "monster":
        url_busca = f"https://ratemyserver.net/index.php?page=mob_db&mob_name={quote_plus(termo_en)}"
    else:
        url_busca = f"https://ratemyserver.net/index.php?iname={quote_plus(termo_en)}&isearch=Search&page=item_db"

    html_busca = _baixar_html(url_busca)
    contexto_busca = _limpar_texto_html(html_busca, limite=7000)

    print("=== BUSCA RAGNAROK ===")
    print("Pergunta original:", pergunta_original)
    print("Pergunta relevante:", pergunta_relevante)
    print("Tipo detectado:", tipo)
    print("Termo PT:", termo_pt)
    print("Termo EN/RMS:", termo_en)
    print("Busca RMS:", url_busca)
    print("Contexto RMS encontrado:", "SIM" if contexto_busca else "NÃO")

    return {
        "found": bool(contexto_busca),
        "source": "ratemyserver",
        "entity_type": tipo,
        "query_pt": termo_pt,
        "query_en": termo_en,
        "search_url": url_busca,
        "context": contexto_busca
    }


# =========================
# BUSCA WIKI
# =========================

def buscar_wiki_skalro(pergunta):
    try:
        pergunta_relevante = extrair_pergunta_relevante(pergunta)
        termo = quote_plus(pergunta_relevante)
        url = f"https://www.skalro.com.br/wiki/?s={termo}"

        html = _baixar_html(url)
        contexto = _limpar_texto_html(html, limite=5000)

        print("=== BUSCA WIKI SKALRO ===")
        print("Pergunta original:", pergunta)
        print("Pergunta relevante:", pergunta_relevante)
        print("URL wiki:", url)
        print("Contexto wiki encontrado:", "SIM" if contexto else "NÃO")

        return {
            "found": bool(contexto),
            "source": "wiki_skalro",
            "url": url,
            "context": contexto
        }

    except Exception as e:
        print(f"Erro wiki SkålRO: {e}")
        return {
            "found": False,
            "source": "wiki_skalro",
            "url": "",
            "context": ""
        }