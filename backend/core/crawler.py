import requests
from bs4 import BeautifulSoup
import os

def get_last_3_quarters(base_url):
    # 1. Acessa a raiz e busca as pastas de anos (YYYY) 
    # 2. Entra no ano mais recente e busca os trimestres (QQ) 
    # 3. Retorna os 3 links de diretórios mais recentes 
    pass 