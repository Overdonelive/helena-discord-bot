import re
from typing import Optional, Dict, List


def limpar_linha(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "")).strip()


def parece_mensagem_helena(texto: str) -> bool:
    t = (texto or "").lower()

    padroes = [
        "isso resolveu seu problema",
        "responda com:",
        "ratemyserver",
        "wiki do skalro",
        "wiki do skålro",
        "vou encaminhar",
        "encaminhar para a equipe",
        "perfeito! que bom que deu certo",
        "se surgir qualquer outra dúvida",
        "esse caso precisa de verificação manual",
        "entendi! confira estes links",
    ]

    return any(p in t for p in padroes)


def parece_mensagem_ruim_para_memoria(texto: str) -> bool:
    t = (texto or "").lower().strip()

    ruins = {
        "resolvido",
        "resolveu",
        "sim",
        "ok",
        "oks",
        "blz",
        "beleza",
        "up",
        "teste",
        "não funcionou",
        "nao funcionou",
        "funcionou",
    }

    return (
        t in ruins
        or len(t) < 3
        or parece_mensagem_helena(t)
    )


def separar_blocos_linhas(conteudo: str) -> List[str]:
    linhas = [limpar_linha(x) for x in (conteudo or "").splitlines()]
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


def extrair_conversa_staff_util(conteudo: str) -> Optional[str]:
    """
    Em vez de pegar só a última resposta,
    tenta montar um bloco com a conversa útil da staff.
    """
    linhas = separar_blocos_linhas(conteudo)

    candidatos = []

    for linha in linhas:
        if parece_mensagem_ruim_para_memoria(linha):
            continue

        ll = linha.lower()

        # ignora partes visuais comuns de transcript
        if any(x in ll for x in [
            "ticket closed by",
            "support team ticket controls",
            "transcript",
            "open",
            "delete",
            "close",
            "tickettool",
            "ticket tool",
            "bem-vindo",
            "este é o começo do canal",
            "um membro da equipe já foi notificado",
            "para agilizar seu atendimento",
            "usuário da conta em questão",
            "nome de um personagem na conta",
            "assunto",
            "descrição detalhada",
        ]):
            continue

        candidatos.append(linha)

    if not candidatos:
        return None

    # pega os últimos blocos úteis e junta
    ultimos = candidatos[-6:]
    texto_final = "\n".join(ultimos).strip()

    return texto_final if texto_final else None


def extrair_aprendizado_do_transcript(conteudo: str) -> Optional[Dict[str, str]]:
    pergunta = extrair_pergunta_do_player(conteudo)
    resposta = extrair_conversa_staff_util(conteudo)

    if not pergunta or not resposta:
        return None

    if pergunta.strip().lower() == resposta.strip().lower():
        return None

    return {
        "pergunta": pergunta.strip(),
        "resposta": resposta.strip()
    }