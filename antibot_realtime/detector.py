from collections import Counter, defaultdict, deque
from statistics import mean, pstdev
from typing import Deque, Dict, List

from models import Event
from config import (
    WINDOW_SECONDS,

    BOT_APM_THRESHOLD,
    BOT_TIMING_CV_THRESHOLD,
    BOT_SAME_SKILL_RATIO_THRESHOLD,
    BOT_MIN_SKILL_EVENTS,
    BOT_FOCUS_CLASS_RATIO_THRESHOLD,
    BOT_FOCUS_MIN_NEARBY_PLAYERS,
    BOT_WARP_COUNT_THRESHOLD,
    BOT_ROUTE_REPEAT_RATIO_THRESHOLD,

    FARM_ROUTE_REPEAT_RATIO_THRESHOLD,
    FARM_TIMING_CV_THRESHOLD,
    FARM_SAME_SKILL_RATIO_THRESHOLD,
    FARM_MIN_EVENTS,
    FARM_MOB_TARGET_RATIO_THRESHOLD,
    FARM_SCORE_ALERT_THRESHOLD,

    JOBFILTER_FOCUS_CLASS_RATIO_THRESHOLD,
    JOBFILTER_MIN_TARGET_EVENTS,
    JOBFILTER_MIN_NEARBY_PLAYERS,
    JOBFILTER_TARGET_SWITCH_RATE_THRESHOLD,
    JOBFILTER_SAME_SKILL_RATIO_THRESHOLD,
    JOBFILTER_TIMING_CV_THRESHOLD,
    JOBFILTER_SCORE_ALERT_THRESHOLD,

    ZENY_TOTAL_GAIN_HOUR_THRESHOLD,
    ZENY_SINGLE_GAIN_THRESHOLD,
    ZENY_NPC_GAIN_COUNT_THRESHOLD,
    ZENY_TOTAL_GAIN_EXTREME_THRESHOLD,
    ZENY_SCORE_ALERT_THRESHOLD,

    TRADE_TOTAL_ZENY_THRESHOLD,
    TRADE_SINGLE_ZENY_THRESHOLD,
    TRADE_TOTAL_ITEMS_THRESHOLD,
    TRADE_COMBINED_ZENY_THRESHOLD,
    TRADE_COMBINED_ITEMS_THRESHOLD,
    TRADE_SCORE_ALERT_THRESHOLD,
)


class AntiBotDetector:
    def __init__(self) -> None:
        self.events_by_char: Dict[int, Deque[Event]] = defaultdict(deque)

    def add_event(self, event: Event) -> None:
        fila = self.events_by_char[event.char_id]
        fila.append(event)
        self._remove_old_events(event.char_id, event.timestamp)

    def _remove_old_events(self, char_id: int, now: float) -> None:
        fila = self.events_by_char[char_id]
        while fila and (now - fila[0].timestamp) > WINDOW_SECONDS:
            fila.popleft()

    def analyze_char(self, char_id: int) -> Dict:
        eventos = list(self.events_by_char[char_id])

        if len(eventos) < 2:
            primeiro = eventos[0] if eventos else None
            return {
                "char_id": char_id,
                "account_id": primeiro.account_id if primeiro else None,
                "account_login": primeiro.account_login if primeiro else "Desconhecido",
                "char_name": primeiro.char_name if primeiro else "Desconhecido",
                "score": 0,
                "farm_score": 0,
                "jobfilter_score": 0,
                "zeny_score": 0,
                "trade_score": 0,
                "suspeita_farm_bot": False,
                "suspeita_jobfilter": False,
                "suspeita_zeny_bug": False,
                "suspeita_trade_abusivo": False,
                "reasons": [],
                "event_count": len(eventos),
                "apm": 0.0,
                "focus_class_ratio": 0.0,
                "target_switch_rate": 0.0,
                "same_skill_ratio": 0.0,
                "timing_cv": None,
                "route_repeat_ratio": 0.0,
                "mob_target_ratio": 0.0,
                "zeny_gain_last_hour": 0,
                "max_single_zeny_gain": 0,
                "npc_zeny_gain_count": 0,
                "total_trade_zeny": 0,
                "max_single_trade_zeny": 0,
                "total_trade_items": 0,
            }

        score = 0
        reasons: List[str] = []

        duration = max(eventos[-1].timestamp - eventos[0].timestamp, 1)
        apm = len(eventos) / (duration / 60)

        if apm > BOT_APM_THRESHOLD:
            score += 2
            reasons.append(f"APM alto ({apm:.1f})")

        deltas = []
        for i in range(1, len(eventos)):
            delta = eventos[i].timestamp - eventos[i - 1].timestamp
            deltas.append(delta)

        timing_cv = None
        if len(deltas) >= 3:
            avg_delta = mean(deltas)
            std_delta = pstdev(deltas) if len(deltas) > 1 else 0.0
            if avg_delta > 0:
                timing_cv = std_delta / avg_delta
                if timing_cv < BOT_TIMING_CV_THRESHOLD:
                    score += 3
                    reasons.append(f"Timing muito regular (cv={timing_cv:.3f})")

        skill_events = [
            e.skill_id for e in eventos
            if e.event_type == "skill" and e.skill_id is not None
        ]

        same_skill_ratio = 0.0
        if skill_events:
            skill_counts = Counter(skill_events)
            most_common_skill, count = skill_counts.most_common(1)[0]
            same_skill_ratio = count / len(skill_events)

            if len(skill_events) >= BOT_MIN_SKILL_EVENTS and same_skill_ratio > BOT_SAME_SKILL_RATIO_THRESHOLD:
                score += 2
                reasons.append(
                    f"Uso excessivo da mesma skill (skill_id={most_common_skill}, {same_skill_ratio:.0%})"
                )

        target_classes = [e.target_class for e in eventos if e.target_class is not None]

        focus_class_ratio = 0.0
        avg_nearby = mean([e.nearby_players for e in eventos]) if eventos else 0
        most_common_class = None

        if target_classes:
            class_counts = Counter(target_classes)
            most_common_class, count = class_counts.most_common(1)[0]
            focus_class_ratio = count / len(target_classes)

            if (
                len(target_classes) >= BOT_MIN_SKILL_EVENTS
                and focus_class_ratio > BOT_FOCUS_CLASS_RATIO_THRESHOLD
                and avg_nearby >= BOT_FOCUS_MIN_NEARBY_PLAYERS
            ):
                score += 2
                reasons.append(
                    f"Foco excessivo em classe {most_common_class} ({focus_class_ratio:.0%}) em ambiente lotado"
                )

        warp_count = sum(1 for e in eventos if e.event_type == "warp")
        if warp_count >= BOT_WARP_COUNT_THRESHOLD:
            score += 2
            reasons.append(f"Muitos warps/teleports na janela ({warp_count})")

        positions = [(e.x, e.y) for e in eventos if e.x is not None and e.y is not None]
        route_repeat_ratio = 0.0
        if len(positions) >= 10:
            unique_positions = len(set(positions))
            route_repeat_ratio = 1 - (unique_positions / len(positions))
            if route_repeat_ratio > BOT_ROUTE_REPEAT_RATIO_THRESHOLD:
                score += 2
                reasons.append(f"Rota/posição muito repetitiva ({route_repeat_ratio:.0%})")

        # FARM BOT
        farm_score = 0
        mob_events = [e for e in eventos if e.target_type == "mob"]
        mob_target_ratio = len(mob_events) / len(eventos) if eventos else 0.0
        unique_maps = len(set(e.map_name for e in eventos))

        if len(eventos) >= FARM_MIN_EVENTS and route_repeat_ratio > FARM_ROUTE_REPEAT_RATIO_THRESHOLD:
            farm_score += 3

        if timing_cv is not None and timing_cv < FARM_TIMING_CV_THRESHOLD:
            farm_score += 2

        if len(skill_events) >= BOT_MIN_SKILL_EVENTS and same_skill_ratio > FARM_SAME_SKILL_RATIO_THRESHOLD:
            farm_score += 2

        if unique_maps == 1 and len(eventos) >= FARM_MIN_EVENTS:
            farm_score += 2

        if mob_target_ratio > FARM_MOB_TARGET_RATIO_THRESHOLD:
            farm_score += 2

        suspeita_farm_bot = farm_score >= FARM_SCORE_ALERT_THRESHOLD
        if suspeita_farm_bot:
            reasons.append("Comportamento compatível com Farm Bot detectado")

        # JOBFILTER
        jobfilter_score = 0

        target_switch_rate = 1.0
        if len(target_classes) >= 2:
            switches = 0
            for i in range(1, len(target_classes)):
                if target_classes[i] != target_classes[i - 1]:
                    switches += 1
            target_switch_rate = switches / (len(target_classes) - 1)

        if focus_class_ratio > JOBFILTER_FOCUS_CLASS_RATIO_THRESHOLD and len(target_classes) >= JOBFILTER_MIN_TARGET_EVENTS:
            jobfilter_score += 3

        if avg_nearby >= JOBFILTER_MIN_NEARBY_PLAYERS:
            jobfilter_score += 2

        if len(target_classes) >= JOBFILTER_MIN_TARGET_EVENTS and target_switch_rate < JOBFILTER_TARGET_SWITCH_RATE_THRESHOLD:
            jobfilter_score += 2

        if len(skill_events) >= BOT_MIN_SKILL_EVENTS and same_skill_ratio > JOBFILTER_SAME_SKILL_RATIO_THRESHOLD:
            jobfilter_score += 2

        if timing_cv is not None and timing_cv < JOBFILTER_TIMING_CV_THRESHOLD:
            jobfilter_score += 2

        suspeita_jobfilter = jobfilter_score >= JOBFILTER_SCORE_ALERT_THRESHOLD
        if suspeita_jobfilter:
            reasons.append("Comportamento compatível com JobFilter detectado")

        # ZENY BUG
        zeny_events = [
            e for e in eventos
            if e.event_type == "zeny_gain" and e.zeny_amount is not None
        ]

        zeny_gain_last_hour = sum(e.zeny_amount for e in zeny_events)
        max_single_zeny_gain = max((e.zeny_amount for e in zeny_events), default=0)
        npc_zeny_gain_count = sum(1 for e in zeny_events if e.zeny_source == "npc")

        zeny_score = 0

        if zeny_gain_last_hour >= ZENY_TOTAL_GAIN_HOUR_THRESHOLD:
            zeny_score += 3

        if max_single_zeny_gain >= ZENY_SINGLE_GAIN_THRESHOLD:
            zeny_score += 3

        if npc_zeny_gain_count >= ZENY_NPC_GAIN_COUNT_THRESHOLD:
            zeny_score += 2

        if zeny_gain_last_hour >= ZENY_TOTAL_GAIN_EXTREME_THRESHOLD:
            zeny_score += 3

        suspeita_zeny_bug = zeny_score >= ZENY_SCORE_ALERT_THRESHOLD
        if suspeita_zeny_bug:
            reasons.append("Comportamento compatível com possível bug de zeny detectado")

        # TRADE
        trade_events = [e for e in eventos if e.event_type == "trade"]

        total_trade_zeny = sum(e.trade_zeny or 0 for e in trade_events)
        max_single_trade_zeny = max((e.trade_zeny or 0 for e in trade_events), default=0)
        total_trade_items = sum(e.trade_item_count or 0 for e in trade_events)

        trade_score = 0

        if total_trade_zeny >= TRADE_TOTAL_ZENY_THRESHOLD:
            trade_score += 3

        if max_single_trade_zeny >= TRADE_SINGLE_ZENY_THRESHOLD:
            trade_score += 2

        if total_trade_items >= TRADE_TOTAL_ITEMS_THRESHOLD:
            trade_score += 2

        if (
            total_trade_zeny >= TRADE_COMBINED_ZENY_THRESHOLD
            and total_trade_items >= TRADE_COMBINED_ITEMS_THRESHOLD
        ):
            trade_score += 3

        suspeita_trade_abusivo = trade_score >= TRADE_SCORE_ALERT_THRESHOLD
        if suspeita_trade_abusivo:
            reasons.append("Trade com muito zeny/itens em curto período detectado")

        return {
            "char_id": char_id,
            "account_id": eventos[-1].account_id,
            "account_login": eventos[-1].account_login,
            "char_name": eventos[-1].char_name,
            "score": score,
            "farm_score": farm_score,
            "jobfilter_score": jobfilter_score,
            "zeny_score": zeny_score,
            "trade_score": trade_score,
            "suspeita_farm_bot": suspeita_farm_bot,
            "suspeita_jobfilter": suspeita_jobfilter,
            "suspeita_zeny_bug": suspeita_zeny_bug,
            "suspeita_trade_abusivo": suspeita_trade_abusivo,
            "reasons": reasons,
            "event_count": len(eventos),
            "apm": round(apm, 2),
            "focus_class_ratio": round(focus_class_ratio, 2),
            "target_switch_rate": round(target_switch_rate, 2),
            "same_skill_ratio": round(same_skill_ratio, 2),
            "timing_cv": round(timing_cv, 3) if timing_cv is not None else None,
            "route_repeat_ratio": round(route_repeat_ratio, 2),
            "mob_target_ratio": round(mob_target_ratio, 2),
            "zeny_gain_last_hour": zeny_gain_last_hour,
            "max_single_zeny_gain": max_single_zeny_gain,
            "npc_zeny_gain_count": npc_zeny_gain_count,
            "total_trade_zeny": total_trade_zeny,
            "max_single_trade_zeny": max_single_trade_zeny,
            "total_trade_items": total_trade_items,
        }

    def analyze_all(self) -> List[Dict]:
        results = []
        for char_id in self.events_by_char:
            results.append(self.analyze_char(char_id))

        return sorted(
            results,
            key=lambda x: (
                x["score"],
                x["farm_score"],
                x["jobfilter_score"],
                x["zeny_score"],
                x["trade_score"],
            ),
            reverse=True
        )