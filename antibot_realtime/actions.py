from datetime import datetime, timedelta
import json
import os

from config import (
    AUTO_KICK_SCORE_THRESHOLD,
    AUTO_BAN_AFTER_3_DISCONNECTS_SCORE_THRESHOLD,
    AUTO_KICK_ZENY_SCORE_THRESHOLD,
    AUTO_BAN_AFTER_3_DISCONNECTS_ZENY_SCORE_THRESHOLD,
    AUTO_KICK_TRADE_SCORE_THRESHOLD,
    AUTO_BAN_AFTER_3_DISCONNECTS_TRADE_SCORE_THRESHOLD,
    KICK_INTERVAL_SECONDS,
    DISCONNECTS_FOR_1DAY_BAN,
    AUTO_BAN_1DAY_DURATION_HOURS
)

PENALTIES_FILE = "penalties_history.json"


def load_penalties_history():
    if not os.path.exists(PENALTIES_FILE):
        return {}

    with open(PENALTIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_penalties_history(history):
    with open(PENALTIES_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def ensure_player(account_login, history):
    if account_login not in history:
        history[account_login] = {
            "disconnect_count": 0,
            "last_kick_time": 0,
            "ban_until": None
        }


def should_kick(suspect):
    if suspect.get("score", 0) >= AUTO_KICK_SCORE_THRESHOLD:
        return True

    if suspect.get("zeny_score", 0) >= AUTO_KICK_ZENY_SCORE_THRESHOLD:
        return True

    if suspect.get("trade_score", 0) >= AUTO_KICK_TRADE_SCORE_THRESHOLD:
        return True

    return False


def should_ban_after_disconnects(suspect):
    if suspect.get("score", 0) >= AUTO_BAN_AFTER_3_DISCONNECTS_SCORE_THRESHOLD:
        return True

    if suspect.get("zeny_score", 0) >= AUTO_BAN_AFTER_3_DISCONNECTS_ZENY_SCORE_THRESHOLD:
        return True

    if suspect.get("trade_score", 0) >= AUTO_BAN_AFTER_3_DISCONNECTS_TRADE_SCORE_THRESHOLD:
        return True

    return False


def build_action_record(suspect, history):
    now = datetime.now()
    now_ts = now.timestamp()

    account_login = suspect["account_login"]

    ensure_player(account_login, history)

    record = history[account_login]

    disconnect_count = record["disconnect_count"]
    last_kick_time = record["last_kick_time"]

    action_type = "none"
    action_reason = "Sem ação"

    if should_kick(suspect):
        if now_ts - last_kick_time >= KICK_INTERVAL_SECONDS:
            disconnect_count += 1

            record["disconnect_count"] = disconnect_count
            record["last_kick_time"] = now_ts

            if (
                disconnect_count >= DISCONNECTS_FOR_1DAY_BAN
                and should_ban_after_disconnects(suspect)
            ):
                action_type = "ban_1day"

                ban_until = now + timedelta(hours=AUTO_BAN_1DAY_DURATION_HOURS)

                record["ban_until"] = ban_until.isoformat()
                action_reason = "Ban automático após 3 desconexões."

            else:
                action_type = "kick"
                action_reason = f"Kick automático #{disconnect_count}"

        else:
            action_type = "none"
            action_reason = "Cooldown de kick ativo"

    return {
        "timestamp": now.isoformat(),
        "account_login": account_login,
        "char_name": suspect["char_name"],
        "char_id": suspect["char_id"],
        "score": suspect.get("score", 0),
        "zeny_score": suspect.get("zeny_score", 0),
        "trade_score": suspect.get("trade_score", 0),
        "action_type": action_type,
        "disconnect_count": record["disconnect_count"],
        "ban_until": record["ban_until"],
        "action_reason": action_reason
    }


def describe_action(action):
    if action["action_type"] == "kick":
        return f"KICK | desconexões: {action['disconnect_count']}"

    if action["action_type"] == "ban_1day":
        return f"BAN 1 DIA até {action['ban_until']}"

    return "SEM AÇÃO"