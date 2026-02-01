import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

# URL base ajustada conforme sua análise do HTML
BASE_URL_ANS = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/" 

def fetch_ans_files(base_url=BASE_URL_ANS):
    """
    Navega na pasta de demonstrações e baixa os ZIPs dos últimos 3 trimestres.
    """
    try:
        print(f"Acessando: {base_url}")
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Identifica pastas de anos (ex: 2024/, 2025/) 
        # Regex busca 4 dígitos seguidos de uma barra opcional
        year_links = sorted(
            [a['href'] for a in soup.find_all('a') if re.match(r'^\d{4}/?$', a['href'])],
            reverse=True
        )

        downloaded_paths = []
        quarters_found = 0

        # Define caminho absoluto para a pasta /data 
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        os.makedirs(data_dir, exist_ok=True)

        for year in year_links:
            if quarters_found >= 3: break # Objetivo: últimos 3 trimestres 

            year_url = urljoin(base_url, year)
            print(f"Verificando ano: {year}")
            
            y_res = requests.get(year_url)
            y_soup = BeautifulSoup(y_res.text, 'html.parser')
            
            # Busca pastas de trimestres (ex: 1T/, 2T/ ou 01/, 02/) 
            quarter_links = sorted(
                [a['href'] for a in y_soup.find_all('a') if a['href'] != '../'],
                reverse=True
            )

            for q in quarter_links:
                if quarters_found >= 3: break
                
                q_url = urljoin(year_url, q)
                q_res = requests.get(q_url)
                q_soup = BeautifulSoup(q_res.text, 'html.parser')
                
                # Identifica links de arquivos ZIP [cite: 33]
                zip_links = [urljoin(q_url, a['href']) for a in q_soup.find_all('a') 
                             if a['href'].lower().endswith('.zip')]

                if zip_links:
                    print(f"-> Encontrado trimestre {q} no ano {year}")
                    for link in zip_links:
                        file_name = link.split('/')[-1]
                        dest = os.path.join(data_dir, file_name)
                        
                        # Download incremental (Trade-off: Baixo uso de RAM) 
                        print(f"   Baixando: {file_name}...")
                        with requests.get(link, stream=True) as r:
                            r.raise_for_status()
                            with open(dest, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        
                        downloaded_paths.append(dest)
                    
                    quarters_found += 1
        
        return downloaded_paths

    except Exception as e:
        print(f"Erro no Crawler: {e}")
        return []

if __name__ == "__main__":
    print("--- INICIANDO TESTE DE INTEGRAÇÃO ANS ---")
    arquivos = fetch_ans_files()
    print(f"\nSucesso! {len(arquivos)} arquivos baixados na pasta /data.")