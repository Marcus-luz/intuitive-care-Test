import pandas as pd
import os

class DataAggregator:
    """
    2.3: Responsável por agrupar os dados e calcular métricas estatísticas
    conforme exigido pelo teste (Total, Média e Desvio Padrão)[cite: 79, 82].
    """
    def __init__(self, data_dir):
        # Ajuste Sênior: Recebe o caminho absoluto injetado pelo main.py
        self.data_dir = os.path.abspath(data_dir)

    def aggregate_expenses(self, df_enriquecido):
        """
        2.3: Agrupa os dados por RazaoSocial e UF para gerar o relatório final.
        """
        print("Iniciando agregação estatística dos dados...")

        # Agrupamento e Cálculo de Múltiplas Estratégias (Item 2.3)
        # Calculamos Soma, Média e Desvio Padrão simultaneamente 
        agg_df = df_enriquecido.groupby(['RazaoSocial', 'UF']).agg(
            Total_Despesas=('ValorDespesas', 'sum'),
            Media_Trimestral=('ValorDespesas', 'mean'),
            Desvio_Padrao=('ValorDespesas', 'std')
        ).reset_index()

        # Saneamento do Desvio Padrão: 
        # Se houver apenas 1 registro para uma operadora/UF, o pandas retorna NaN.
        # Preenchemos com 0 para manter a integridade numérica do relatório.
        agg_df['Desvio_Padrao'] = agg_df['Desvio_Padrao'].fillna(0)

        # 2.3: Ordenação por valor total (maior para menor) conforme requisito 
        # Justificativa de Trade-off: Ordenação em memória para facilitar visualização analítica.
        agg_df = agg_df.sort_values(by='Total_Despesas', ascending=False)

        return agg_df

    def save_report(self, df_final):
        """Salva o resultado final em despesas_agregadas.csv[cite: 89]."""
        output_path = os.path.join(self.data_dir, 'despesas_agregadas.csv')
        
        # 3.3: Salvamento garantindo o encoding UTF-8 solicitado 
        df_final.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"Relatório de agregação salvo com sucesso em: {output_path}")
        return output_path