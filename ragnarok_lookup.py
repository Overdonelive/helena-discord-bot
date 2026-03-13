def extrair_pergunta_relevante(texto):
    if not texto:
        return ""

    texto = texto.lower()

    palavras_remover = [
        "usuário da conta em questão",
        "nome de um personagem na conta",
        "assunto",
        "descrição detalhada"
    ]

    for p in palavras_remover:
        texto = texto.replace(p, "")

    return texto.strip()