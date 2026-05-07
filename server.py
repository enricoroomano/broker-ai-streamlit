import os
import tempfile
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor

from agents.polizza_agent import PolizzaExtractor
from utils.logger import setup_logger

logger = setup_logger()

# Configurazione FastAPI
app = FastAPI(title="Broker AI API", version="1.0.0")

# Abilita CORS se necessario per frontend separati
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta la cartella static per servire l'interfaccia web
app.mount("/static", StaticFiles(directory="static"), name="static")

extractor = PolizzaExtractor()
executor = ThreadPoolExecutor(max_workers=5)

def elabora_file_sincrono(file_content: bytes, file_name: str) -> dict:
    """Funzione worker per l'estrazione"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_pdf_path = tmp_file.name

    try:
        testo_grezzo = extractor.extract_text_from_pdf(tmp_pdf_path)
        if testo_grezzo:
            risultato = extractor.analyze_policy(testo_grezzo)
            risultato['nome_file'] = file_name
            return risultato
        else:
            return {"nome_file": file_name, "error": "Documento vuoto o illeggibile."}
    except Exception as e:
        return {"nome_file": file_name, "error": str(e)}
    finally:
        Path(tmp_pdf_path).unlink(missing_ok=True)

@app.post("/api/extract")
async def extract_policies(files: list[UploadFile] = File(...)):
    """Endpoint API che riceve i file e li processa in parallelo"""
    logger.info(f"Ricevuta richiesta di elaborazione per {len(files)} file.")

    # Leggiamo il contenuto dei file in memoria in modo asincrono
    file_contents = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"Il file {file.filename} non è un PDF.")
        content = await file.read()
        file_contents.append((content, file.filename))

    # Eseguiamo l'elaborazione pesante in un ThreadPool per non bloccare il server asincrono
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(executor, elabora_file_sincrono, content, name)
        for content, name in file_contents
    ]

    risultati = await asyncio.gather(*tasks)
    return {"status": "success", "data": risultati}

@app.get("/")
async def root():
    """Route principale che serve l'interfaccia grafica"""
    return FileResponse('static/index.html')
