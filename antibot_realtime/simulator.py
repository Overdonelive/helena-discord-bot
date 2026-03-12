import random
import time
from models import Event


TOTAL_PLAYERS = 100
EVENTS_PER_PLAYER = 40


def generate_human_event(char_id: int, timestamp: float) -> Event:
    possible_maps = [
        "prontera",
        "geffen",
        "payon",
        "prt_fild08",
        "gef_fild01",
        "pay_fild02",
        "gef_dun00",
        "pay_dun00",
    ]

    map_name = random.choice(possible_maps)

    if "fild" in map_name or "dun" in map_name:
        event_type = random.choice(["move", "attack", "skill", "warp"])
        target_type = "mob"
    elif map_name in ["prontera", "geffen", "payon"]:
        event_type = random.choice(["move", "trade", "zeny_gain"])
        target_type = None
    else:
        event_type = random.choice(["move", "attack", "skill"])
        target_type = None

    skill_id = None
    target_class = None
    zeny_amount = None
    zeny_source = None
    trade_zeny = None
    trade_item_count = None
    trade_partner_id = None

    if event_type == "skill":
        skill_id = random.choice([101, 102, 103, 104, 105])

    if event_type == "zeny_gain":
        zeny_amount = random.choice([500, 1500, 2500, 5000])
        zeny_source = random.choice(["mob_drop", "npc", "quest"])

    if event_type == "trade":
        trade_zeny = random.choice([0, 5000, 10000, 25000])
        trade_item_count = random.choice([1, 2, 3, 4])
        trade_partner_id = random.randint(1000, 2000)

    return Event(
        timestamp=timestamp,
        char_id=char_id,
        account_id=char_id,
        account_login=f"human_login_{char_id}",
        char_name=f"Human_{char_id}",
        class_id=random.randint(1, 10),
        event_type=event_type,
        map_name=map_name,
        x=random.randint(0, 200),
        y=random.randint(0, 200),
        target_type=target_type,
        target_class=target_class,
        skill_id=skill_id,
        nearby_players=random.randint(0, 6),
        mode_tag="NORMAL",
        zeny_amount=zeny_amount,
        zeny_source=zeny_source,
        trade_zeny=trade_zeny,
        trade_item_count=trade_item_count,
        trade_partner_id=trade_partner_id,
    )


def generate_field_bot_event(char_id: int, timestamp: float) -> Event:
    event_type = random.choice(["move", "attack", "skill", "warp"])

    return Event(
        timestamp=timestamp,
        char_id=char_id,
        account_id=char_id,
        account_login=f"field_bot_login_{char_id}",
        char_name=f"FieldBot_{char_id}",
        class_id=random.randint(1, 10),
        event_type=event_type,
        map_name=random.choice(["pay_fild02", "gef_fild01", "prt_fild08"]),
        x=random.randint(98, 102),
        y=random.randint(98, 102),
        target_type="mob",
        skill_id=201 if event_type == "skill" else None,
        nearby_players=random.randint(0, 2),
        mode_tag="NORMAL",
    )


def generate_dungeon_bot_event(char_id: int, timestamp: float) -> Event:
    event_type = random.choice(["move", "attack", "skill", "warp"])

    return Event(
        timestamp=timestamp,
        char_id=char_id,
        account_id=char_id,
        account_login=f"dungeon_bot_login_{char_id}",
        char_name=f"DungeonBot_{char_id}",
        class_id=random.randint(1, 10),
        event_type=event_type,
        map_name=random.choice(["gef_dun00", "pay_dun00", "orc_dun01"]),
        x=random.randint(48, 52),
        y=random.randint(48, 52),
        target_type="mob",
        skill_id=201 if event_type == "skill" else None,
        nearby_players=random.randint(0, 2),
        mode_tag="NORMAL",
    )


def generate_trade_abuse_event(char_id: int, timestamp: float) -> Event:
    return Event(
        timestamp=timestamp,
        char_id=char_id,
        account_id=char_id,
        account_login=f"trade_abuse_login_{char_id}",
        char_name=f"TradeAbuse_{char_id}",
        class_id=random.randint(1, 10),
        event_type="trade",
        map_name=random.choice(["prontera", "geffen", "morocc", "alberta", "payon"]),
        x=random.randint(90, 110),
        y=random.randint(90, 110),
        nearby_players=random.randint(2, 8),
        mode_tag="NORMAL",
        trade_zeny=random.choice([50_000_000, 80_000_000, 120_000_000]),
        trade_item_count=random.choice([40, 60, 90]),
        trade_partner_id=random.randint(1000, 2000),
    )


def generate_zeny_abuse_event(char_id: int, timestamp: float) -> Event:
    return Event(
        timestamp=timestamp,
        char_id=char_id,
        account_id=char_id,
        account_login=f"zeny_abuse_login_{char_id}",
        char_name=f"ZenyAbuse_{char_id}",
        class_id=random.randint(1, 10),
        event_type="zeny_gain",
        map_name=random.choice(["prontera", "geffen", "morocc", "alberta", "payon"]),
        x=random.randint(90, 110),
        y=random.randint(90, 110),
        nearby_players=random.randint(1, 5),
        mode_tag="NORMAL",
        zeny_amount=random.choice([30_000_000, 50_000_000, 80_000_000]),
        zeny_source="npc",
    )


def generate_jobfilter_event(char_id: int, timestamp: float) -> Event:
    return Event(
        timestamp=timestamp,
        char_id=char_id,
        account_id=char_id,
        account_login=f"jobfilter_login_{char_id}",
        char_name=f"JobFilter_{char_id}",
        class_id=random.randint(1, 10),
        event_type="skill",
        map_name="prtg_cas01",
        x=random.randint(100, 102),
        y=random.randint(100, 102),
        target_type="player",
        target_class=4008,
        skill_id=345,
        nearby_players=random.randint(12, 20),
        mode_tag="PVP",
    )


def generate_events():
    events = []
    now = time.time()

    # 94 humanos
    human_ids = list(range(1, 95))

    # 2 bots em field
    field_bot_ids = [201, 202]

    # 1 bot em dungeon
    dungeon_bot_ids = [301]

    # 1 abuso de trade
    trade_ids = [401]

    # 1 abuso de zeny
    zeny_ids = [501]

    # 1 jobfilter
    jobfilter_ids = [601]

    # humanos
    for char_id in human_ids:
        timestamp = now

        for _ in range(EVENTS_PER_PLAYER):
            event = generate_human_event(char_id, timestamp)
            timestamp += random.uniform(1.5, 4.0)
            events.append(event)

    # bots field
    for char_id in field_bot_ids:
        timestamp = now

        for _ in range(EVENTS_PER_PLAYER):
            event = generate_field_bot_event(char_id, timestamp)
            timestamp += 1.0
            events.append(event)

    # bot dungeon
    for char_id in dungeon_bot_ids:
        timestamp = now

        for _ in range(EVENTS_PER_PLAYER):
            event = generate_dungeon_bot_event(char_id, timestamp)
            timestamp += 1.0
            events.append(event)

    # trade abuse
    for char_id in trade_ids:
        timestamp = now

        for _ in range(EVENTS_PER_PLAYER):
            event = generate_trade_abuse_event(char_id, timestamp)
            timestamp += random.uniform(180, 700)
            events.append(event)

    # zeny abuse
    for char_id in zeny_ids:
        timestamp = now

        for _ in range(EVENTS_PER_PLAYER):
            event = generate_zeny_abuse_event(char_id, timestamp)
            timestamp += random.uniform(120, 600)
            events.append(event)

    # jobfilter
    for char_id in jobfilter_ids:
        timestamp = now

        for _ in range(EVENTS_PER_PLAYER):
            event = generate_jobfilter_event(char_id, timestamp)
            timestamp += 1.0
            events.append(event)

    return events