import os
from groq import Groq
from pydantic import BaseModel
from typing import Optional
import json

from config import settings
from utils.logger import setup_logger

logger = setup_logger()

class LLMClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.error("❌ ERRORE: GROQ_API_KEY non trovata nel file .env!")
            raise ValueError("API Key mancante.")

        # Inizializza il client ufficiale di Groq
        self.client = Groq(api_key=self.api_key)

        # Scegliamo un modello veloce e potente per i JSON (llama-3.1-8b-instant è ottimo per questo)
        self.model = "llama-3.1-8b-instant"

    def generate_json(self, prompt: str) -> dict:
        """Invia un prompt a Groq e forza l'output in formato JSON."""
        logger.debug(f"Inviando richiesta a Groq (modello: {self.model})...")
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sei un assistente per l'estrazione dati. Rispondi SEMPRE e SOLO con un oggetto JSON valido. Non includere saluti, spiegazioni o markdown extra come ```json."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                # Temperature bassa (0.1) perché vogliamo risposte deterministiche e precise per l'estrazione dati
                temperature=0.1,
                # Chiediamo esplicitamente a Groq di formattare l'output come JSON
                response_format={"type": "json_object"},
            )

            # Estraiamo il testo della risposta
            response_text = chat_completion.choices[0].message.content

            # Lo convertiamo da stringa a dizionario Python
            return json.loads(response_text)

        except Exception as e:
            logger.error(f"Errore durante la chiamata LLM: {e}")
            return {"error": str(e), "status": "failed"}

# Crea un'istanza pronta all'uso
llm = LLMClient()
