import time

from detector import AntiBotDetector
from simulator import generate_events

from actions import (
    build_action_record,
    describe_action,
    load_penalties_history,
    save_penalties_history
)

from discord_alerts import send_discord_alert
from event_filter import should_process_event, event_matches_context


SCAN_INTERVAL_SECONDS = 3600   # 1 hora=3600

def run_analysis_cycle():

    detector = AntiBotDetector()

    events = generate_events()

    total_events = len(events)
    filtered_events = 0
    ignored_events = 0

    for event in events:

        if not should_process_event(event):
            ignored_events += 1
            continue

        if not event_matches_context(event):
            ignored_events += 1
            continue

        detector.add_event(event)
        filtered_events += 1

    resultados = detector.analyze_all()

    penalties_history = load_penalties_history()

    print("\n=========== NOVO CICLO DE ANÁLISE ===========\n")
    print(f"Eventos gerados: {total_events}")
    print(f"Eventos processados: {filtered_events}")
    print(f"Eventos ignorados: {ignored_events}")
    print("--------------------------------\n")

    for r in resultados:

        print("Char:", r["char_name"])
        print("Login:", r["account_login"])
        print("Score:", r["score"])
        print("Farm Score:", r.get("farm_score", 0))
        print("JobFilter Score:", r.get("jobfilter_score", 0))
        print("Zeny Score:", r.get("zeny_score", 0))
        print("Trade Score:", r.get("trade_score", 0))

        action = build_action_record(r, penalties_history)

        print("Ação:", describe_action(action))

        send_discord_alert(r, action)

        print("--------------------------------")

    save_penalties_history(penalties_history)


def main():

    print("Sistema Antibot iniciado.")

    while True:

        run_analysis_cycle()

        print(f"\nPróxima análise em {SCAN_INTERVAL_SECONDS/60} minutos...\n")

        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()