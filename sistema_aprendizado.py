"""
Sistema Genérico de Aprendizado de Padrões Elétricos
Aplica padrões descobertos automaticamente a partir de arquivos de exemplo
"""

import json
import openpyxl
from typing import Dict, List, Any
from pathlib import Path

class SistemaAprendizado:
    """Sistema que aprende e aplica padrões automaticamente"""
    
    def __init__(self, arquivo_padroes='padroes_eletricos.json'):
        self.arquivo_padroes = arquivo_padroes
        self.padroes = self.carregar_padroes()
    
    def carregar_padroes(self) -> Dict:
        """Carrega padrões salvos ou retorna padrões padrão"""
        if Path(self.arquivo_padroes).exists():
            with open(self.arquivo_padroes, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.padroes_padrao()
    
    def padroes_padrao(self) -> Dict:
        """Padrões descobertos automaticamente do arquivo de referência"""
        return {
            "version": "1.0",
            "descricao": "Padrões elétricos aprendidos automaticamente",
            "padroes_expansao": {
                "DESP-1": {
                    "tipo": "borne_multiplicado",
                    "linhas_base": 3,
                    "linhas_total": 12,
                    "cartoes": [
                        {"template": "Despeliculadora {i}", "range": [1, 3]},
                        {"template": "Despeliculadora {i} Borne Rele 8", "range": [1, 3], "sem_anilha": True},
                        {"template": "Despeliculadora {i} Borne Rele 9", "range": [1, 3], "sem_anilha": True},
                        {"template": "Despeliculadora {i} Borne  0V2", "range": [1, 3], "sem_anilha": True}
                    ]
                },
                "DESP-2": {
                    "tipo": "borne_multiplicado",
                    "linhas_base": 2,
                    "linhas_total": 5,
                    "cartoes": [
                        "Despeliculadora 4",
                        "Autorização Despeliculadora",
                        {"template": "Despeliculadora 4 Borne Rele 8", "sem_anilha": True},
                        {"template": "Despeliculadora 4 Borne Rele 9", "sem_anilha": True},
                        {"template": "Despeliculadora 4 Borne  0V2", "sem_anilha": True}
                    ]
                },
                "ACT-RES-1": {
                    "tipo": "replicacao",
                    "linhas": 6,
                    "cartoes": [
                        {"template": "Acionamento Reserva {i}", "range": [1, 6]}
                    ]
                },
                "ACT-RES-2": {
                    "tipo": "replicacao",
                    "linhas": 2,
                    "cartoes": [
                        {"template": "Acionamento Reserva {i}", "range": [7, 8]}
                    ]
                },
                "SENS-EL": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 2,
                    "numeros": [1, 2, 3, 4, 5],
                    "cartoes": [
                        {"template": "K-EL-{num}", "sem_anilha": True},
                        {"template": "Módulo de freio do motor (EL-{num})", "sem_anilha": True}
                    ]
                },
                "IF-RES": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 3,
                    "cartoes": [
                        {"template": "Inversor Reserva {num}"},
                        {"template": "Inversor Reserva {num} (POSITIVO)"},
                        {"template": "Inversor Reserva {num} (NEGATIVO)"}
                    ]
                },
                "VAL-GAS-CA": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 2,
                    "cartoes": [
                        {"template": "Servo Gás Câmara {num}"},
                        {"template": "Servo Gás Câmara {num}"}
                    ]
                },
                "AUT-EST": {
                    "tipo": "fixo",
                    "linhas": 3,
                    "cartoes": [
                        "Autorização Esteira",
                        {"template": "Autorização Esteira Borne Saida", "sem_anilha": True},
                        "Autorização Sirene"
                    ]
                },
                "IGN-CA": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 2,
                    "cartoes": [
                        {"template": "Ignição Camara {num}"},
                        {"template": "Reset Ignição  Camara {num}"}
                    ]
                },
                "IF-PC": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 5,
                    "cartoes": [
                        "Porta Carga (Forno)",
                        "Porta Carga (Máximo)",
                        "Porta Carga (Mínimo)",
                        "Porta Carga (Positivo)",
                        "Porta Carga (Negativo)"
                    ]
                },
                "IF-E": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 3,
                    "cartoes": [
                        "Esteira (Forno)",
                        "Esteira (Positivo)",
                        "Esteira (Negativo)"
                    ]
                },
                "FT-AT": {
                    "tipo": "fixo",
                    "linhas": 1,
                    "cartoes": [
                        "Acionamento Contator da Fonte"
                    ]
                },
                "AT": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 4,
                    "descricoes": [
                        "K-AT-{num}A",
                        "K-AT-{num}F",
                        "Atuador {num}",
                        "Atuador {num}"
                    ]
                },
                "PIS": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 3,
                    "descricoes": [
                        "R{num}A",
                        "R{num}F",
                        "Acionamento / Status Registro {num} Abre / Fecha"
                    ]
                },
                "MT-RES": {
                    "tipo": "para_cada_numero",
                    "linhas_por_item": 2,
                    "descricoes": [
                        "Motor Reserva {num} (DM)",
                        "Motor Reserva {num} (CONTATOR)"
                    ]
                }
            },
            "mapeamentos_nomenclatura": {
                "ACIONAMENTO RESERVA": "ACT-RES",
                "INVERSOR RESERVA": "IF-RES",
                "SENSOR ELEVADOR": "SENS-EL",
                "ELEVADOR": "SENS-EL",
                "VALVULA GAS": "VAL-GAS-CA",
                "SERVO GAS": "VAL-GAS-CA",
                "FOTOCELULA": "FT-AT",
                "AUTORIZACAO ESTEIRA": "AUT-EST",
                "IGNICAO CAMARA": "IGN-CA"
            }
        }
    
    def salvar_padroes(self, padroes: Dict = None):
        """Salva padrões em arquivo JSON"""
        if padroes is None:
            padroes = self.padroes
        
        with open(self.arquivo_padroes, 'w', encoding='utf-8') as f:
            json.dump(padroes, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Padrões salvos em: {self.arquivo_padroes}")
    
    def aplicar_padrao(self, nomenclatura: str, item_base: Dict) -> List[Dict]:
        """Aplica padrão de expansão a um item"""
        # Extrair número se houver
        import re
        match = re.search(r'-(\d+)$', nomenclatura)
        numero = match.group(1) if match else None
        
        # Buscar padrão base (sem número)
        padrao_key = re.sub(r'-\d+$', '', nomenclatura)
        
        if padrao_key not in self.padroes.get('padroes_expansao', {}):
            return [item_base]  # Sem padrão, retorna original
        
        padrao = self.padroes['padroes_expansao'][padrao_key]
        tipo = padrao.get('tipo')
        resultado = []
        
        if tipo == 'fixo':
            # Gera linhas fixas
            for cartao_info in padrao['cartoes']:
                if isinstance(cartao_info, dict):
                    cartao = cartao_info['template']
                    sem_anilha = cartao_info.get('sem_anilha', False)
                else:
                    cartao = cartao_info
                    sem_anilha = False
                
                novo_item = {**item_base, 'nomenclatura': nomenclatura, 'descricao': '', 'cartao': cartao}
                if sem_anilha:
                    novo_item['anilha_cartao'] = ''
                    novo_item['anilha_rele'] = ''
                resultado.append(novo_item)
        
        elif tipo == 'replicacao':
            # Gera linhas com template
            for cartao_info in padrao['cartoes']:
                if isinstance(cartao_info, dict):
                    template = cartao_info['template']
                    range_vals = cartao_info.get('range', [1, 1])
                    for i in range(range_vals[0], range_vals[1] + 1):
                        cartao = template.replace('{i}', str(i))
                        resultado.append({**item_base, 'nomenclatura': nomenclatura, 'descricao': '', 'cartao': cartao})
                else:
                    resultado.append({**item_base, 'nomenclatura': nomenclatura, 'descricao': '', 'cartao': cartao_info})
        
        elif tipo == 'para_cada_numero' and numero:
            # Gera linhas para número específico
            for cartao_info in padrao.get('cartoes', []):
                if isinstance(cartao_info, dict):
                    cartao = cartao_info['template'].replace('{num}', numero)
                    sem_anilha = cartao_info.get('sem_anilha', False)
                else:
                    cartao = cartao_info.replace('{num}', numero)
                    sem_anilha = False
                
                novo_item = {**item_base, 'nomenclatura': nomenclatura, 'descricao': '', 'cartao': cartao}
                if sem_anilha:
                    novo_item['anilha_cartao'] = ''
                    novo_item['anilha_rele'] = ''
                resultado.append(novo_item)
            
            # Se tem descrições ao invés de cartões
            for desc_template in padrao.get('descricoes', []):
                descricao = desc_template.replace('{num}', numero)
                resultado.append({**item_base, 'nomenclatura': nomenclatura, 'descricao': descricao})
        
        elif tipo == 'borne_multiplicado':
            # Padrão complexo com bornes
            for cartao_info in padrao['cartoes']:
                if isinstance(cartao_info, dict):
                    template = cartao_info['template']
                    range_vals = cartao_info.get('range', [1, 1])
                    sem_anilha = cartao_info.get('sem_anilha', False)
                    
                    for i in range(range_vals[0], range_vals[1] + 1):
                        cartao = template.replace('{i}', str(i))
                        novo_item = {**item_base, 'nomenclatura': nomenclatura, 'descricao': '', 'cartao': cartao}
                        if sem_anilha:
                            novo_item['anilha_cartao'] = ''
                            novo_item['anilha_rele'] = ''
                        resultado.append(novo_item)
                else:
                    resultado.append({**item_base, 'nomenclatura': nomenclatura, 'descricao': '', 'cartao': cartao_info})
        
        return resultado if resultado else [item_base]
    
    def mapear_nomenclatura(self, descricao: str) -> str:
        """Mapeia descrição para nomenclatura baseado em padrões aprendidos"""
        desc_upper = descricao.upper()
        
        for palavra_chave, nomenclatura in self.padroes.get('mapeamentos_nomenclatura', {}).items():
            if palavra_chave in desc_upper:
                # Extrair número se houver
                import re
                match = re.search(r'(\d+)', descricao)
                if match:
                    return f"{nomenclatura}-{match.group(1)}"
                return nomenclatura
        
        return None


if __name__ == "__main__":
    # Criar e salvar padrões
    sistema = SistemaAprendizado()
    sistema.salvar_padroes()
    
    print("\n" + "=" * 80)
    print("SISTEMA GENÉRICO DE APRENDIZADO - PRONTO!")
    print("=" * 80)
    print(f"\nPadrões salvos em: {sistema.arquivo_padroes}")
    print(f"Total de padrões de expansão: {len(sistema.padroes['padroes_expansao'])}")
    print(f"Total de mapeamentos de nomenclatura: {len(sistema.padroes['mapeamentos_nomenclatura'])}")
    print("\nPara adicionar novos padrões:")
    print("1. Coloque um novo arquivo de exemplo na pasta")
    print("2. Execute: python analise_comparativa.py")
    print("3. Os novos padrões serão descobertos automaticamente")
    print("4. Edite padroes_eletricos.json para ajustar se necessário")
