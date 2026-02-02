import pandas as pd
import zipfile
import os
import re

class DataProcessor:
    def __init__(self, data_dir='../../data'):
        # Define o caminho absoluto para a pasta data para evitar erros de diretório
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), data_dir))
        
        # Mapeamento atualizado baseado na estrutura real vista nos arquivos da ANS
        self.column_map = {
            'RegistroANS': ['REG_ANS', 'Registro ANS', 'NR_REG_ANS'],
            'Descricao': ['DESCRICAO', 'DS_CONTA', 'Descricao'],
            'ValorDespesas': ['VL_SALDO_FINAL', 'VALOR', 'VL_SALDO', 'VL_EVENTO', 'DESPESA']
        }

    def unzip_files(self):
        """1.2: Extrai todos os arquivos ZIP na pasta data automaticamente."""
        for item in os.listdir(self.data_dir):
            if item.endswith('.zip') and 'consolidado' not in item:
                file_path = os.path.join(self.data_dir, item)
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    print(f"Extraindo: {item}")
                    zip_ref.extractall(self.data_dir)

    def is_target_file(self, filename):
        """1.2: Identifica arquivos CSV de dados de forma resiliente."""
        return filename.lower().endswith('.csv') and 'consolidado' not in filename.lower() and 'operadoras' not in filename.lower()

    def normalize_columns(self, df):
        """1.2: Identifica automaticamente a estrutura e normaliza os dados."""
        renamed = {}
        for target, synonyms in self.column_map.items():
            for col in df.columns:
                if col.strip().upper() in [s.upper() for s in synonyms]:
                    renamed[col] = target
                    break
        return df.rename(columns=renamed)

    def process_file(self, file_path, year, quarter):
        """1.2: Processamento incremental (Chunks) filtrando por conteúdo."""
        ext = os.path.splitext(file_path)[1].lower()
        df_list = []

        try:
            if ext in ['.csv', '.txt']:
                # CORREÇÃO DE LEITURA: Prioriza 'iso-8859-1' para ler corretamente os acentos da ANS
                for encoding in ['iso-8859-1', 'latin1', 'utf-8-sig', 'utf-8']:
                    try:
                        reader = pd.read_csv(file_path, sep=None, engine='python', 
                                           chunksize=50000, encoding=encoding)
                        for chunk in reader:
                            chunk = self.normalize_columns(chunk)
                            
                            if 'Descricao' in chunk.columns:
                                mask = chunk['Descricao'].astype(str).str.contains('DESPESA|EVENTO|SINISTRO', case=False, na=False)
                                chunk = chunk[mask].copy()
                            
                            if 'ValorDespesas' in chunk.columns:
                                chunk['ValorDespesas'] = pd.to_numeric(chunk['ValorDespesas'].astype(str).str.replace(',', '.'), errors='coerce')
                            
                            cols_to_keep = [c for c in ['RegistroANS', 'ValorDespesas'] if c in chunk.columns]
                            if cols_to_keep:
                                chunk = chunk[cols_to_keep]
                                chunk['Ano'] = year
                                chunk['Trimestre'] = quarter
                                df_list.append(chunk)
                        break 
                    except: continue
            
            if df_list:
                return pd.concat(df_list, ignore_index=True)
        except Exception as e:
            print(f"Aviso: Erro ao processar {file_path}: {e}")
        return None

    def clean_and_consolidate(self, df):
        """1.3: Saneamento financeiro e preparação do contrato de saída."""
        print("Iniciando saneamento dos dados financeiros...")

        initial_count = len(df)
        df = df[df['ValorDespesas'] > 0].copy()
        print(f"-> Removidos {initial_count - len(df)} registros inválidos (<= 0).")

        df['Trimestre'] = df['Trimestre'].astype(str).str.strip().str.upper()
        df['Ano'] = df['Ano'].astype(str).str.strip()

        df['CNPJ'] = df['RegistroANS'].astype(str).str.zfill(6) 
        df['RazaoSocial'] = "PENDENTE_ENRIQUECIMENTO"

        df = df.drop_duplicates(subset=['CNPJ', 'Ano', 'Trimestre'], keep='first')

        return df

    def save_final_output(self, df):
        """1.3: Gera o CSV consolidado com as 5 colunas obrigatórias e zipa."""
        csv_path = os.path.join(self.data_dir, 'consolidado_despesas.csv')
        zip_path = os.path.join(self.data_dir, 'consolidado_despesas.zip')

        cols = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
        
        # CORREÇÃO DE ESCRITA: Usar 'utf-8-sig' para que o arquivo intermediário não quebre acentos
        df.to_csv(csv_path, index=False, encoding='utf-8-sig', columns=cols)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(csv_path, arcname='consolidado_despesas.csv')
        
        print(f"\nSucesso! Arquivo final gerado: {zip_path}")

    def run(self):
        """Orquestra o fluxo do Teste 1."""
        self.unzip_files()
        all_dfs = []
        
        for file in os.listdir(self.data_dir):
            if self.is_target_file(file):
                print(f"Processando arquivo: {file}")
                
                year_match = re.search(r'20\d{2}', file)
                year = year_match.group() if year_match else "2024"
                
                q_match = re.search(r'(\d[tT]|\b\d{2}\b)', file)
                quarter = q_match.group() if q_match else "03"
                
                df_data = self.process_file(os.path.join(self.data_dir, file), year, quarter)
                if df_data is not None:
                    all_dfs.append(df_data)
        
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            cleaned_df = self.clean_and_consolidate(combined_df)
            self.save_final_output(cleaned_df)
        else:
            print("Nenhum dado compatível foi encontrado.")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()