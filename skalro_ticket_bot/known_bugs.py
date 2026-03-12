KNOWN_BUGS = [
    {
        "id": "patch_trava_porcentagem",
        "categoria": "patch",
        "tipo_resposta": "segunda_tentativa_patch",
        "keywords": [
            "trava em 50%",
            "trava em 50",
            "travando em 50%",
            "travando em 50",
            "travou em 50%",
            "travou em 50",
            "trava em 70%",
            "trava em 70",
            "travando em 70%",
            "travando em 70",
            "travou em 70%",
            "travou em 70",
            "trava em alguma porcentagem",
            "patch travando",
            "patch trava",
            "trava no patch",
            "parou em 50%",
            "parou em 50",
            "fica em 50%"
        ],
        "resposta": """Entendi. Quando o patch trava em alguma porcentagem, tente este passo a passo:

1. Feche o jogo e o patcher completamente.
2. Extraia novamente o client atualizado em uma pasta limpa.
3. Execute o patcher como administrador.
4. Verifique se o antivírus ou o Windows Defender não bloqueou arquivos do client.
5. Teste novamente após alguns segundos.

Link do client atualizado:
{patch_link}

Se ainda continuar com erro, responda:
ainda não funcionou"""
    },
    {
        "id": "gepard_error",
        "categoria": "patch",
        "tipo_resposta": "inicial_patch",
        "keywords": [
            "erro gepard",
            "gepard error",
            "gepard bloqueando",
            "gepard",
            "erro do gepard"
        ],
        "resposta": """Entendi. Esse problema com o Gepard normalmente é resolvido reinstalando o client atualizado.

Baixe aqui:
{patch_link}

Depois extraia novamente em uma pasta limpa, execute como administrador e teste novamente.

Se ainda continuar com erro, responda:
não funcionou"""
    },
    {
        "id": "odin_error",
        "categoria": "patch",
        "tipo_resposta": "inicial_patch",
        "keywords": [
            "erro odin",
            "odin não abre",
            "odin nao abre",
            "odin",
            "erro do odin"
        ],
        "resposta": """Entendi. Esse problema com o Odin normalmente é resolvido reinstalando o client atualizado.

Baixe aqui:
{patch_link}

Depois extraia novamente em uma pasta limpa, execute como administrador e teste novamente.

Se ainda continuar com erro, responda:
não funcionou"""
    },
    {
        "id": "patch_update",
        "categoria": "patch",
        "tipo_resposta": "inicial_patch",
        "keywords": [
            "não atualiza",
            "nao atualiza",
            "atualização do patch",
            "atualizacao do patch",
            "patch não atualiza",
            "patch nao atualiza",
            "meu patch não atualiza",
            "meu patch nao atualiza",
            "patch"
        ],
        "resposta": """Olá! Esse problema normalmente é resolvido baixando o client atualizado.

Baixe aqui:
{patch_link}

Depois extraia novamente o client em uma pasta limpa e teste abrir o jogo.

Se ainda continuar com erro, responda:
não funcionou"""
    }
]


def buscar_bug_conhecido(texto):
    texto = texto.lower()

    melhor_bug = None
    maior_keyword = ""

    for bug in KNOWN_BUGS:
        for keyword in bug["keywords"]:
            if keyword in texto:
                if len(keyword) > len(maior_keyword):
                    melhor_bug = bug
                    maior_keyword = keyword

    return melhor_bug