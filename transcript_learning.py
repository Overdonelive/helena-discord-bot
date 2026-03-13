import re
from typing import Optional, Dict, List


def limpar_linha(texto: str) -> str:
    return re.sub(r"\s+", " ", texto or "").strip()


def parece_mensagem_helena(texto: str) -> bool:
    t = (texto or "").lower()
    padroes = [
        "isso resolveu seu problema",
        "responda com:",
        "rate myserver",
        "rate myserver:",
        "wiki do skalro",
        "wiki do skålro",
        "vou encaminhar",
        "entendi! confira estes links",
        "perfeito! que bom que deu certo",
    ]
    return any(p in t for p in padroes)


def parece_mensagem_ruim_para_memoria(texto: str) -> bool:
    t = (texto or "").lower().strip()
    ruins = {
        "resolvido",
        "resolveu",
        "sim",
        "ok",
        "blz",
        "beleza",
        "up",
        "teste",
    }
    return t in ruins or len(t) < 8 or parece_mensagem_helena(t)


def separar_blocos_linhas(conteudo: str) -> List[str]:
    linhas = [limpar_linha(x) for x in conteudo.splitlines()]
    return [x for x in linhas if x]


def extrair_pergunta_do_player(conteudo: str) -> Optional[str]:
    linhas = separar_blocos_linhas(conteudo)

    for i, linha in enumerate(linhas):
        ll = linha.lower()
        if "descrição detalhada" in ll or "descricao detalhada" in ll:
            if i + 1 < len(linhas):
                prox = linhas[i + 1]
                if prox:
                    return prox

    candidatos = []
    for linha in linhas:
        ll = linha.lower()
        if any(chave in ll for chave in [
            "onde",
            "drop",
            "bug",
            "erro",
            "nao funcionou",
            "não funcionou",
            "xingou",
            "ks",
            "racismo",
            "homofobia",
            "machismo",
            "?",
        ]):
            candidatos.append(linha)

    return candidatos[-1] if candidatos else None


def extrair_ultima_resposta_staff(conteudo: str) -> Optional[str]:
    linhas = separar_blocos_linhas(conteudo)

    candidatos = []
    for linha in linhas:
        if parece_mensagem_ruim_para_memoria(linha):
            continue
        candidatos.append(linha)

    if not candidatos:
        return None

    return candidatos[-1]


def extrair_aprendizado_do_transcript(conteudo: str) -> Optional[Dict[str, str]]:
    pergunta = extrair_pergunta_do_player(conteudo)
    resposta = extrair_ultima_resposta_staff(conteudo)

    if not pergunta or not resposta:
        return None

    if pergunta.strip().lower() == resposta.strip().lower():
        return None

    return {
        "pergunta": pergunta.strip(),
        "resposta": resposta.strip()
    }