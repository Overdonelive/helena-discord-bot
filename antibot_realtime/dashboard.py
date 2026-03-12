import streamlit as st

from detector import AntiBotDetector
from simulator import generate_events
from ai_review import review_suspect_with_ai


def load_results():
    detector = AntiBotDetector()
    events = generate_events()

    for event in events:
        detector.add_event(event)

    return detector.analyze_all()


st.set_page_config(page_title="Painel Antibot", layout="wide")

st.title("Painel Antibot / Economia - Simulação em Tempo Real")

resultados = load_results()

total_jogadores = len(resultados)
total_suspeitos_bot = sum(1 for r in resultados if r["score"] >= 5)
total_suspeitos_farm = sum(1 for r in resultados if r["farm_score"] >= 6)
total_suspeitos_jobfilter = sum(1 for r in resultados if r["jobfilter_score"] >= 6)
total_suspeitos_zeny = sum(1 for r in resultados if r["zeny_score"] >= 5)
total_suspeitos_trade = sum(1 for r in resultados if r["trade_score"] >= 5)
total_geral = sum(
    1 for r in resultados
    if r["score"] >= 5
    or r["farm_score"] >= 6
    or r["jobfilter_score"] >= 6
    or r["zeny_score"] >= 5
    or r["trade_score"] >= 5
)

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Jogadores", total_jogadores)
col2.metric("Bots", total_suspeitos_bot)
col3.metric("Farm Bots", total_suspeitos_farm)
col4.metric("JobFilter", total_suspeitos_jobfilter)
col5.metric("Zeny Bug", total_suspeitos_zeny)
col6.metric("Trade", total_suspeitos_trade)

st.divider()

score_bot_min = st.slider("Score mínimo de bot", 0, 10, 5)
score_farm_min = st.slider("Score mínimo de farm bot", 0, 10, 6)
score_job_min = st.slider("Score mínimo de JobFilter", 0, 10, 6)
score_zeny_min = st.slider("Score mínimo de zeny", 0, 10, 5)
score_trade_min = st.slider("Score mínimo de trade", 0, 10, 5)

mostrar_so_suspeitos = st.checkbox("Mostrar apenas suspeitos", value=True)
somente_bot = st.checkbox("Somente bot", value=False)
somente_farm = st.checkbox("Somente farm bot", value=False)
somente_jobfilter = st.checkbox("Somente JobFilter", value=False)
somente_zeny = st.checkbox("Somente zeny bug", value=False)
somente_trade = st.checkbox("Somente trade abusivo", value=False)

filtrados = resultados

if mostrar_so_suspeitos:
    filtrados = [
        r for r in filtrados
        if r["score"] >= score_bot_min
        or r["farm_score"] >= score_farm_min
        or r["jobfilter_score"] >= score_job_min
        or r["zeny_score"] >= score_zeny_min
        or r["trade_score"] >= score_trade_min
    ]

if somente_bot:
    filtrados = [r for r in filtrados if r["score"] >= score_bot_min]

if somente_farm:
    filtrados = [r for r in filtrados if r["farm_score"] >= score_farm_min]

if somente_jobfilter:
    filtrados = [r for r in filtrados if r["jobfilter_score"] >= score_job_min]

if somente_zeny:
    filtrados = [r for r in filtrados if r["zeny_score"] >= score_zeny_min]

if somente_trade:
    filtrados = [r for r in filtrados if r["trade_score"] >= score_trade_min]

st.subheader("Lista de jogadores analisados")

if not filtrados:
    st.info("Nenhum jogador encontrado com os filtros atuais.")

for r in filtrados:
    with st.container():
        st.markdown(f"### {r['char_name']}")
        st.write(f"**Login da conta:** {r['account_login']}")
        st.write(f"**Account ID:** {r['account_id']}")
        st.write(f"**Char ID:** {r['char_id']}")
        st.write(f"**Score Bot:** {r['score']}")
        st.write(f"**Farm Score:** {r['farm_score']}")
        st.write(f"**JobFilter Score:** {r['jobfilter_score']}")
        st.write(f"**Zeny Score:** {r['zeny_score']}")
        st.write(f"**Trade Score:** {r['trade_score']}")
        st.write(f"**APM:** {r['apm']}")
        st.write(f"**Route Repeat Ratio:** {r['route_repeat_ratio']}")
        st.write(f"**Mob Target Ratio:** {r['mob_target_ratio']}")
        st.write(f"**Zeny na última hora:** {r['zeny_gain_last_hour']}")
        st.write(f"**Total trade zeny:** {r['total_trade_zeny']}")
        st.write(f"**Total itens em trade:** {r['total_trade_items']}")

        if (
            r["score"] >= 7
            or r["farm_score"] >= 6
            or r["jobfilter_score"] >= 6
            or r["zeny_score"] >= 5
            or r["trade_score"] >= 5
        ):
            st.error("ALERTA FORTE")
        elif r["score"] >= 5:
            st.warning("ALERTA")
        else:
            st.success("Normal")

        if r["suspeita_farm_bot"]:
            st.info("Comportamento compatível com Farm Bot detectado")

        if r["suspeita_jobfilter"]:
            st.info("Comportamento compatível com JobFilter detectado")

        if r["suspeita_zeny_bug"]:
            st.info("Possível bug/exploit de zeny detectado")

        if r["suspeita_trade_abusivo"]:
            st.info("Trade abusivo com muito zeny/itens detectado")

        if r["reasons"]:
            st.write("**Motivos detectados:**")
            for reason in r["reasons"]:
                st.write(f"- {reason}")

        if (
            r["score"] >= 7
            or r["farm_score"] >= 6
            or r["jobfilter_score"] >= 6
            or r["zeny_score"] >= 5
            or r["trade_score"] >= 5
        ):
            if st.button(f"Analisar com IA: {r['char_name']}", key=f"ai_{r['char_id']}"):
                with st.spinner("Consultando OpenAI..."):
                    parecer = review_suspect_with_ai(r)
                st.write("**Parecer da IA:**")
                st.text(parecer)

        st.divider()

st.subheader("Resumo textual")
st.write(f"**Total de jogadores analisados:** {total_jogadores}")
st.write(f"**Total suspeitos de bot:** {total_suspeitos_bot}")
st.write(f"**Total suspeitos de farm bot:** {total_suspeitos_farm}")
st.write(f"**Total suspeitos de JobFilter:** {total_suspeitos_jobfilter}")
st.write(f"**Total suspeitos de zeny bug:** {total_suspeitos_zeny}")
st.write(f"**Total suspeitos de trade abusivo:** {total_suspeitos_trade}")
st.write(f"**Total geral de suspeitos:** {total_geral}")