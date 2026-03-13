import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime

import config
from classifier import classificar_ticket
from ragnarok_lookup import extrair_pergunta_relevante
from memory_lookup import buscar_memoria_semelhante, adicionar_memoria_se_nao_existir, contar_memorias
from transcript_learning import extrair_aprendizado_do_transcript


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


ESTADOS_FILE = "estados_tickets.json"
HISTORICO_FILE = "tickets_history.json"

FALHA_RESPOSTA = [
    "não funcionou",
    "nao funcionou",
    "ainda não funcionou",
    "ainda nao funcionou",
    "continua com erro",
    "deu o mesmo erro",
    "deu o mesmo problema",
    "não resolveu",
    "nao resolveu",
    "não",
    "nao"
]

SUCESSO_RESPOSTA = [
    "funcionou",
    "deu certo",
    "resolveu",
    "consegui",
    "agora foi",
    "agora funcionou",
    "sim",
    "sim resolveu",
    "resolvido",
    "foi resolvido"
]


def carregar_estados():
    if not os.path.exists(ESTADOS_FILE):
        return {}

    try:
        with open(ESTADOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def salvar_estados(estados):
    with open(ESTADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(estados, f, indent=4, ensure_ascii=False)


estado_tickets = carregar_estados()


def definir_estado(canal, estado):
    if canal not in estado_tickets:
        estado_tickets[canal] = {}

    estado_tickets[canal]["estado"] = estado
    salvar_estados(estado_tickets)


def salvar_dados_ticket(canal, pergunta=None, resposta=None, categoria=None):
    if canal not in estado_tickets:
        estado_tickets[canal] = {}

    if pergunta:
        estado_tickets[canal]["pergunta"] = pergunta

    if resposta:
        estado_tickets[canal]["ultima_resposta"] = resposta

    if categoria:
        estado_tickets[canal]["categoria"] = categoria

    salvar_estados(estado_tickets)


def obter_dados_ticket(canal):
    return estado_tickets.get(canal, {})


def salvar_historico(canal, pergunta, resposta, categoria, estado):
    registro = {
        "canal": canal,
        "pergunta": pergunta,
        "resposta": resposta,
        "categoria": categoria,
        "estado": estado,
        "data": str(datetime.now())
    }

    try:
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except Exception:
        historico = []

    historico.append(registro)

    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)


def carregar_historico():
    if not os.path.exists(HISTORICO_FILE):
        return []

    try:
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def mensagem_igual(texto, lista):
    texto = (texto or "").strip().lower()
    return texto in lista


def gerar_mencoes(ids):
    if not ids:
        return ""
    return " ".join([f"<@{x}>" for x in ids])


def obter_responsaveis(categoria):
    if categoria == "denuncia":
        return config.RESPONSAVEIS_DENUNCIAS

    if categoria == "seguranca":
        return config.RESPONSAVEIS_SEGURANCA

    if categoria == "bug":
        return config.RESPONSAVEIS_BUGS

    if categoria == "financeiro":
        return config.RESPONSAVEIS_FINANCEIRO

    if categoria == "sugestao":
        return config.RESPONSAVEIS_SUGESTOES

    return config.RESPONSAVEIS_SUPORTE_GERAL


def obter_responsaveis_por_categoria(categoria):
    if categoria in ["denuncia_bot", "cheat", "jobfilter", "bug_zeny"]:
        return config.RESPONSAVEIS_SEGURANCA

    if categoria == "denuncia":
        return config.RESPONSAVEIS_DENUNCIAS

    if categoria in ["patch", "bug", "login"]:
        return config.RESPONSAVEIS_BUGS

    if categoria in ["pagamento", "doacao", "pix"]:
        return config.RESPONSAVEIS_FINANCEIRO

    if categoria == "sugestao":
        return config.RESPONSAVEIS_SUGESTOES

    return config.RESPONSAVEIS_SUPORTE_GERAL


def ajustar_categoria_especial(texto, categoria_original):
    texto = (texto or "").lower()

    palavras_seguranca = [
        "bot",
        "macro",
        "hack",
        "cheat",
        "autoclick",
        "programa ilegal",
        "programa irregular",
        "jobfilter",
        "job filter",
        "filtro de job",
        "bug de zeny",
        "duplicar zeny",
        "duplica zeny",
        "zeny bugado",
        "bug zeny"
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

    palavras_sugestao = [
        "sugestão",
        "sugestao",
        "sugerir",
        "minha sugestão",
        "minha sugestao",
        "seria legal",
        "vocês poderiam",
        "voces poderiam"
    ]

    if any(p in texto for p in ["jobfilter", "job filter", "filtro de job"]):
        return "jobfilter"

    if any(p in texto for p in ["bug de zeny", "duplicar zeny", "duplica zeny", "zeny bugado", "bug zeny"]):
        return "bug_zeny"

    if any(p in texto for p in palavras_seguranca):
        return "denuncia_bot"

    if any(p in texto for p in palavras_denuncia_conduta):
        return "denuncia"

    if any(p in texto for p in palavras_sugestao):
        return "sugestao"

    return categoria_original


def extrair_texto_ticket_tool(embeds):
    partes = []

    for embed in embeds:
        if embed.title:
            partes.append(embed.title)

        if embed.description:
            partes.append(embed.description)

        for field in embed.fields:
            nome = (field.name or "").strip()
            valor = (field.value or "").strip()

            if nome:
                partes.append(nome)

            if valor:
                partes.append(valor)

    texto = "\n".join(partes)
    print("\n=== TEXTO EXTRAÍDO DO TICKET ===")
    print(texto)
    return texto


def eh_mensagem_automatica_fechamento(texto):
    if not texto:
        return False

    texto = texto.lower()

    padroes = [
        "ticket closed by",
        "support team ticket controls",
        "transcript",
        "open",
        "delete"
    ]

    return any(p in texto for p in padroes)


def anexar_pergunta_resolvido(texto):
    return f"""{texto}

Isso resolveu seu problema?
Responda com:
- sim
- ou
- não funcionou
"""


async def enviar_resposta(channel, texto):
    async with channel.typing():
        await asyncio.sleep(2)
    await channel.send(texto)


async def responder_links(channel):
    texto = """
Entendi! Confira estes links:

RateMyServer
https://ratemyserver.net/

Wiki SkålRO
https://www.skalro.com.br/wiki/

Isso resolveu seu problema?
Responda:
sim
ou
não funcionou
"""
    await enviar_resposta(channel, texto)
    return texto


async def responder_sucesso(channel):
    texto = "Perfeito! Que bom que funcionou. Se precisar de algo mais é só chamar."
    await enviar_resposta(channel, texto)
    return texto


async def escalar_suporte(channel, categoria):
    ids = obter_responsaveis_por_categoria(categoria)
    mencoes = gerar_mencoes(ids)

    if categoria == "denuncia":
        texto = "Entendi. Vou encaminhar essa denúncia para a equipe responsável analisar com cuidado."
    elif categoria in ["denuncia_bot", "cheat", "jobfilter", "bug_zeny"]:
        texto = "Entendi. Vou encaminhar esse caso para a equipe responsável verificar com prioridade."
    else:
        texto = "Entendi. Nesse caso, vou encaminhar para a equipe verificar com mais cuidado."

    if mencoes:
        texto = f"{texto}\n\n{mencoes}"

    await enviar_resposta(channel, texto)
    return texto


async def tentar_resolver_com_memoria(pergunta, categoria):
    memoria = await asyncio.to_thread(
        buscar_memoria_semelhante,
        pergunta,
        categoria
    )

    if memoria["found"]:
        return memoria["item"]["resposta"]

    return None


async def capturar_conversa_staff(channel, mensagem_resolvido):
    ignorar = {
        "resolvido",
        "resolveu",
        "sim",
        "foi resolvido",
        "ok",
        "oks",
        "blz",
        "beleza"
    }

    blocos = []

    async for msg in channel.history(limit=15, before=mensagem_resolvido):
        if msg.author.bot:
            continue

        conteudo = (msg.content or "").strip()
        if not conteudo:
            continue

        if conteudo.lower() in ignorar:
            continue

        blocos.append(conteudo)

    if not blocos:
        return None

    blocos.reverse()
    return "\n".join(blocos[-6:])


async def aprender_de_anexo_transcript(message):
    if not getattr(config, "LOGS_CHANNEL_ID", 0):
        return

    if message.channel.id != config.LOGS_CHANNEL_ID:
        return

    if not message.attachments:
        return

    for attachment in message.attachments:
        nome = (attachment.filename or "").lower()

        if not (
            nome.endswith(".txt")
            or nome.endswith(".md")
            or nome.endswith(".log")
            or "transcript" in nome
        ):
            continue

        try:
            conteudo_bytes = await attachment.read()
            conteudo = conteudo_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"Erro ao ler transcript anexado: {e}")
            continue

        aprendizado = extrair_aprendizado_do_transcript(conteudo)

        if not aprendizado:
            print("Nenhum aprendizado útil extraído do transcript.")
            continue

        salvo = await asyncio.to_thread(
            adicionar_memoria_se_nao_existir,
            aprendizado["pergunta"],
            aprendizado["resposta"],
            "duvida_geral"
        )

        if salvo:
            print("Aprendizado salvo automaticamente via transcript.")
        else:
            print("Aprendizado do transcript já existia.")


@bot.command()
async def debug(ctx):
    resposta = f"""
🔎 Diagnóstico Helena

TOKEN carregado: {bool(config.TOKEN)}
Modelo OpenAI: {config.OPENAI_MODEL}
LOGS_CHANNEL_ID: {config.LOGS_CHANNEL_ID}

RESP_SEGURANCA: {len(config.RESPONSAVEIS_SEGURANCA)}
RESP_DENUNCIAS: {len(config.RESPONSAVEIS_DENUNCIAS)}
RESP_BUGS: {len(config.RESPONSAVEIS_BUGS)}
RESP_FINANCEIRO: {len(config.RESPONSAVEIS_FINANCEIRO)}
RESP_SUGESTOES: {len(config.RESPONSAVEIS_SUGESTOES)}
RESP_SUPORTE: {len(config.RESPONSAVEIS_SUPORTE_GERAL)}

Memória aprendida: {contar_memorias()}
"""
    await ctx.send(resposta)


@bot.command()
async def stats(ctx):
    historico = carregar_historico()

    total = len(historico)
    resolvidos = len([h for h in historico if h.get("estado") == "resolvido"])
    escalados = len([h for h in historico if h.get("estado") == "escalado"])
    memoria = len([h for h in historico if h.get("estado") == "respondido_memoria"])
    respondidos = len([h for h in historico if h.get("estado") == "respondido"])

    resposta = f"""
📊 Estatísticas Helena

Tickets no histórico: {total}
Resolvidos: {resolvidos}
Escalados: {escalados}
Respondidos pela memória: {memoria}
Respondidos automaticamente: {respondidos}
Memória aprendida total: {contar_memorias()}
"""
    await ctx.send(resposta)


@bot.event
async def on_ready():
    print(f"Helena conectada como {bot.user}")


@bot.event
async def on_message(message):
    await aprender_de_anexo_transcript(message)

    if message.author == bot.user:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    nome_canal = message.channel.name.lower()

    if nome_canal.startswith("closed"):
        return

    if not nome_canal.startswith("ticket"):
        return

    canal = message.channel.name
    dados = obter_dados_ticket(canal)
    estado = dados.get("estado", "novo")

    texto = message.content

    if message.author.bot:
        if len(message.embeds) == 0:
            return

        texto = extrair_texto_ticket_tool(message.embeds)

        if eh_mensagem_automatica_fechamento(texto):
            print("Mensagem automática de fechamento ignorada.")
            return

        if estado != "novo":
            return

    pergunta = extrair_pergunta_relevante(texto)
    categoria = ajustar_categoria_especial(texto, classificar_ticket(texto))

    if estado == "escalado":
        if mensagem_igual(pergunta, ["resolvido", "resolveu", "sim", "foi resolvido"]):
            resposta = await responder_sucesso(message.channel)
            definir_estado(canal, "resolvido")
            salvar_historico(canal, pergunta, resposta, categoria, "resolvido")

            pergunta_original = dados.get("pergunta")
            resposta_staff = await capturar_conversa_staff(message.channel, message)

            if pergunta_original and resposta_staff:
                await asyncio.to_thread(
                    adicionar_memoria_se_nao_existir,
                    pergunta_original,
                    resposta_staff,
                    categoria
                )

            return

        return

    if categoria in ["denuncia_bot", "cheat", "jobfilter", "bug_zeny"]:
        resposta = await escalar_suporte(message.channel, categoria)
        definir_estado(canal, "escalado")
        salvar_dados_ticket(canal, pergunta, resposta, categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "escalado")
        return

    if categoria == "denuncia":
        resposta = await escalar_suporte(message.channel, categoria)
        definir_estado(canal, "escalado")
        salvar_dados_ticket(canal, pergunta, resposta, categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "escalado")
        return

    resposta_memoria = await tentar_resolver_com_memoria(pergunta, categoria)

    if resposta_memoria:
        resposta = anexar_pergunta_resolvido(resposta_memoria)
        await enviar_resposta(message.channel, resposta)
        definir_estado(canal, "respondido_memoria")
        salvar_dados_ticket(canal, pergunta, resposta, categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "respondido_memoria")
        return

    resposta = await responder_links(message.channel)
    definir_estado(canal, "respondido")
    salvar_dados_ticket(canal, pergunta, resposta, categoria)
    salvar_historico(canal, pergunta, resposta, categoria, "respondido")


bot.run(config.TOKEN)