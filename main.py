from utils.logger import setup_logger
from agents.polizza_agent import PolizzaExtractor
from pathlib import Path
import json

logger = setup_logger()

def main():
    logger.info("🚀 Insurance Assistant avviato")

    # Percorso del PDF di prova
    pdf_path = Path("input_polizze/esempio_polizza_rc_auto.pdf")

    if not pdf_path.exists():
        logger.error(f"File non trovato: {pdf_path}")
        return

    # Inizializza l'estrattore
    extractor = PolizzaExtractor()

    # Fase 1: Estrai il testo dal PDF
    testo_grezzo = extractor.extract_text_from_pdf(str(pdf_path))

    if testo_grezzo:
         # Fase 2: Manda il testo a Groq per l'estrazione strutturata
         risultato = extractor.analyze_policy(testo_grezzo)

         # Fase 3: Stampa il risultato (formattato in modo leggibile)
         logger.info("\n✅ Dati estratti con successo:")
         print(json.dumps(risultato, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
