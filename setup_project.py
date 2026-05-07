from pathlib import Path

project = Path(".")

dirs = ["utils", "agents", "data", "logs", "notebooks", "output", "templates"]

for d in dirs:
    (project / d).mkdir(exist_ok=True)
    (project / d / "__init__.py").touch(exist_ok=True)

files = {
    ".env": """GROQ_API_KEY=
OPENAI_API_KEY=

# Database
DB_PATH=data/polizze.db
""",

    ".gitignore": "venv/\n__pycache__/\n*.pyc\n.env\nlogs/\ndata/*.db\noutput/*.pdf\n",

    "requirements.txt": """python-dotenv
pydantic
pydantic-settings
requests
pymupdf
pandas
sqlalchemy
openpyxl
groq
openai
apscheduler
rich
""",

    "config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DB_PATH: str = "data/polizze.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
""",

    "main.py": """from utils.logger import setup_logger

logger = setup_logger()

def main():
    logger.info("🚀 Insurance Assistant avviato")
    print("Insurance Polizze AI Assistant")
    print("Pronto per estrarre polizze e automatizzare il tuo lavoro di broker.")

if __name__ == "__main__":
    main()
""",

    "README.md": """# Insurance Assistant

Automazione professionale per Broker Assicurativi
- Estrazione dati da polizze PDF
- Database centralizzato
- Monitoraggio scadenze
- Confronto preventivi
""",
}

for file_path, content in files.items():
    path = project / file_path
    path.write_text(content, encoding="utf-8")
    print(f"✅ Creato: {file_path}")

print("\n🎉 Progetto 'insurance-assistant' creato con successo!")
print("Prossimo comando: pip install -r requirements.txt")
