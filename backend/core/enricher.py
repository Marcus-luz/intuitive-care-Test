import pandas as pd
import os

class DataEnricher:
    """
    2.2: Realiza o join entre o financeiro e o cadastro com tratamento de falhas.
    """
    def __init__(self, data_dir):
        # Injeção de dependência do caminho absoluto vindo da main.py
        self.data_dir = os.path.abspath(data_dir)
        
        # Mapeamento de sinônimos atualizado
        self.registry_map = {
            'RegistroANS_Real': ['REGISTRO_OPERADORA', 'Registro_ANS', 'Registro ANS', 'RegistroANS', 'REG_ANS'],
            'CNPJ_Real': ['CNPJ', 'NR_CNPJ', 'cnpj'],
            'RazaoSocial_Real': ['Razao_Social', 'Razao Social', 'RAZAO_SOCIAL', 'NM_RAZAO_SOCIAL'],
            'Modalidade': ['Modalidade', 'MODALIDADE'],
            'UF': ['UF', 'Sigla_UF', 'Estado']
        }

    def _normalize_registry_columns(self, df):
        """Identifica e renomeia as colunas do cadastro dinamicamente."""
        renamed = {}
        df.columns = [c.strip() for c in df.columns]
        
        for target, synonyms in self.registry_map.items():
            for col in df.columns:
                if col.upper() in [s.upper() for s in synonyms]:
                    renamed[col] = target
                    break
        return df.rename(columns=renamed)

    def enrich(self, df_financeiro):
        path_cad = os.path.join(self.data_dir, 'operadoras_ativas.csv')
        
        if not os.path.exists(path_cad):
            print(f"Erro: Cadastro não encontrado em {path_cad}")
            return df_financeiro

        print("Enriquecendo dados (Join)...")
        
        # --- AJUSTE CRÍTICO: Forçando iso-8859-1 para ler os nomes da ANS sem erro ---
        # A maioria dos arquivos de cadastro da ANS usa este encoding.
        df_cadastro = pd.read_csv(path_cad, sep=';', engine='python', encoding='iso-8859-1', dtype=str)
        df_cadastro = self._normalize_registry_columns(df_cadastro)

        if 'RazaoSocial_Real' in df_cadastro.columns:
            # Limpeza extra para remover espaços e garantir nomes limpos
            df_cadastro['RazaoSocial_Real'] = df_cadastro['RazaoSocial_Real'].str.strip()

        if 'RegistroANS_Real' not in df_cadastro.columns:
            print(f"Erro Crítico: Coluna de identificação não encontrada. Colunas: {df_cadastro.columns.tolist()}")
            return df_financeiro

        # Forçamos as chaves de busca para String (texto)
        df_financeiro['CNPJ'] = df_financeiro['CNPJ'].astype(str).str.strip()
        df_cadastro['RegistroANS_Real'] = df_cadastro['RegistroANS_Real'].astype(str).str.strip()

        # Tratamento de duplicatas
        df_cadastro = df_cadastro.drop_duplicates(subset=['RegistroANS_Real'], keep='first')

        # Join Inner
        df_final = pd.merge(
            df_financeiro, 
            df_cadastro[['RegistroANS_Real', 'CNPJ_Real', 'RazaoSocial_Real', 'Modalidade', 'UF']], 
            left_on='CNPJ', 
            right_on='RegistroANS_Real', 
            how='inner' 
        )

        # Atualiza colunas para o contrato final
        df_final['CNPJ'] = df_final['CNPJ_Real']
        df_final['RazaoSocial'] = df_final['RazaoSocial_Real']
        df_final['RegistroANS'] = df_final['RegistroANS_Real']
        
        return df_final.drop(columns=['CNPJ_Real', 'RazaoSocial_Real', 'RegistroANS_Real'])