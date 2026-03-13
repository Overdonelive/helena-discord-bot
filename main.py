import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime

import config
from classifier import classificar_ticket
from ragnarok_lookup import extrair_pergunta_relevante
from memory_lookup import buscar_memoria_semelhante, adicionar_memoria_se_nao_existir
from transcript_learning import extrair_aprendizado_do_transcript


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


ESTADOS_FILE = "estados_tickets.json"
HISTORICO_FILE = "tickets_history.json"


def carregar_estados():
    if not os.path.exists(ESTADOS_FILE):
        return {}

    with open(ESTADOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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
    except:
        historico = []

    historico.append(registro)

    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)


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

    ids = obter_responsaveis(categoria)

    mencoes = gerar_mencoes(ids)

    texto = f"""
Esse caso precisa de verificação manual da equipe.

{mencoes}
"""

    await enviar_resposta(channel, texto)

    return texto


@bot.event
async def on_ready():

    print(f"Helena conectada como {bot.user}")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    canal = message.channel.name

    if not canal.startswith("ticket"):
        return

    dados = obter_dados_ticket(canal)

    estado = dados.get("estado", "novo")

    texto = message.content.lower()

    pergunta = extrair_pergunta_relevante(texto)

    categoria = classificar_ticket(texto)

    if estado == "escalado":

        if texto in ["resolvido", "sim", "resolveu"]:

            resposta = await responder_sucesso(message.channel)

            definir_estado(canal, "resolvido")

            pergunta_original = dados.get("pergunta")

            resposta_staff = None

            async for msg in message.channel.history(limit=20, before=message):

                if msg.author.bot:
                    continue

                resposta_staff = msg.content
                break

            if pergunta_original and resposta_staff:

                await asyncio.to_thread(
                    adicionar_memoria_se_nao_existir,
                    pergunta_original,
                    resposta_staff,
                    categoria
                )

            return

        return

    resposta_memoria = await asyncio.to_thread(
        buscar_memoria_semelhante,
        pergunta,
        categoria
    )

    if resposta_memoria["found"]:

        resposta = resposta_memoria["item"]["resposta"]

        resposta += "\n\nIsso resolveu seu problema?"

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