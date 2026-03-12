import requests
from config import (
    DISCORD_WEBHOOK_URL,
    DISCORD_ROLE_ID,
    SEND_DISCORD_ALERTS,
    DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD,
    DISCORD_ZENY_ALERT_THRESHOLD,
    DISCORD_TRADE_ALERT_THRESHOLD,
)


def should_send_discord_alert(suspect, action):
    """
    Regras de envio:
    - score geral >= 7
    - ou farm_score >= 7
    - ou jobfilter_score >= 7
    - ou zeny_score >= 6
    - ou trade_score >= 6
    - ou houve kick/ban
    """

    has_high_general = suspect.get("score", 0) >= DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD
    has_high_farm = suspect.get("farm_score", 0) >= DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD
    has_high_jobfilter = suspect.get("jobfilter_score", 0) >= DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD
    has_high_zeny = suspect.get("zeny_score", 0) >= DISCORD_ZENY_ALERT_THRESHOLD
    has_high_trade = suspect.get("trade_score", 0) >= DISCORD_TRADE_ALERT_THRESHOLD

    has_action = action.get("action_type", "none") in ["kick", "ban_1day"]

    return (
        has_high_general
        or has_high_farm
        or has_high_jobfilter
        or has_high_zeny
        or has_high_trade
        or has_action
    )


def detect_alert_type(suspect, action):
    action_type = action.get("action_type", "none")

    if action_type == "ban_1day":
        return "ban"

    if action_type == "kick":
        return "kick"

    # prioridade para economia se score específico estiver alto
    if suspect.get("zeny_score", 0) >= DISCORD_ZENY_ALERT_THRESHOLD:
        return "zeny"

    if suspect.get("trade_score", 0) >= DISCORD_TRADE_ALERT_THRESHOLD:
        return "trade"

    if suspect.get("jobfilter_score", 0) >= DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD:
        return "jobfilter"

    if suspect.get("farm_score", 0) >= DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD:
        return "farm"

    return "bot"


def get_alert_title_and_color(alert_type):
    if alert_type == "kick":
        return "⚠️ PERSONAGEM DESCONECTADO", 15105570

    if alert_type == "ban":
        return "🔨 CONTA BANIDA POR 1 DIA", 15158332

    if alert_type == "zeny":
        return "💰 ALERTA DE ABUSO DE ZENY", 15844367

    if alert_type == "trade":
        return "📦 ALERTA DE ABUSO DE TRADE", 3447003

    if alert_type == "jobfilter":
        return "🎯 ALERTA DE JOBFILTER", 10181046

    if alert_type == "farm":
        return "🌾 ALERTA DE FARM BOT", 15844367

    return "🤖 ALERTA ANTIBOT", 16753920


def send_discord_alert(suspect, action):
    if not SEND_DISCORD_ALERTS:
        print("[Discord] envio desativado no config.")
        return

    if not should_send_discord_alert(suspect, action):
        print(
            f"[Discord] sem envio para {suspect['char_name']} | "
            f"score={suspect.get('score', 0)} | "
            f"farm={suspect.get('farm_score', 0)} | "
            f"job={suspect.get('jobfilter_score', 0)} | "
            f"zeny={suspect.get('zeny_score', 0)} | "
            f"trade={suspect.get('trade_score', 0)} | "
            f"action={action.get('action_type', 'none')}"
        )
        return

    alert_type = detect_alert_type(suspect, action)
    title, color = get_alert_title_and_color(alert_type)

    reasons = suspect.get("reasons", [])
    reasons_text = "\n".join([f"• {r}" for r in reasons]) if reasons else "Nenhum"

    zeny_gain_hour = suspect.get("zeny_gain_last_hour", 0)
    trade_zeny_total = suspect.get("total_trade_zeny", 0)
    trade_item_total = suspect.get("total_trade_items", 0)

    action_type = action.get("action_type", "none")
    action_reason = action.get("action_reason", "Nenhuma")
    disconnect_count = action.get("disconnect_count", 0)
    ban_until = action.get("ban_until", None)

    if action_type == "ban_1day" and ban_until:
        action_detail = f"{action_reason}\nBan até: {ban_until}"
    else:
        action_detail = action_reason

    embed = {
        "title": title,
        "description": "Um comportamento suspeito foi detectado pelo sistema.",
        "color": color,
        "fields": [
            {"name": "Personagem", "value": suspect["char_name"], "inline": True},
            {"name": "Login", "value": suspect["account_login"], "inline": True},
            {"name": "Account ID", "value": str(suspect["account_id"]), "inline": True},

            {"name": "Char ID", "value": str(suspect["char_id"]), "inline": True},
            {"name": "Bot Score", "value": str(suspect.get("score", 0)), "inline": True},
            {"name": "Farm Score", "value": str(suspect.get("farm_score", 0)), "inline": True},

            {"name": "JobFilter Score", "value": str(suspect.get("jobfilter_score", 0)), "inline": True},
            {"name": "Zeny Score", "value": str(suspect.get("zeny_score", 0)), "inline": True},
            {"name": "Trade Score", "value": str(suspect.get("trade_score", 0)), "inline": True},

            {"name": "APM", "value": str(round(suspect.get("apm", 0), 2)), "inline": True},
            {"name": "Route Repeat Ratio", "value": str(round(suspect.get("route_repeat_ratio", 0), 2)), "inline": True},
            {"name": "Mob Target Ratio", "value": str(round(suspect.get("mob_target_ratio", 0), 2)), "inline": True},

            {"name": "Zeny na última hora", "value": str(zeny_gain_hour), "inline": True},
            {"name": "Total trade zeny", "value": str(trade_zeny_total), "inline": True},
            {"name": "Total itens em trade", "value": str(trade_item_total), "inline": True},

            {"name": "Desconexões", "value": str(disconnect_count), "inline": True},
            {"name": "Ação aplicada", "value": action_type.upper(), "inline": True},
            {"name": "Detalhe da ação", "value": action_detail, "inline": False},

            {"name": "Motivos detectados", "value": reasons_text[:1000], "inline": False},
        ]
    }

    message = {
        "content": f"<@&{DISCORD_ROLE_ID}>",
        "embeds": [embed],
        "allowed_mentions": {"roles": [DISCORD_ROLE_ID]}
    }

    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=message, timeout=15)
        print(
            f"[Discord] enviado para {suspect['char_name']} | "
            f"tipo={alert_type} | status={r.status_code} | "
            f"score={suspect.get('score', 0)} | "
            f"zeny={suspect.get('zeny_score', 0)} | "
            f"trade={suspect.get('trade_score', 0)}"
        )
        if r.text:
            print(f"[Discord] resposta: {r.text}")
    except Exception as e:
        print("[Discord] erro:", e)