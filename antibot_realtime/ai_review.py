import os
from openai import OpenAI


def review_suspect_with_ai(suspect: dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "Erro: variável OPENAI_API_KEY não encontrada."

    client = OpenAI(api_key=api_key)

    prompt = f"""
Você é um analista de segurança de um servidor de MMORPG.

Analise o jogador suspeito abaixo e gere um parecer curto, claro e objetivo para a equipe anti-bot/economia.

Dados do suspeito:
- Nome do personagem: {suspect.get('char_name')}
- Login da conta: {suspect.get('account_login')}
- Account ID: {suspect.get('account_id')}
- Char ID: {suspect.get('char_id')}

Pontuações:
- Score de bot: {suspect.get('score')}
- Farm Score: {suspect.get('farm_score')}
- JobFilter Score: {suspect.get('jobfilter_score')}
- Zeny Score: {suspect.get('zeny_score')}
- Trade Score: {suspect.get('trade_score')}

Indicadores:
- APM: {suspect.get('apm')}
- Focus Class Ratio: {suspect.get('focus_class_ratio')}
- Target Switch Rate: {suspect.get('target_switch_rate')}
- Same Skill Ratio: {suspect.get('same_skill_ratio')}
- Timing CV: {suspect.get('timing_cv')}
- Route Repeat Ratio: {suspect.get('route_repeat_ratio')}
- Mob Target Ratio: {suspect.get('mob_target_ratio')}
- Zeny ganho na última hora: {suspect.get('zeny_gain_last_hour')}
- Maior ganho único de zeny: {suspect.get('max_single_zeny_gain')}
- Ganhos via NPC: {suspect.get('npc_zeny_gain_count')}
- Total trade zeny: {suspect.get('total_trade_zeny')}
- Total itens em trade: {suspect.get('total_trade_items')}

Motivos detectados:
{", ".join(suspect.get('reasons', []))}

Responda em português neste formato:

Nível de risco: <baixo/médio/alto>
Resumo: <1 ou 2 frases>
Categoria principal: <bot/farm/jobfilter/zeny/trade/misto>
Recomendação: <ação sugerida>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um analista técnico de detecção de bots, farm bots, exploits econômicos e comportamento suspeito em jogos online."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=220
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Erro ao consultar a OpenAI: {e}"