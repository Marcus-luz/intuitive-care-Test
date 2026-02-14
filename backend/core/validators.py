import re

def is_valid_cnpj(cnpj: str) -> bool:
    """
    2.1: Valida formato e dígitos verificadores do CNPJ.
    Implementa o algoritmo de validação da Receita Federal.
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', str(cnpj))
    
    # Valida tamanho e evita sequências repetidas (ex: 11.111.111/1111-11)
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False
    
    def calculate_digit(digits, weights):
        s = sum(int(d) * w for d, w in zip(digits, weights))
        remainder = s % 11
        return str(r if (r := 11 - remainder) < 10 else 0)

    # Pesos oficiais para o cálculo dos dígitos
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    if calculate_digit(cnpj[:12], w1) != cnpj[12]:
        return False
    if calculate_digit(cnpj[:13], w2) != cnpj[13]:
        return False
        
    return True

def validate_row(row):
    """
    2.1: Executa o conjunto completo de validações exigidas:
    - Valores numéricos positivos [cite: 61]
    - Razão Social não vazia [cite: 63]
    - CNPJ válido (apenas se já houver sido enriquecido)
    """
    # 1. Validação de Valor Positivo [cite: 61]
    # Essencial para garantir a integridade de cálculos estatísticos futuros.
    try:
        if float(row['ValorDespesas']) <= 0:
            return False
    except (ValueError, TypeError):
        return False
        
    # 2. Validação de Razão Social [cite: 63]
    # Garante que a operadora esteja identificada nominalmente.
    razao = str(row.get('RazaoSocial', '')).strip()
    if not razao or razao == "PENDENTE_ENRIQUECIMENTO":
        return False
        
    # 3. Validação de CNPJ [cite: 60]
    # Trade-off: Rejeitamos o registro se o CNPJ for inválido para manter
    # a qualidade do banco de dados (Item 3).
    cnpj_str = str(row.get('CNPJ', ''))
    if len(cnpj_str) == 14: # Só valida se for um CNPJ completo (pós-enriquecimento)
        if not is_valid_cnpj(cnpj_str):
            return False
    else:
        # Se ainda for o placeholder de 6 dígitos (RegistroANS), permitimos
        # para não travar o pipeline antes do join.
        pass
        
    return True
