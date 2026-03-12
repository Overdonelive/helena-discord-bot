import os


# ===== TOKENS E LINKS =====

TOKEN = os.getenv("TOKEN")
PATCH_LINK = os.getenv("PATCH_LINK")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")


# ===== FUNÇÃO PARA LER LISTAS DE IDS =====

def ler_ids(nome_variavel):
    valor = os.getenv(nome_variavel, "")
    if not valor:
        return []

    return [int(x.strip()) for x in valor.split(",") if x.strip()]


# ===== RESPONSÁVEIS =====

RESPONSAVEIS_SEGURANCA = ler_ids("RESPONSAVEIS_SEGURANCA")

RESPONSAVEIS_DENUNCIAS = ler_ids("RESPONSAVEIS_DENUNCIAS")

RESPONSAVEIS_BUGS = ler_ids("RESPONSAVEIS_BUGS")

RESPONSAVEIS_FINANCEIRO = ler_ids("RESPONSAVEIS_FINANCEIRO")

RESPONSAVEIS_SUGESTOES = ler_ids("RESPONSAVEIS_SUGESTOES")

RESPONSAVEIS_SUPORTE_GERAL = ler_ids("RESPONSAVEIS_SUPORTE_GERAL")