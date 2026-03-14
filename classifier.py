def classificar_ticket(texto):
    texto = texto.lower().strip()

    palavras_patch = [
        "patch",
        "atualiza",
        "atualização",
        "atualizar",
        "não atualiza",
        "nao atualiza",
        "launcher",
        "client",
        "cliente",
        "gepard",
        "odin",
        "erro gepard",
        "erro odin",
        "patch trava",
        "patch travando",
        "trava em 50",
        "trava em 50%",
        "travando em 50",
        "travando em 50%",
        "travou em 50",
        "travou em 50%",
        "patch não abre",
        "patch nao abre"
    ]

    palavras_login = [
        "login",
        "logar",
        "não consigo logar",
        "nao consigo logar",
        "não consigo entrar",
        "nao consigo entrar",
        "não entra",
        "nao entra",
        "senha",
        "recuperar senha",
        "minha conta",
        "acesso à conta",
        "acesso a conta"
    ]

    palavras_bug = [
        "bug",
        "erro",
        "travando",
        "crash",
        "fecha sozinho",
        "fechando sozinho",
        "problema no jogo",
        "item bugado",
        "npc bugado",
        "quest bugada",
        "skill bugada",
        "mapa bugado",
        "evento bugado"
    ]

    palavras_denuncia_bot = [
        "bot",
        "macro",
        "hack",
        "cheat",
        "autoclick",
        "uso de bot",
        "usando bot",
        "player bot",
        "farmando bot",
        "programa ilegal",
        "programa irregular"
    ]

    palavras_jobfilter = [
        "jobfilter",
        "job filter",
        "filtro de job",
        "filtro de classe"
    ]

    palavras_bug_zeny = [
        "bug de zeny",
        "zeny bugado",
        "duplica zeny",
        "duplicar zeny",
        "dupar zeny",
        "zeny duplicado"
    ]

    palavras_denuncia_conduta = [
        "xingamento",
        "xingar",
        "xingou",
        "ofensa",
        "ofendeu",
        "insulto",
        "ks",
        "kill steal",
        "roubou mob",
        "roubando mob",
        "racismo",
        "racista",
        "macaco",
        "homofobia",
        "homofóbico",
        "homofobico",
        "machismo",
        "machista",
        "ódio contra mulher",
        "odio contra mulher",
        "misoginia",
        "misógino",
        "misogino",
        "assédio",
        "assedio",
        "preconceito",
        "discriminação",
        "discriminacao"
    ]

    palavras_denuncia = [
        "denúncia",
        "denuncia",
        "reportar",
        "denunciar",
        "player abusivo",
        "comportamento inadequado"
    ]

    palavras_banimento = [
        "ban",
        "banido",
        "banimento",
        "punição",
        "punicao",
        "mute",
        "suspensão",
        "suspensao",
        "fui punido",
        "fui banido"
    ]

    palavras_pagamento = [
        "pix",
        "pagamento",
        "doação",
        "doacao",
        "recarga",
        "compra",
        "cash",
        "donate",
        "vip",
        "não caiu",
        "nao caiu",
        "comprei"
    ]

    palavras_sugestao = [
        "sugestão",
        "sugestao",
        "sugerir",
        "minha sugestão",
        "minha sugestao",
        "seria legal",
        "voces poderiam",
        "vocês poderiam",
        "acho que seria bom",
        "quero sugerir"
    ]

    palavras_duvida_jogo = [
        "onde dropa",
        "onde dropo",
        "drop",
        "dropa",
        "dropo",
        "qual mob",
        "que monstro",
        "monstro dropa",
        "drop de",
        "dropa de",
        "item",
        "mob",
        "monstro",
        "carta",
        "equipamento",
        "quest",
        "npc",
        "mapa",
        "skill",
        "build"
    ]

    palavras_duvida_servidor = [
        "wiki",
        "skalro",
        "como funciona o servidor",
        "como funciona o sistema",
        "sistema do servidor",
        "regra do servidor",
        "evento do servidor",
        "comando do servidor",
        "como funciona"
    ]

    if any(p in texto for p in palavras_jobfilter):
        return "jobfilter"

    if any(p in texto for p in palavras_bug_zeny):
        return "bug_zeny"

    if any(p in texto for p in palavras_denuncia_bot):
        return "denuncia_bot"

    if any(p in texto for p in palavras_denuncia_conduta):
        return "denuncia"

    if any(p in texto for p in palavras_sugestao):
        return "sugestao"

    if any(p in texto for p in palavras_patch):
        return "patch"

    if any(p in texto for p in palavras_login):
        return "login"

    if any(p in texto for p in palavras_bug):
        return "bug"

    if any(p in texto for p in palavras_denuncia):
        return "denuncia"

    if any(p in texto for p in palavras_banimento):
        return "banimento"

    if any(p in texto for p in palavras_pagamento):
        return "pagamento"

    if any(p in texto for p in palavras_duvida_jogo):
        return "duvida_jogo"

    if any(p in texto for p in palavras_duvida_servidor):
        return "duvida_servidor"

    return "duvida_geral"