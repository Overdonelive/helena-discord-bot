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


def adicionar_memoria(pergunta, resposta, categoria):
    memoria = carregar_memoria()

    registro = {
        "pergunta": pergunta.strip(),
        "resposta": resposta.strip(),
        "categoria": categoria.strip()
    }

    memoria.append(registro)
    salvar_memoria(memoria)


def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def buscar_memoria_semelhante(pergunta, categoria=None, limite=0.72):
    memoria = carregar_memoria()

    melhor_item = None
    melhor_score = 0

    for item in memoria:
        if categoria and item.get("categoria") != categoria:
            continue

        score = similaridade(pergunta, item.get("pergunta", ""))

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