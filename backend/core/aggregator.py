import pandas as pd
import os

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

        # 1. --- FILTRO "BOMBA ATÔMICA" CONTRA FUNDAÃÇÃOO ---
        # Reverte a corrupção de caracteres especiais caso ocorra na leitura
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
        
        # AJUSTES DE SANEAMENTO: Remove espaços invisíveis e normaliza o CNPJ
        df_enriquecido['RazaoSocial'] = df_enriquecido['RazaoSocial'].str.strip()
        df_enriquecido['CNPJ'] = df_enriquecido['CNPJ'].astype(str).str.strip()

        # 2. --- SALVAMENTO DO HISTÓRICO PARA OS GRÁFICOS ---
        # Salvamos os dados linha a linha ANTES da agregação para alimentar o Dashboard
        hist_path = os.path.join(self.data_dir, 'historico_final.csv')
        df_enriquecido.to_csv(hist_path, index=False, encoding='utf-8-sig')
        print(f"Arquivo de histórico (detalhado) gerado em: {hist_path}")

        # 3. --- LÓGICA DO REQUISITO 2.3 (AGREGAÇÃO COM MÚLTIPLAS ESTRATÉGIAS) ---
        # Agrupamos por CNPJ, RazaoSocial e UF conforme item 2.3 do PDF [cite: 80]
        # Calculamos Total, Média e Desvio Padrão simultaneamente [cite: 81, 83, 84]
        agg_df = df_enriquecido.groupby(['CNPJ', 'RazaoSocial', 'UF']).agg(
            Total_Despesas=('ValorDespesas', 'sum'),
            Media_Trimestral=('ValorDespesas', 'mean'),
            Desvio_Padrao=('ValorDespesas', 'std')
        ).reset_index()

        # Saneamento do Desvio Padrão: 
        # Se houver apenas 1 registro para uma operadora/UF, o pandas retorna NaN.
        # Preenchemos com 0 para manter a integridade numérica do relatório.
        agg_df['Desvio_Padrao'] = agg_df['Desvio_Padrao'].fillna(0)

        # 4. ORDENAÇÃO CONFORME REQUISITO 2.3 DO PDF 
        # Trade-off técnico: Ordenação em memória (Python/Pandas) escolhida pela facilidade 
        # de manipulação de volumes médios de dados e rapidez de implementação.
        agg_df = agg_df.sort_values(by='Total_Despesas', ascending=False)

        return agg_df

    def save_report(self, df_final):
        """Salva o resumo final em despesas_agregadas.csv conforme item 2.3[cite: 89]."""
        output_path = os.path.join(self.data_dir, 'despesas_agregadas.csv')
        
        # Uso de 'utf-8-sig' para garantir que o Excel e MySQL reconheçam os acentos [cite: 118]
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"Relatório de agregação salvo com sucesso (UTF-8-SIG) em: {output_path}")
        return output_path