import json
import os
from difflib import SequenceMatcher

ARQUIVO_MEMORIA = "tickets_memory.json"


def carregar_memoria():
    if not os.path.exists(ARQUIVO_MEMORIA):
        return []

    try:
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def salvar_memoria(memoria):
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)


def normalizar_texto(texto):
    return (texto or "").strip().lower()


def similaridade(a, b):
    return SequenceMatcher(None, normalizar_texto(a), normalizar_texto(b)).ratio()


def adicionar_memoria(pergunta, resposta, categoria):
    memoria = carregar_memoria()

    registro = {
        "pergunta": (pergunta or "").strip(),
        "resposta": (resposta or "").strip(),
        "categoria": (categoria or "").strip()
    }

    memoria.append(registro)
    salvar_memoria(memoria)


def adicionar_memoria_se_nao_existir(pergunta, resposta, categoria):
    memoria = carregar_memoria()

    pergunta_norm = normalizar_texto(pergunta)
    resposta_norm = normalizar_texto(resposta)
    categoria_norm = normalizar_texto(categoria)

    for item in memoria:
        if (
            normalizar_texto(item.get("pergunta")) == pergunta_norm and
            normalizar_texto(item.get("resposta")) == resposta_norm and
            normalizar_texto(item.get("categoria")) == categoria_norm
        ):
            return False

    registro = {
        "pergunta": (pergunta or "").strip(),
        "resposta": (resposta or "").strip(),
        "categoria": (categoria or "").strip()
    }

    memoria.append(registro)
    salvar_memoria(memoria)
    return True


def buscar_memoria_semelhante(pergunta, categoria=None, limite=0.72):
    memoria = carregar_memoria()

    melhor_item = None
    melhor_score = 0

    pergunta_norm = normalizar_texto(pergunta)
    categoria_norm = normalizar_texto(categoria) if categoria else None

    for item in memoria:
        if categoria_norm and normalizar_texto(item.get("categoria")) != categoria_norm:
            continue

        score = similaridade(pergunta_norm, item.get("pergunta", ""))

        if score > melhor_score:
            melhor_score = score
            melhor_item = item

    if melhor_item and melhor_score >= limite:
        return {
            "found": True,
            "score": melhor_score,
            "item": melhor_item
        }

    return {
        "found": False,
        "score": melhor_score,
        "item": None
    }


def listar_memoria():
    return carregar_memoria()


def contar_memorias():
    return len(carregar_memoria())


def limpar_memoria():
    salvar_memoria([])


def remover_memoria_por_pergunta(pergunta):
    memoria = carregar_memoria()
    pergunta_norm = normalizar_texto(pergunta)

    nova_memoria = [
        item for item in memoria
        if normalizar_texto(item.get("pergunta")) != pergunta_norm
    ]

    alterou = len(nova_memoria) != len(memoria)
    if alterou:
        salvar_memoria(nova_memoria)

    return alterou