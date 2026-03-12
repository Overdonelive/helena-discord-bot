from config import (
    PVP_GVG_MONITORED_MAPS,
    ECONOMY_MONITORED_MAPS,
    RELEVANT_EVENT_TYPES,
)


def is_relevant_event(event) -> bool:
    return event.event_type in RELEVANT_EVENT_TYPES


def is_field_map(map_name: str) -> bool:
    return "_fild" in map_name


def is_dungeon_map(map_name: str) -> bool:
    dungeon_patterns = [
        "_dun",
        "dun",
        "cata",
        "tower",
        "abbey",
        "thor",
        "ice",
        "mag_dun",
        "glast",
        "gef_dun",
        "prt_maze",
        "anthell",
        "moc_pryd",
        "orc_dun",
        "pay_dun",
    ]

    return any(pattern in map_name for pattern in dungeon_patterns)


def is_farm_context_map(map_name: str) -> bool:
    return is_field_map(map_name) or is_dungeon_map(map_name)


def is_pvp_gvg_map(map_name: str) -> bool:
    return map_name in PVP_GVG_MONITORED_MAPS


def is_economy_map(map_name: str) -> bool:
    return map_name in ECONOMY_MONITORED_MAPS


def should_process_event(event) -> bool:
    if not is_relevant_event(event):
        return False

    map_name = event.map_name

    if is_farm_context_map(map_name):
        return True

    if is_pvp_gvg_map(map_name):
        return True

    if is_economy_map(map_name):
        return True

    return False


def event_matches_context(event) -> bool:
    map_name = event.map_name

    # farm maps: bot/farm
    if is_farm_context_map(map_name):
        return event.event_type in ["move", "attack", "skill", "warp"]

    # pvp/gvg: jobfilter e dano pvp/gvg
    if is_pvp_gvg_map(map_name):
        if event.event_type not in ["move", "attack", "skill"]:
            return False
        return event.target_type == "player"

    # economy: trade/zeny
    if is_economy_map(map_name):
        return event.event_type in ["trade", "zeny_gain"]

    return False


def detect_context(event) -> str:
    map_name = event.map_name

    if is_farm_context_map(map_name):
        return "farm"

    if is_pvp_gvg_map(map_name):
        return "pvp_gvg"

    if is_economy_map(map_name):
        return "economy"

    return "unknown"