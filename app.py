import streamlit as st
import tempfile
import pandas as pd
import concurrent.futures
from pathlib import Path
import json

from agents.polizza_agent import PolizzaExtractor

# --- 1. CONFIGURAZIONE PAGINA E UI ---
st.set_page_config(page_title="Broker AI Pro", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #2563eb;
    }
    .saas-header { font-size: 2.5rem; font-weight: 800; color: #1e293b; margin-bottom: 0.5rem; }
    .saas-subheader { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 2. GESTIONE STATO (MEMORIA DELL'APP) ---
if 'database_polizze' not in st.session_state:
    st.session_state.database_polizze = []

@st.cache_resource
def get_extractor():
    return PolizzaExtractor()

extractor = get_extractor()

def elabora_singolo_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_pdf_path = tmp_file.name

    try:
        testo_grezzo = extractor.extract_text_from_pdf(tmp_pdf_path)
        if testo_grezzo:
            risultato = extractor.analyze_policy(testo_grezzo)
            risultato['nome_file'] = uploaded_file.name
            return risultato
        else:
            return {"nome_file": uploaded_file.name, "error": "Documento vuoto o scansionato senza OCR."}
    except Exception as e:
        return {"nome_file": uploaded_file.name, "error": str(e)}
    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🛡️ Broker AI Pro</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**Stato Sistema:**")
    st.success("Connesso a Groq AI")
    st.info(f"Polizze in memoria: **{len(st.session_state.database_polizze)}**")

    if st.button("🗑️ Svuota Memoria", use_container_width=True):
        st.session_state.database_polizze = []
        st.rerun()

# --- 4. LAYOUT PRINCIPALE ---
st.markdown('<div class="saas-header">Gestione Polizze Automatizzata</div>', unsafe_allow_html=True)
st.markdown('<div class="saas-subheader">Carica, analizza e gestisci il tuo portafoglio clienti con l\'Intelligenza Artificiale.</div>', unsafe_allow_html=True)

tab_upload, tab_dashboard, tab_dettagli = st.tabs(["📤 Importa Documenti", "📊 Cruscotto Portafoglio", "🔎 Ispezione Dati"])

# --- TAB 1: IMPORTAZIONE ---
with tab_upload:
    uploaded_files = st.file_uploader(
        "Seleziona o trascina multipli PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button(f"🚀 Avvia Analisi AI su {len(uploaded_files)} file", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            nuovi_risultati = []

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(elabora_singolo_pdf, file): file for file in uploaded_files}
                completati = 0
                for future in concurrent.futures.as_completed(futures):
                    ris = future.result()
                    nuovi_risultati.append(ris)
                    completati += 1
                    progress_bar.progress(completati / len(uploaded_files))
                    status_text.text(f"Elaborazione in corso: {completati}/{len(uploaded_files)} completati...")

            st.session_state.database_polizze.extend(nuovi_risultati)
            status_text.success("✅ Elaborazione completata! Vai alla scheda 'Cruscotto Portafoglio' per i risultati.")
            st.balloons()

# --- TAB 2: DASHBOARD ---
with tab_dashboard:
    dati = st.session_state.database_polizze
    if not dati:
        st.warning("Nessuna polizza in memoria. Carica dei documenti nella scheda 'Importa Documenti'.")
    else:
        totale_premi = 0.0
        polizze_valide = 0
        errori = 0
        df_data = []

        for r in dati:
            if "error" in r:
                errori += 1
            else:
                polizze_valide += 1
                try:
                    val_str = str(r.get("premio_totale", "0")).replace(',', '.').replace('€', '').strip()
                    totale_premi += float(val_str)
                except: pass

                df_data.append({
                    "File": r.get("nome_file"),
                    "Contraente": r.get("contraente"),
                    "Compagnia": r.get("compagnia"),
                    "Ramo": r.get("tipo_polizza"),
                    "N. Polizza": r.get("numero_polizza"),
                    "Premio (€)": r.get("premio_totale")
                })

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Totale Polizze", polizze_valide + errori)
        col2.metric("Estrazioni Riuscite", polizze_valide)
        col3.metric("Volume Premi", f"€ {totale_premi:,.2f}")
        col4.metric("Documenti con Errori", errori)

        if df_data:
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

# --- TAB 3: ISPEZIONE DATI ---
with tab_dettagli:
    if not st.session_state.database_polizze:
        st.info("Nessun dato da ispezionare.")
    else:
        for r in st.session_state.database_polizze:
            nome = r.get("nome_file", "File Sconosciuto")
            with st.expander(f"📄 {nome}"):
                if "error" in r:
                    st.error(f"Errore: {r['error']}")
                else:
                    st.json(r)
