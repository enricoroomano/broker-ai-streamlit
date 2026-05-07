import fitz  # PyMuPDF
import json
from pathlib import Path
from utils.logger import setup_logger
from utils.llm import llm # Importiamo il client che abbiamo appena creato!

logger = setup_logger()

class PolizzaExtractor:
    def __init__(self):
        # Usiamo il client LLM importato
        self.llm_client = llm

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Legge il testo grezzo dal file PDF."""
        logger.info(f"📄 Lettura del file: {Path(pdf_path).name}")
        try:
            doc = fitz.open(pdf_path)
            text = ""
            # Per evitare di mandare testi enormi all'LLM (che costano token),
            # spesso per i dati base bastano le prime 2-3 pagine.
            # Se vuoi leggere tutto, togli [:3]
            for page in doc[:3]:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error(f"Errore nella lettura del PDF {pdf_path}: {e}")
            return ""

    def analyze_policy(self, text: str) -> dict:
        """Invia il testo all'LLM e chiede un JSON strutturato."""
        if not text:
             return {"error": "Nessun testo fornito per l'analisi"}

        logger.info("🧠 Analisi del testo con l'Intelligenza Artificiale (Groq)...")

        # Prompt ingegnerizzato per ottenere i dati che ci interessano
        prompt = f"""
        Analizza con attenzione il seguente testo estratto da una polizza assicurativa.
        Estrai le seguenti informazioni e crea un oggetto JSON con queste chiavi esatte (se un dato non è presente, inserisci "non trovato"):

        - "compagnia": (string) Nome della compagnia assicurativa
        - "tipo_polizza": (string) Categoria principale (es. "RC Auto", "Casa", "Salute")
        - "numero_polizza": (string) Il codice univoco identificativo della polizza
        - "contraente": (string) Nome e Cognome del contraente
        - "data_decorrenza": (string) Data inizio copertura nel formato YYYY-MM-DD
        - "data_scadenza": (string) Data fine copertura nel formato YYYY-MM-DD
        - "premio_totale": (float) Importo del premio finito (solo il numero senza valuta, es. 550.70)

        Testo polizza:
        ---
        {text}
        ---
        """

        # Facciamo la vera chiamata a Groq
        risultato_json = self.llm_client.generate_json(prompt)
        return risultato_json
