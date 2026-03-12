from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def gerar_resposta_humana(
    tipo_ticket,
    mensagem_jogador,
    contexto_ticket="",
    instrucao_interna="",
    tom="humano"
):
    """
    Gera uma resposta mais humana para a Helena usando OpenAI.
    """

    system_prompt = f"""
Você é Helena, atendente de suporte do servidor privado de Ragnarok chamado SkålRO.

Regras obrigatórias:
- Responda sempre em português do Brasil.
- Seja humana, educada, natural e clara.
- Não fale que você é uma IA.
- Não invente regras, sistemas ou soluções.
- Não invente links.
- Se houver uma instrução interna, siga exatamente essa instrução.
- Responda de forma curta a média, sem texto excessivo.
- Se o contexto já trouxer a solução, apenas reformule de forma humana.
- Se o assunto for denúncia de bot, use tom sério e diga que será encaminhado imediatamente.
"""

    user_prompt = f"""
Tipo do ticket: {tipo_ticket}

Mensagem do jogador:
{mensagem_jogador}

Contexto adicional:
{contexto_ticket}

Instrução interna:
{instrucao_interna}

Tom desejado:
{tom}

Escreva apenas a mensagem final que será enviada ao jogador.
"""

    try:
        response = client.responses.create(
            model=config.OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response.output_text.strip()

    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return None