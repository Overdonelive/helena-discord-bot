import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime
import os

import config
from classifier import classificar_ticket
from ragnarok_lookup import extrair_pergunta_relevante
from memory_lookup import (
    buscar_memoria_semelhante,
    adicionar_memoria
)

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

    if pergunta is not None:
        estado_tickets[canal]["pergunta"] = pergunta

    if resposta is not None:
        estado_tickets[canal]["ultima_resposta"] = resposta

    if categoria is not None:
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


def mensagem_igual(texto, lista):
    texto = texto.strip().lower()
    return texto in lista


def gerar_mencoes(lista_ids):
    if not lista_ids:
        return ""
    return " ".join([f"<@{user_id}>" for user_id in lista_ids])


def obter_responsaveis_por_categoria(categoria):
    if categoria in ["denuncia_bot", "cheat", "jobfilter", "bug_zeny"]:
        return getattr(config, "RESPONSAVEIS_SEGURANCA", [])

    if categoria == "denuncia":
        return getattr(config, "RESPONSAVEIS_DENUNCIAS", [])

    if categoria in ["patch", "bug", "login"]:
        return getattr(config, "RESPONSAVEIS_BUGS", [])

    if categoria in ["pagamento", "doacao", "pix"]:
        return getattr(config, "RESPONSAVEIS_FINANCEIRO", [])

    if categoria == "sugestao":
        return getattr(config, "RESPONSAVEIS_SUGESTOES", [])

    return getattr(config, "RESPONSAVEIS_SUPORTE_GERAL", [])


def ajustar_categoria_especial(texto, categoria_original):
    texto = texto.lower()

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
    try:
        async with channel.typing():
            await asyncio.sleep(2)
        await channel.send(texto)
    except discord.NotFound:
        print("Canal não encontrado ao responder.")
    except Exception as e:
        print("Erro ao enviar resposta:", e)


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


async def responder_sugestao(channel):
    mencoes = gerar_mencoes(obter_responsaveis_por_categoria("sugestao"))

    texto = "Obrigada pela sugestão! Vou encaminhar isso para a equipe avaliar."
    if mencoes:
        texto = f"{texto}\n\n{mencoes}"

    await enviar_resposta(channel, texto)
    return texto


async def responder_patch(channel):
    texto = f"""Oi! Esse problema normalmente é resolvido baixando o client atualizado.

Baixe aqui:
{config.PATCH_LINK}

Depois extraia novamente o client em uma pasta limpa e teste abrir o jogo.

Se ainda continuar com erro, responda:
não funcionou"""

    await enviar_resposta(channel, texto)
    return texto


async def responder_sucesso(channel):
    texto = "Perfeito! Que bom que deu certo 💛 Se surgir qualquer outra dúvida, estou por aqui."
    await enviar_resposta(channel, texto)
    return texto


async def tentar_resolver_com_memoria(pergunta, categoria):
    memoria = await asyncio.to_thread(
        buscar_memoria_semelhante,
        pergunta,
        categoria
    )

    print("\n=== MEMÓRIA CONSULTADA ===")
    print(memoria)

    if memoria["found"]:
        return memoria["item"]["resposta"]

    return None


async def responder_links_duvida_jogo(channel):
    texto = """Entendi! Para esse tipo de dúvida, confira estes links:

RateMyServer:
https://ratemyserver.net/

Wiki do SkålRO:
https://www.skalro.com.br/wiki/"""
    texto = anexar_pergunta_resolvido(texto)

    await enviar_resposta(channel, texto)
    return texto


async def responder_links_duvida_servidor(channel):
    texto = """Entendi! Para esse tipo de dúvida, confira estes links:

Wiki do SkålRO:
https://www.skalro.com.br/wiki/

RateMyServer:
https://ratemyserver.net/"""
    texto = anexar_pergunta_resolvido(texto)

    await enviar_resposta(channel, texto)
    return texto


async def responder_links_duvida_geral(channel):
    texto = """Entendi! Confira estes links:

RateMyServer:
https://ratemyserver.net/

Wiki do SkålRO:
https://www.skalro.com.br/wiki/"""
    texto = anexar_pergunta_resolvido(texto)

    await enviar_resposta(channel, texto)
    return texto


@bot.event
async def on_ready():
    print(f"Helena conectada como {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    nome_canal = message.channel.name.lower()

    if nome_canal.startswith("closed"):
        return

    if not nome_canal.startswith("ticket"):
        return

    canal = message.channel.name
    dados_ticket = obter_dados_ticket(canal)
    estado = dados_ticket.get("estado", "novo")

    texto = message.content

    if message.author.bot:
        if len(message.embeds) == 0:
            return

        texto = extrair_texto_ticket_tool(message.embeds)

        # ignora mensagens automáticas de fechamento do Ticket Tool
        if eh_mensagem_automatica_fechamento(texto):
            print("Mensagem automática de fechamento ignorada.")
            return

        if estado != "novo":
            return

    categoria = classificar_ticket(texto)
    categoria = ajustar_categoria_especial(texto, categoria)

    print("\nCategoria detectada:", categoria)

    pergunta = extrair_pergunta_relevante(texto)

    print("Pergunta relevante:", pergunta)

    if estado == "escalado":
        if mensagem_igual(pergunta, ["resolvido", "resolveu", "foi resolvido"]):
            resposta = await responder_sucesso(message.channel)
            definir_estado(canal, "resolvido")
            salvar_historico(canal, pergunta, resposta, categoria, "resolvido")

            pergunta_original = dados_ticket.get("pergunta")
            resposta_original = dados_ticket.get("ultima_resposta")
            categoria_original = dados_ticket.get("categoria", categoria)

            if pergunta_original and resposta_original:
                await asyncio.to_thread(
                    adicionar_memoria,
                    pergunta_original,
                    resposta_original,
                    categoria_original
                )
            return

        return

    if categoria in ["denuncia_bot", "cheat", "jobfilter", "bug_zeny"]:
        resposta = await escalar_suporte(message.channel, categoria)
        definir_estado(canal, "escalado")
        salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta, categoria=categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "escalado")
        return

    if categoria == "denuncia":
        resposta = await escalar_suporte(message.channel, categoria)
        definir_estado(canal, "escalado")
        salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta, categoria=categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "escalado")
        return

    if categoria == "sugestao":
        resposta = await responder_sugestao(message.channel)
        definir_estado(canal, "encaminhado_sugestao")
        salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta, categoria=categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "encaminhado_sugestao")
        return

    if categoria == "patch":
        resposta = await responder_patch(message.channel)
        definir_estado(canal, "aguardando_teste_patch")
        salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta, categoria=categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "aguardando_teste_patch")
        return

    if categoria in ["banimento", "pagamento"]:
        resposta = await escalar_suporte(message.channel, categoria)
        definir_estado(canal, "escalado")
        salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta, categoria=categoria)
        salvar_historico(canal, pergunta, resposta, categoria, "escalado")
        return

    if estado == "aguardando_teste_patch":
        if mensagem_igual(pergunta, FALHA_RESPOSTA):
            resposta = await escalar_suporte(message.channel, categoria)
            definir_estado(canal, "escalado")
            salvar_historico(canal, pergunta, resposta, categoria, "escalado")
            return

        if mensagem_igual(pergunta, SUCESSO_RESPOSTA):
            resposta = await responder_sucesso(message.channel)
            definir_estado(canal, "resolvido")
            salvar_dados_ticket(canal, resposta=resposta)
            salvar_historico(canal, pergunta, resposta, categoria, "resolvido")

            pergunta_original = dados_ticket.get("pergunta")
            resposta_original = dados_ticket.get("ultima_resposta")
            categoria_original = dados_ticket.get("categoria", categoria)

            if pergunta_original and resposta_original:
                await asyncio.to_thread(
                    adicionar_memoria,
                    pergunta_original,
                    resposta_original,
                    categoria_original
                )
            return

    if estado in ["respondido", "respondido_memoria"]:
        if mensagem_igual(pergunta, SUCESSO_RESPOSTA):
            resposta = await responder_sucesso(message.channel)
            definir_estado(canal, "resolvido")
            salvar_historico(canal, pergunta, resposta, categoria, "resolvido")

            pergunta_original = dados_ticket.get("pergunta")
            resposta_original = dados_ticket.get("ultima_resposta")
            categoria_original = dados_ticket.get("categoria", categoria)

            if pergunta_original and resposta_original:
                await asyncio.to_thread(
                    adicionar_memoria,
                    pergunta_original,
                    resposta_original,
                    categoria_original
                )
            return

        if mensagem_igual(pergunta, FALHA_RESPOSTA):
            resposta = await escalar_suporte(message.channel, categoria)
            definir_estado(canal, "escalado")
            salvar_historico(canal, pergunta, resposta, categoria, "escalado")
            return

        return

    resposta_memoria = await tentar_resolver_com_memoria(pergunta, categoria)

    if resposta_memoria:
        resposta_memoria = anexar_pergunta_resolvido(resposta_memoria)
        await enviar_resposta(message.channel, resposta_memoria)
        definir_estado(canal, "respondido_memoria")
        salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta_memoria, categoria=categoria)
        salvar_historico(canal, pergunta, resposta_memoria, categoria, "respondido_memoria")
        return

    if categoria == "duvida_jogo":
        resposta = await responder_links_duvida_jogo(message.channel)
    elif categoria == "duvida_servidor":
        resposta = await responder_links_duvida_servidor(message.channel)
    else:
        resposta = await responder_links_duvida_geral(message.channel)

    definir_estado(canal, "respondido")
    salvar_dados_ticket(canal, pergunta=pergunta, resposta=resposta, categoria=categoria)
    salvar_historico(canal, pergunta, resposta, categoria, "respondido")


bot.run(config.TOKEN)