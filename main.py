import subprocess
import time
import sys
import os
from run_etl import executar_pipeline

def start_api():
    print("\n🚀 Iniciando a API Backend (FastAPI)...")
    # Comando para rodar o uvicorn
    subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.api.main_api:app", "--reload"])

if __name__ == "__main__":
    print("      --- INTUITIVE CARE AUTO-SETUP ---")
    
    # 1. Roda o ETL
    setup_ok = executar_pipeline()
    
    if setup_ok:
        print("\n✅ ETL finalizado. Os dados estão prontos no banco.")
        
        # 2. Inicia a API
        start_api()
        print("\n💡 O Sistema Unificado (Frontend + Backend) está rodando em http://localhost:8000")
        print("💡 Documentação da API disponível em http://localhost:8000/docs")
        
        # Verifica se a pasta dist existe
        frontend_dist = os.path.join("frontend", "dist")
        if not os.path.exists(frontend_dist):
            print("\n⚠️  ATENÇÃO: A interface visual (Frontend) ainda não foi compilada.")
            print("⚠️  Abra o terminal na pasta 'frontend' e rode o comando: npm run build")
            print("⚠️  Depois reinicie este arquivo para ver a tela do sistema no navegador.")
        else:
            print("\n✅ Frontend compilado detectado! Tudo pronto para uso.")
            
    else:
        print("\n❌ O setup falhou. Verifique os erros acima e o arquivo pipeline.log.")