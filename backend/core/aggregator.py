import pandas as pd
import os
import zipfile  # Import necessário para o desafio de compactação

class DataAggregator:
    """
    2.3: Responsável por agrupar os dados e calcular métricas estatísticas
    conforme exigido pelo teste (Total, Média e Desvio Padrão).
    """
    def __init__(self, data_dir):
        # Ajuste Sênior: Recebe o caminho absoluto injetado pelo main.py
        self.data_dir = os.path.abspath(data_dir)

    def aggregate_expenses(self, df_enriquecido):
        """
        2.3: Agrupa os dados por CNPJ, RazaoSocial e UF para gerar o relatório final.
        Também limpa a acentuação e gera o histórico para os gráficos.
        """
        print("Iniciando processamento e agregação estatística...")

        # 1. --- FILTRO CONTRA CORRUPÇÃO DE CARACTERES ---
        def fix_broken_text(text):
            if not isinstance(text, str): return text
            try:
                if "Ã" in text:
                    return text.encode('latin-1').decode('utf-8')
            except:
                pass
            return text

        print("Limpando possíveis erros de acentuação nos nomes...")
        df_enriquecido['RazaoSocial'] = df_enriquecido['RazaoSocial'].apply(fix_broken_text)
        
        # AJUSTES DE SANEAMENTO
        df_enriquecido['RazaoSocial'] = df_enriquecido['RazaoSocial'].str.strip()
        df_enriquecido['CNPJ'] = df_enriquecido['CNPJ'].astype(str).str.strip()

        # 2. --- SALVAMENTO DO HISTÓRICO PARA OS GRÁFICOS ---
        hist_path = os.path.join(self.data_dir, 'historico_final.csv')
        df_enriquecido.to_csv(hist_path, index=False, encoding='utf-8-sig')

        # 3. --- LÓGICA DO REQUISITO 2.3 (AGREGAÇÃO) ---
        # Calculamos Total, Média e Desvio Padrão
        # Nota: A média de despesas por trimestre é o resultado de ValorDespesas.mean() 
        # se cada linha do df_enriquecido for um trimestre diferente.
        agg_df = df_enriquecido.groupby(['CNPJ', 'RazaoSocial', 'UF']).agg(
            Total_Despesas=('ValorDespesas', 'sum'),
            Media_Trimestral=('ValorDespesas', 'mean'),
            Desvio_Padrao=('ValorDespesas', 'std')
        ).reset_index()

        agg_df['Desvio_Padrao'] = agg_df['Desvio_Padrao'].fillna(0)

        # 4. ORDENAÇÃO CONFORME REQUISITO 2.3 (Maior para Menor)
        agg_df = agg_df.sort_values(by='Total_Despesas', ascending=False)

        return agg_df

    def save_report(self, df_final):
        """
        Salva o resumo final em despesas_agregadas.csv e 
        COMPACTA em Teste_{seu_nome}.zip conforme o desafio do PDF.
        """
        csv_name = 'despesas_agregadas.csv'
        output_path = os.path.join(self.data_dir, csv_name)
        
        # Salva o CSV (usamos separador ';' para compatibilidade Excel BR)
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig', sep=';')
        print(f"Relatório de agregação gerado em: {output_path}")

        # --- SOLUÇÃO DO DESAFIO ADICIONAL ---
        zip_name = 'Teste_Marcus_Vinicius_Luz.zip'
        zip_path = os.path.join(self.data_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(output_path, arcname=csv_name)
        
        print(f"📦 Desafio Adicional Concluído: {zip_name} criado com sucesso!")
        return zip_path