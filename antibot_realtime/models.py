from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    timestamp: float
    char_id: int
    account_id: int
    account_login: str
    char_name: str
    class_id: int
    event_type: str
    map_name: str

    x: Optional[int] = None
    y: Optional[int] = None

    target_id: Optional[int] = None
    target_type: Optional[str] = None
    target_class: Optional[int] = None

    skill_id: Optional[int] = None
    skill_lv: Optional[int] = None
    item_id: Optional[int] = None

    nearby_players: int = 0
    mode_tag: str = "NORMAL"

    # economia / zeny
    zeny_amount: Optional[int] = None
    zeny_source: Optional[str] = None

    # trade
    trade_zeny: Optional[int] = None
    trade_item_count: Optional[int] = None
    trade_partner_id: Optional[int] = None