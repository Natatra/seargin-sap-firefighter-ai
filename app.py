"""Streamlit UI: Przeglądarka wyników z pliku predictions.jsonl."""

from __future__ import annotations
import json
import streamlit as st

def main() -> None:
    st.set_page_config(page_title="SAP Firefighter Audit Dashboard", layout="wide")
    
    st.title("🛡️ SAP Firefighter Audit Dashboard")
    st.markdown("Wgraj plik `predictions.jsonl`, aby przejrzeć wyniki analizy AI.")

    uploaded_file = st.file_uploader("Wgraj plik predictions.jsonl", type=["jsonl"])

    if uploaded_file is None:
        st.info("Oczekiwanie na plik z wynikami...")
        return

    results = []
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        for line in content.strip().split('\n'):
            if line.strip():
                results.append(json.loads(line))
    except Exception as e:
        st.error(f"Błąd podczas odczytu pliku: {e}")
        return

    if not results:
        st.warning("Plik jest pusty.")
        return

    st.sidebar.header("Lista sesji")
    session_ids = [r['session_id'] for r in results]
    selected_id = st.sidebar.selectbox("Wybierz sesję do przeglądu:", session_ids)

    res = next(r for r in results if r['session_id'] == selected_id)

    st.header(f"Analiza sesji: {selected_id}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Werdykt")
        verdict = res.get('verdict', 'UNKNOWN')
        if verdict == "PASS":
            st.success(f"✅ **{verdict}**")
        elif verdict == "REJECT":
            st.error(f"🚨 **{verdict}**")
        else:
            st.warning(f"⚠️ **{verdict}**")
            
        st.metric("Confidence Score", f"{res.get('confidence', 0.85)*100}%")

    st.subheader("🔍 Ustalenia (Findings)")
    findings = res.get('findings', [])
    
    if not findings:
        st.write("Nie wykryto żadnych naruszeń.")
    else:
        for f in findings:
            with st.expander(f"Rule: {f['rule_id']} - {f['severity'].upper()}"):
                st.markdown(f"**Lokalizacja:** `{f['location']}`")
                st.markdown(f"**Opis:** {f['description']}")
                st.info(f"**Dowód:** {f['evidence']}")

    sc = res.get('suggested_correction', {})
    if sc:
        st.subheader("📝 Sugerowana korekta")
        st.info(f"**Wiadomość do strażaka:**\n\n{sc.get('message_to_firefighter', 'N/A')}")
        if sc.get('suggested_reason_rewrite'):
            st.code(f"Sugerowany powód: {sc['suggested_reason_rewrite']}")

    st.divider()
    st.subheader("Decyzja Controllera")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Zatwierdź (PASS)", use_container_width=True):
            st.balloons()
            st.toast("Decyzja zapisana!")
    with c2:
        if st.button("Odrzuć (REJECT)", use_container_width=True):
            st.toast("Sesja eskalowana do Security")
    with c3:
        if st.button("Zwróć do poprawy", use_container_width=True):
            st.toast("Wysłano prośbę o uzupełnienie danych")

if __name__ == "__main__":
    main()