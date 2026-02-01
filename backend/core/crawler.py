import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

# URL base ajustada conforme sua análise do HTML
BASE_URL_ANS = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/" 

# =========================================================================
# ITEM 2.2: ENRIQUECIMENTO DE DADOS - EXTRAÇÃO (CADASTRO DE OPERADORAS) 
# =========================================================================
URL_OPERADORAS_ATVAS = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"

def fetch_ans_files(base_url=BASE_URL_ANS):
    """
    1.1: Navega na pasta de demonstrações e baixa os ZIPs dos últimos 3 trimestres.
    """
    try:
        print(f"Acessando: {base_url}")
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Identifica pastas de anos (ex: 2024/, 2025/) 
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
            if quarters_found >= 3: break 

            year_url = urljoin(base_url, year)
            print(f"Verificando ano: {year}")
            
            y_res = requests.get(year_url)
            y_soup = BeautifulSoup(y_res.text, 'html.parser')
            
            quarter_links = sorted(
                [a['href'] for a in y_soup.find_all('a') if a['href'] != '../'],
                reverse=True
            )

            for q in quarter_links:
                if quarters_found >= 3: break
                
                q_url = urljoin(year_url, q)
                q_res = requests.get(q_url)
                q_soup = BeautifulSoup(q_res.text, 'html.parser')
                
                zip_links = [urljoin(q_url, a['href']) for a in q_soup.find_all('a') 
                             if a['href'].lower().endswith('.zip')]

                if zip_links:
                    print(f"-> Encontrado trimestre {q} no ano {year}")
                    for link in zip_links:
                        file_name = link.split('/')[-1]
                        dest = os.path.join(data_dir, file_name)
                        
                        print(f"   Baixando ZIP: {file_name}...")
                        with requests.get(link, stream=True) as r:
                            r.raise_for_status()
                            with open(dest, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        
                        downloaded_paths.append(dest)
                    
                    quarters_found += 1
        
        return downloaded_paths

    except Exception as e:
        print(f"Erro no Crawler Financeiro: {e}")
        return []

# =========================================================================
# IMPLEMENTAÇÃO DO ITEM 2.2: DOWNLOAD DO CADASTRO
# =========================================================================
def fetch_operator_registry(base_url=URL_OPERADORAS_ATVAS):
    """
    2.2: Baixa o arquivo CSV de Dados Cadastrais das Operadoras Ativas[cite: 68].
    """
    try:
        print(f"Acessando diretório de operadoras: {base_url}")
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Busca dinâmica pelo arquivo Relatorio_cadop.csv visto na imagem
        target_link = None
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'relatorio_cadop' in href.lower() and href.lower().endswith('.csv'):
                target_link = urljoin(base_url, href)
                break

        if not target_link:
            print("Erro: Arquivo Relatorio_cadop.csv não encontrado no servidor.")
            return None

        # Define caminho de destino na pasta /data
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        dest_path = os.path.join(data_dir, 'operadoras_ativas.csv')

        print(f"Iniciando download do cadastro: {target_link}")
        with requests.get(target_link, stream=True) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        print(f"Cadastro de operadoras salvo com sucesso em: {dest_path}")
        return dest_path

    except Exception as e:
        print(f"Erro ao baixar cadastro de operadoras: {e}")
        return None

if __name__ == "__main__":
    print("--- INICIANDO COLETA DE DADOS ANS ---")
    
    # 1.1: Download das Demonstrações Contábeis
    arquivos = fetch_ans_files()
    
    # 2.2: Download do Cadastro de Operadoras
    cadastro = fetch_operator_registry()
    
    print("\n--- RESUMO DA EXTRAÇÃO ---")
    print(f"Arquivos ZIP financeiros: {len(arquivos)}")
    print(f"Arquivo de cadastro: {'Baixado com sucesso' if cadastro else 'Falha no download'}")