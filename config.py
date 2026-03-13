import os


TOKEN = os.getenv("TOKEN")
PATCH_LINK = os.getenv("PATCH_LINK")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

LOGS_CHANNEL_ID = int(os.getenv("LOGS_CHANNEL_ID", "0"))


def ler_ids(nome):
    valor = os.getenv(nome, "")

    if not valor:
        return []

    return [int(x.strip()) for x in valor.split(",") if x.strip()]


RESPONSAVEIS_SEGURANCA = ler_ids("RESPONSAVEIS_SEGURANCA")
RESPONSAVEIS_DENUNCIAS = ler_ids("RESPONSAVEIS_DENUNCIAS")
RESPONSAVEIS_BUGS = ler_ids("RESPONSAVEIS_BUGS")
RESPONSAVEIS_FINANCEIRO = ler_ids("RESPONSAVEIS_FINANCEIRO")
RESPONSAVEIS_SUGESTOES = ler_ids("RESPONSAVEIS_SUGESTOES")
RESPONSAVEIS_SUPORTE_GERAL = ler_ids("RESPONSAVEIS_SUPORTE_GERAL")