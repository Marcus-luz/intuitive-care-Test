import pandas as pd
import zipfile
import os
import re

class DataProcessor:
    def __init__(self, data_dir='../../data'):
        # Define o caminho absoluto para a pasta data para evitar erros de diretório
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), data_dir))
        
        # Mapeamento atualizado baseado na estrutura real vista nos arquivos da ANS
        # REG_ANS e DESCRICAO são as âncoras para identificação resiliente
        self.column_map = {
            'RegistroANS': ['REG_ANS', 'Registro ANS', 'NR_REG_ANS'],
            'Descricao': ['DESCRICAO', 'DS_CONTA', 'Descricao'],
            'ValorDespesas': ['VL_SALDO_FINAL', 'VALOR', 'VL_SALDO', 'VL_EVENTO', 'DESPESA']
        }

    def unzip_files(self):
        """1.2: Extrai todos os arquivos ZIP na pasta data automaticamente[cite: 33, 34]."""
        for item in os.listdir(self.data_dir):
            if item.endswith('.zip') and 'consolidado' not in item:
                file_path = os.path.join(self.data_dir, item)
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    print(f"Extraindo: {item}")
                    zip_ref.extractall(self.data_dir)

    def is_target_file(self, filename):
        """1.2: Identifica arquivos CSV de dados (ex: 1T2025.csv) de forma resiliente."""
        # Aceitamos CSVs que não sejam arquivos já processados ou cadastros
        return filename.lower().endswith('.csv') and 'consolidado' not in filename.lower() and 'operadoras' not in filename.lower()

    def normalize_columns(self, df):
        """1.2: Identifica automaticamente a estrutura e normaliza os dados[cite: 37]."""
        renamed = {}
        for target, synonyms in self.column_map.items():
            for col in df.columns:
                if col.strip().upper() in [s.upper() for s in synonyms]:
                    renamed[col] = target
                    break
        return df.rename(columns=renamed)

    def process_file(self, file_path, year, quarter):
        """1.2: Processamento incremental (Chunks) filtrando por conteúdo[cite: 35, 38]."""
        ext = os.path.splitext(file_path)[1].lower()
        df_list = []

        try:
            if ext in ['.csv', '.txt']:
                for encoding in ['utf-8', 'latin1']:
                    try:
                        # Trade-off: Processamento Incremental para volume variável [cite: 38, 39]
                        reader = pd.read_csv(file_path, sep=None, engine='python', 
                                           chunksize=50000, encoding=encoding)
                        for chunk in reader:
                            chunk = self.normalize_columns(chunk)
                            
                            # FILTRO DE CONTEÚDO: Identifica despesas pela Descrição da conta 
                            if 'Descricao' in chunk.columns:
                                mask = chunk['Descricao'].astype(str).str.contains('DESPESA|EVENTO|SINISTRO', case=False, na=False)
                                chunk = chunk[mask].copy()
                            
                            # Normalização do valor (trata vírgulas e converte para float)
                            if 'ValorDespesas' in chunk.columns:
                                chunk['ValorDespesas'] = pd.to_numeric(chunk['ValorDespesas'].astype(str).str.replace(',', '.'), errors='coerce')
                            
                            # Mantemos apenas o RegistroANS para consolidação
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

    # =========================================================================
    # NOVA ESTRATÉGIA ITEM 1.3: CONSOLIDAÇÃO POR IDENTIFICADOR ÚNICO (REG_ANS)
    # =========================================================================

    def clean_and_consolidate(self, df):
        """1.3: Saneamento financeiro e preparação do contrato de saída[cite: 40, 43]."""
        print("Iniciando saneamento dos dados financeiros...")

        # A. Tratamento de Valores zerados ou negativos 
        # Justificativa: Despesas de sinistros devem ser positivas para análise crítica.
        initial_count = len(df)
        df = df[df['ValorDespesas'] > 0].copy()
        print(f"-> Removidos {initial_count - len(df)} registros inválidos (<= 0).")

        # B. Normalização de formatos de data/trimestre 
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip().str.upper()
        df['Ano'] = df['Ano'].astype(str).str.strip()

        # C. Estratégia de Identificador Único: Preparação para o Teste 2
        # Como o dado contábil original não possui CNPJ nem Razão Social,
        # usamos o RegistroANS como ID único para satisfazer as colunas do 1.3.
        # O preenchimento real será feito no Teste 2.2 (Enriquecimento).
        df['CNPJ'] = df['RegistroANS'].astype(str).str.zfill(6) # Usamos o REG_ANS como ID temporário
        df['RazaoSocial'] = "PENDENTE_ENRIQUECIMENTO"

        # D. Tratamento de duplicatas por Identificador/Ano/Trimestre [cite: 45]
        df = df.drop_duplicates(subset=['CNPJ', 'Ano', 'Trimestre'], keep='first')

        return df

    def save_final_output(self, df):
        """1.3: Gera o CSV consolidado com as 5 colunas obrigatórias e zipa[cite: 41, 42, 52]."""
        csv_path = os.path.join(self.data_dir, 'consolidado_despesas.csv')
        zip_path = os.path.join(self.data_dir, 'consolidado_despesas.zip')

        # Colunas obrigatórias conforme exigência do item 1.3 
        cols = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
        df.to_csv(csv_path, index=False, encoding='utf-8', columns=cols)

        # Compactação final [cite: 52]
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(csv_path, arcname='consolidado_despesas.csv')
        
        print(f"\nSucesso! Arquivo final gerado: {zip_path}")

    def run(self):
        """Orquestra o fluxo do Teste 1 usando a Estratégia de Identificador Único."""
        self.unzip_files()
        all_dfs = []
        
        print(f"Arquivos na pasta /data: {os.listdir(self.data_dir)}")
        
        for file in os.listdir(self.data_dir):
            if self.is_target_file(file):
                print(f"Processando arquivo: {file}")
                
                # Extração resiliente de Metadados Temporais
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
            print("Nenhum dado compatível foi encontrado. Verifique se os arquivos CSV estão na pasta /data.")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()