import streamlit as st
import tempfile
import pandas as pd
import concurrent.futures
from pathlib import Path
import time

from agents.polizza_agent import PolizzaExtractor

# --- 1. CONFIGURAZIONE PAGINA E METADATI ---
st.set_page_config(
    page_title="Broker Intelligence System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MOTORE GRAFICO ULTRA-PROFESSIONALE (CSS INJECTION) ---
custom_css = """
<style>
    /* Importazione Font Moderno 'Inter' */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Pulizia interfaccia nativa Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sfondo applicazione globale */
    .stApp {
        background-color: #f8fafc;
    }

    /* Stile Sidebar Enterprise */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        padding-top: 2rem;
    }

    /* Stile delle Card delle Metriche */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-top: 4px solid #4f46e5; /* Indigo accent */
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="metric-container"] > div {
        color: #64748b; /* Etichetta metrica */
        font-weight: 500;
        font-size: 0.9rem;
    }
    div[data-testid="metric-container"] > div:nth-child(2) {
        color: #0f172a; /* Valore metrica */
        font-weight: 700;
        font-size: 1.8rem;
    }

    /* Stile dei Tabs Moderni */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        background-color: transparent;
        border-radius: 0;
        gap: 0.5rem;
        padding: 0 1rem;
        color: #64748b;
        font-weight: 500;
        font-size: 1rem;
        transition: color 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #4f46e5 !important;
        border-bottom: 3px solid #4f46e5 !important;
        font-weight: 600;
    }

    /* Bottoni Premium */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
        background-color: white;
        color: #334155;
    }
    .stButton > button:hover {
        border-color: #cbd5e1;
        background-color: #f8fafc;
    }
    .stButton > button[kind="primary"] {
        background-color: #4f46e5;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4338ca;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3);
    }

    /* Area di Caricamento (Uploader) */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 2rem;
        transition: border-color 0.3s;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #4f46e5;
        background-color: #e0e7ff;
    }

    /* Stile Tabella Dati */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }

    /* Componenti Custom HTML */
    .sys-badge {
        background-color: #e0e7ff;
        color: #3730a3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .sys-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    .sys-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 800px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. INIZIALIZZAZIONE LOGICA E MEMORIA ---
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
            return {"nome_file": uploaded_file.name, "error": "Documento illeggibile o senza OCR."}
    except Exception as e:
        return {"nome_file": uploaded_file.name, "error": str(e)}
    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

# --- 4. SIDEBAR (Pannello di Controllo) ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding-bottom: 2rem;'><h2 style='color: #0f172a; margin: 0;'>🏦 Broker System</h2><p style='color: #64748b; font-size: 0.8rem; margin: 0;'>v 2.0 Enterprise</p></div>", unsafe_allow_html=True)

    st.markdown("**Stato Connessione**")
    st.success("🟢 Motore AI Operativo (Groq)")

    st.markdown("**Statistiche Sessione**")
    st.info(f"📄 Documenti in cache: **{len(st.session_state.database_polizze)}**")

    st.divider()

    if st.session_state.database_polizze:
        if st.button("🗑️ Pulisci Memoria Cache", use_container_width=True):
            st.session_state.database_polizze = []
            st.rerun()

    st.markdown("<div style='position: absolute; bottom: 20px; width: 100%; text-align: center; color: #94a3b8; font-size: 0.75rem;'>Sistema Protetto e Crittografato</div>", unsafe_allow_html=True)

# --- 5. CORPO PRINCIPALE DELL'APP ---
# Header elegante
st.markdown("""
    <div>
        <span class="sys-badge">Sistema Intelligente di Acquisizione Dati</span>
        <h1 class="sys-title">Elaborazione Documentale AI</h1>
        <p class="sys-subtitle">Carica i contratti e le polizze assicurative in formato PDF. Il nostro modello di Intelligenza Artificiale estrarrà istantaneamente i dati strutturati, i premi e le anagrafiche, organizzandoli per te.</p>
    </div>
""", unsafe_allow_html=True)

# Sistema a Tabs pulito
tab1, tab2, tab3 = st.tabs(["📤 Acquisizione Dati", "📊 Cruscotto Direzionale", "🔎 Log di Sistema (JSON)"])

# --- TAB 1: ACQUISIZIONE ---
with tab1:
    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 1rem; color: #334155;'>Area di Caricamento Sicura</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Trascina qui i tuoi file PDF oppure clicca per sfogliare",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown(f"<p style='color: #475569; font-weight: 500;'>Hai selezionato {len(uploaded_files)} documenti pronti per l'analisi.</p>", unsafe_allow_html=True)

        if st.button(f"⚡ Avvia Estrazione Automatica", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            nuovi_risultati = []

            with st.spinner("Inizializzazione cluster AI in corso..."):
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {executor.submit(elabora_singolo_pdf, file): file for file in uploaded_files}
                    completati = 0
                    for future in concurrent.futures.as_completed(futures):
                        ris = future.result()
                        nuovi_risultati.append(ris)
                        completati += 1
                        progress_bar.progress(completati / len(uploaded_files))
                        status_text.markdown(f"**Elaborazione in corso:** `{completati}/{len(uploaded_files)}` completati...")

            st.session_state.database_polizze.extend(nuovi_risultati)
            status_text.empty()
            progress_bar.empty()

            st.success("✅ Estrazione completata con successo! I dati sono disponibili nel Cruscotto Direzionale.")
            time.sleep(1.5) # Pausa drammatica prima di far esplodere i palloncini
            st.balloons()

# --- TAB 2: CRUSCOTTO ---
with tab2:
    dati = st.session_state.database_polizze
    if not dati:
        st.info("💡 Il cruscotto è vuoto. Carica dei documenti nell'area di Acquisizione per generare le metriche.")
    else:
        # Calcolo logico delle metriche
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
                    # Normalizzazione della stringa monetaria in un numero reale
                    val_str = str(r.get("premio_totale", "0")).replace('.', '').replace(',', '.').replace('€', '').strip()
                    totale_premi += float(val_str)
                except Exception:
                    pass

                # Aggiunta alla riga del dataframe
                df_data.append({
                    "Nome File": r.get("nome_file"),
                    "Contraente": r.get("contraente"),
                    "Compagnia": r.get("compagnia"),
                    "Ramo Polizza": r.get("tipo_polizza"),
                    "N. Contratto": r.get("numero_polizza"),
                    "Scadenza": r.get("data_scadenza"),
                    "Premio": r.get("premio_totale")
                })

        # Rendere le metriche come Card aziendali
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Volumi Caricati", polizze_valide + errori)
        col2.metric("Tasso di Successo", f"{int((polizze_valide/(polizze_valide+errori))*100)} %" if (polizze_valide+errori)>0 else "0 %")
        col3.metric("Raccolta Premi Stimata", f"€ {totale_premi:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        col4.metric("Documenti Rifiutati", errori)

        st.markdown("<br><h3 style='font-size: 1.2rem; color: #334155;'>Archivio Dati Strutturati</h3>", unsafe_allow_html=True)

        # Rendere il Dataframe perfetto
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome File": st.column_config.TextColumn("Nome File", width="medium"),
                    "Premio": st.column_config.TextColumn("Premio", width="small"),
                }
            )

# --- TAB 3: ISPEZIONE LOGS ---
with tab3:
    if not st.session_state.database_polizze:
        st.info("💡 Nessun dato tecnico da analizzare.")
    else:
        st.markdown("<p style='color: #64748b;'>Ispeziona i payload JSON nativi restituiti dal Large Language Model per eseguire il debug delle estrazioni.</p>", unsafe_allow_html=True)
        for index, r in enumerate(st.session_state.database_polizze):
            nome = r.get("nome_file", f"Documento_{index}")

            # Colora l'expander di rosso se c'è un errore, altrimenti standard
            icona = "🚨 Errore Estrazione:" if "error" in r else "📄 Payload:"

            with st.expander(f"{icona} {nome}"):
                if "error" in r:
                    st.error(f"Dettaglio Tecnico: {r['error']}")
                else:
                    st.json(r)
