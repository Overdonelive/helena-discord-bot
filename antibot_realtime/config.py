# =========================================
# CONFIGURAÇÕES GERAIS
# =========================================

WINDOW_SECONDS = 3600


# =========================================
# MAPAS MONITORADOS
# =========================================

PVP_GVG_MONITORED_MAPS = [
    "prtg_cas01",
    "guild_vs1",
    "guild_vs2",
    "guild_vs3",
    "guild_vs4",
    "agit_01",
    "agit_02",
    "agit_03",
    "agit_04",
    "agit_05",
]

ECONOMY_MONITORED_MAPS = [
    "prontera",
    "izlude",
    "geffen",
    "payon",
    "morocc",
    "alberta",
    "aldebaran",
    "comodo",
    "umbala",
    "niflheim",
    "louyang",
    "amatsu",
    "kunlun",
    "ayothaya",
    "jawaii",
    "yuno",
    "lighthalzen",
    "einbroch",
    "einbech",
    "hugel",
    "rachel",
    "veins",
    "brasilis",
    "dewata",
    "malaya",
    "port_malaya",
    "lasagna",
    "malangdo",
    "mora",
    "splendide",
    "dicastes01",
    "eclage",
]


# =========================================
# EVENTOS RELEVANTES
# =========================================

RELEVANT_EVENT_TYPES = [
    "move",
    "attack",
    "skill",
    "warp",
    "trade",
    "zeny_gain",
]


# =========================================
# DETECTOR BOT
# =========================================

BOT_APM_THRESHOLD = 80
BOT_TIMING_CV_THRESHOLD = 0.12
BOT_SAME_SKILL_RATIO_THRESHOLD = 0.85
BOT_MIN_SKILL_EVENTS = 10

BOT_FOCUS_CLASS_RATIO_THRESHOLD = 0.80
BOT_FOCUS_MIN_NEARBY_PLAYERS = 8
BOT_WARP_COUNT_THRESHOLD = 8
BOT_ROUTE_REPEAT_RATIO_THRESHOLD = 0.60

BOT_SCORE_ALERT_THRESHOLD = 5
BOT_SCORE_STRONG_ALERT_THRESHOLD = 7


# =========================================
# DETECTOR FARM BOT
# =========================================

FARM_ROUTE_REPEAT_RATIO_THRESHOLD = 0.65
FARM_TIMING_CV_THRESHOLD = 0.10
FARM_SAME_SKILL_RATIO_THRESHOLD = 0.75
FARM_MIN_EVENTS = 20
FARM_MOB_TARGET_RATIO_THRESHOLD = 0.70

FARM_SCORE_ALERT_THRESHOLD = 6


# =========================================
# DETECTOR JOBFILTER
# =========================================

JOBFILTER_FOCUS_CLASS_RATIO_THRESHOLD = 0.85
JOBFILTER_MIN_TARGET_EVENTS = 10
JOBFILTER_MIN_NEARBY_PLAYERS = 10
JOBFILTER_TARGET_SWITCH_RATE_THRESHOLD = 0.20
JOBFILTER_SAME_SKILL_RATIO_THRESHOLD = 0.80
JOBFILTER_TIMING_CV_THRESHOLD = 0.12

JOBFILTER_SCORE_ALERT_THRESHOLD = 6


# =========================================
# DETECTOR ZENY BUG
# =========================================

ZENY_TOTAL_GAIN_HOUR_THRESHOLD = 50_000_000
ZENY_SINGLE_GAIN_THRESHOLD = 20_000_000
ZENY_NPC_GAIN_COUNT_THRESHOLD = 2
ZENY_TOTAL_GAIN_EXTREME_THRESHOLD = 100_000_000

ZENY_SCORE_ALERT_THRESHOLD = 5
DISCORD_ZENY_ALERT_THRESHOLD = 6
AUTO_KICK_ZENY_SCORE_THRESHOLD = 7
AUTO_BAN_AFTER_3_DISCONNECTS_ZENY_SCORE_THRESHOLD = 7


# =========================================
# DETECTOR TRADE ABUSIVO
# =========================================

TRADE_TOTAL_ZENY_THRESHOLD = 100_000_000
TRADE_SINGLE_ZENY_THRESHOLD = 30_000_000
TRADE_TOTAL_ITEMS_THRESHOLD = 80
TRADE_COMBINED_ZENY_THRESHOLD = 50_000_000
TRADE_COMBINED_ITEMS_THRESHOLD = 40

TRADE_SCORE_ALERT_THRESHOLD = 5
DISCORD_TRADE_ALERT_THRESHOLD = 6
AUTO_KICK_TRADE_SCORE_THRESHOLD = 7
AUTO_BAN_AFTER_3_DISCONNECTS_TRADE_SCORE_THRESHOLD = 7


# =========================================
# AÇÕES AUTOMÁTICAS
# =========================================

AUTO_KICK_SCORE_THRESHOLD = 8
AUTO_BAN_AFTER_3_DISCONNECTS_SCORE_THRESHOLD = 8

KICK_INTERVAL_SECONDS = 300
DISCONNECTS_FOR_1DAY_BAN = 3
AUTO_BAN_1DAY_DURATION_HOURS = 24


# =========================================
# ALERTA DE SUSPEITO
# =========================================

DISCORD_SUSPECT_ALERT_SCORE_THRESHOLD = 7


# =========================================
# DISCORD
# =========================================

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1481638673358393494/qjFBbOO7IFVoGSOM-E1PVkD1J4n8rKP3yEzObGptvZJx3k0nFwidEOIVn-cR9CV1VGpR"
DISCORD_ROLE_ID = "1407739499454271610"

SEND_DISCORD_ALERTS = True
DISCORD_ALERT_COOLDOWN_SECONDS = 0