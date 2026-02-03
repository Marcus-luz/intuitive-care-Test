import subprocess
import time
import sys
from run_etl import executar_pipeline

def start_api():
    print("\n🚀 Iniciando a API Backend (FastAPI)...")
    # Comando para rodar o uvicorn
    # backend.api.main_api:app assume que sua estrutura é backend/api/main_api.py
    subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.api.main_api:app", "--reload"])

if __name__ == "__main__":
    print("      --- INTUITIVE CARE AUTO-SETUP ---")
    
    # 1. Roda o ETL
    setup_ok = executar_pipeline()
    
    if setup_ok:
        print("\n✅ ETL finalizado. Os dados estão prontos no banco.")
        # 2. Inicia a API
        start_api()
        print("\n💡 O Backend está rodando em http://localhost:8000")
        print("💡 Documentação disponível em http://localhost:8000/docs")
        print("\n⚠️  IMPORTANTE: Agora, abra um novo terminal na pasta 'frontend' e rode: npm run dev")
    else:
        print("\n❌ O setup falhou. Verifique os erros acima e o arquivo pipeline.log.")