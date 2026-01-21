"""
Validador de Compatibilidade com Sistema C#
Garante que o Excel gerado está 100% compatível com ProjetosEletricosAutomacao
"""

import pandas as pd
from typing import Dict, List, Tuple
import re


class CSharpCompatibilityValidator:
    """
    Valida se o Excel gerado segue EXATAMENTE os padrões
    esperados pelo sistema C# ProjetosEletricosAutomacao
    """
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.errors = []
        self.warnings = []
        
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Executa todas as validações"""
        
        self.validate_anilha_format()
        self.validate_cartao_format()
        self.validate_numero_cartao_extraction()
        self.validate_secao_cartao_calculation()
        self.validate_numero_saida_cartao()
        self.validate_borne_format()
        self.validate_nomenclatura_patterns()
        self.validate_sheet_structure()
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def validate_anilha_format(self):
        """
        Valida formato de ANILHA-CARTAO
        
        Padrões C# esperados:
        - Formato: {PAINEL}-{TIPO}-{NUMERO}.{SAIDA}
        - Exemplo: 1A-CT-13.1
        - GetNumeroCartao() extrai '13'
        - GetSecaoCartao() calcula seção (1-5) baseado em saída
        
        IMPORTANTE: Conexões diretas (Borne Rele, 0V2, etc) não têm ANILHA-CARTAO e isso é esperado.
        """
        df = pd.read_excel(self.excel_path, sheet_name='Acionamento CCM-1A')
        
        # Padrões de CARTAO que indicam conexão direta (não têm ANILHA-CARTAO)
        direct_connection_patterns = [
            r'Borne\s+Rele',
            r'Borne\s+0V',
            r'Módulo\s+de\s+freio',
            r'K-EL-\d+',  # Contatores diretos de elevador
        ]
        
        for idx, row in df.iterrows():
            anilha = row.get('ANILHA-CARTAO', None)
            cartao = str(row.get('CARTAO', ''))
            
            # Se CARTAO é conexão direta, ANILHA vazia é esperada
            is_direct_connection = any(re.search(pattern, cartao, re.IGNORECASE) for pattern in direct_connection_patterns)
            
            if pd.isna(anilha):
                if not is_direct_connection:
                    self.warnings.append(
                        f"Linha {idx+2}: ANILHA-CARTAO vazia mas CARTAO '{cartao}' parece ser do CLP (não é conexão direta)"
                    )
                continue
            
            anilha = str(anilha)
            
            if anilha == '':
                continue
            
            # Validar formato básico: XX-YY-NN.S
            if not re.match(r'^\d[A-Z]-[A-Z]+-\d+\.\d+$', anilha):
                self.errors.append(
                    f"Linha {idx+2}: ANILHA '{anilha}' não segue padrão C# (esperado: 1A-CT-13.1)"
                )
            
            # Validar se pode extrair número do cartão
            parts = anilha.split('-')
            if len(parts) >= 3:
                last_part = parts[-1]
                if '.' not in last_part:
                    self.errors.append(
                        f"Linha {idx+2}: ANILHA '{anilha}' sem ponto (C# GetNumeroCartao() falhará)"
                    )
                else:
                    numero_cartao = last_part.split('.')[0]
                    if not numero_cartao.isdigit():
                        self.errors.append(
                            f"Linha {idx+2}: ANILHA '{anilha}' - número cartão '{numero_cartao}' não é numérico"
                        )
    
    def validate_cartao_format(self):
        """
        Valida formato de CARTAO
        
        Padrões C# esperados:
        - Formato com sufixo completo: 16-DO-P05, 20-DI-PF, 8-AO-U2, 8-AIO-U2
        - Normalização: PCNT vira \r\nPCNT
        - IsDigital(): !contains("AO" ou "AIO")
        - IsAnalogic(): contains("AO" ou "AIO")
        """
        df = pd.read_excel(self.excel_path, sheet_name='Acionamento CCM-1A')
        
        valid_patterns = [
            r'^\d+-DO-P\d+$',      # 16-DO-P05
            r'^\d+-DI-[A-Z]+$',    # 20-DI-PF, 20-DI-PCNT
            r'^\d+-AO-[A-Z0-9]+$', # 8-AO-U2
            r'^\d+-AIO-[A-Z0-9]+$' # 8-AIO-U2
        ]
        
        for idx, row in df.iterrows():
            cartao = str(row.get('CARTAO', ''))
            
            if pd.isna(cartao) or cartao == '':
                continue
            
            # Verificar se match algum padrão válido
            matches_pattern = any(re.match(pattern, cartao) for pattern in valid_patterns)
            
            if not matches_pattern:
                self.warnings.append(
                    f"Linha {idx+2}: CARTAO '{cartao}' pode não ser reconhecido pelo C# (padrões esperados: 16-DO-P05, 20-DI-PF, 8-AO-U2, 8-AIO-U2)"
                )
    
    def validate_numero_cartao_extraction(self):
        """
        Valida se GetNumeroCartao() conseguirá extrair corretamente
        
        Lógica C#:
        1. Split por '-'
        2. Pega última parte
        3. Se não tem '.', retorna vazio
        4. Split por '.'
        5. Pega primeira parte (antes do ponto)
        6. Se é número, retorna; senão, vazio
        
        IMPORTANTE: Conexões diretas não têm ANILHA-CARTAO, então são ignoradas.
        """
        df = pd.read_excel(self.excel_path, sheet_name='Acionamento CCM-1A')
        
        # Padrões de CARTAO que indicam conexão direta
        direct_connection_patterns = [
            r'Borne\s+Rele',
            r'Borne\s+0V',
            r'Módulo\s+de\s+freio',
            r'K-EL-\d+',
        ]
        
        for idx, row in df.iterrows():
            anilha = row.get('ANILHA-CARTAO', None)
            cartao = str(row.get('CARTAO', ''))
            
            # Ignorar conexões diretas
            is_direct_connection = any(re.search(pattern, cartao, re.IGNORECASE) for pattern in direct_connection_patterns)
            if is_direct_connection or pd.isna(anilha):
                continue
            
            anilha = str(anilha)
            if anilha == '':
                continue
            
            # Simular lógica C#
            parts = anilha.split('-')
            last_part = parts[-1]
            
            if '.' not in last_part:
                self.errors.append(
                    f"Linha {idx+2}: GetNumeroCartao() retornará vazio para '{anilha}' (falta ponto)"
                )
                continue
            
            numero_cartao = last_part.split('.')[0]
            if not numero_cartao.isdigit():
                self.errors.append(
                    f"Linha {idx+2}: GetNumeroCartao() retornará vazio para '{anilha}' ('{numero_cartao}' não é número)"
                )
    
    def validate_secao_cartao_calculation(self):
        """
        Valida cálculo de seção do cartão
        
        Lógica C# GetSecaoCartao():
        - Extrai número da saída (parte após o ponto)
        - 1-4: seção 1
        - 5-8: seção 2
        - 9-12: seção 3
        - 13-16: seção 4 (bug no C#: >= 12)
        - 17-20: seção 5
        """
        df = pd.read_excel(self.excel_path, sheet_name='Acionamento CCM-1A')
        
        for idx, row in df.iterrows():
            anilha = str(row.get('ANILHA-CARTAO', ''))
            
            if pd.isna(anilha) or anilha == '':
                continue
            
            # Extrair número da saída
            parts = anilha.split('-')
            last_part = parts[-1]
            
            if '.' not in last_part:
                continue
            
            numero_saida = last_part.split('.')[-1]
            
            if not numero_saida.isdigit():
                continue
            
            num = int(numero_saida)
            
            # Validar se está em range válido (1-20)
            if num < 1 or num > 20:
                self.warnings.append(
                    f"Linha {idx+2}: Número saída {num} em '{anilha}' fora do range (1-20) - GetSecaoCartao() retornará vazio"
                )
    
    def validate_numero_saida_cartao(self):
        """
        Valida GetNumeroSaidaCartao() - formatação baseada no tipo de cartão
        
        Lógica C#:
        - Digital (16-DO, 20-DI): formatação com zero à esquerda (01, 02, etc)
        - 8-AO: ímpar = N+, par = -  (ex: 1 = 1+, 2 = -)
        - 8-AIO: mapeamento complexo (1=1+, 2=1-, 3=2+, 4=2-, ... 13=1+, 14=-)
        """
        df = pd.read_excel(self.excel_path, sheet_name='Acionamento CCM-1A')
        
        for idx, row in df.iterrows():
            anilha = str(row.get('ANILHA-CARTAO', ''))
            cartao = str(row.get('CARTAO', ''))
            
            if pd.isna(anilha) or anilha == '' or pd.isna(cartao) or cartao == '':
                continue
            
            # Extrair número da saída
            parts = anilha.split('-')
            last_part = parts[-1]
            
            if '.' not in last_part:
                continue
            
            numero_saida = last_part.split('.')[-1]
            
            if not numero_saida.isdigit():
                continue
            
            num = int(numero_saida)
            
            # Validar por tipo de cartão
            if 'AIO' in cartao:
                # 8-AIO tem limites específicos
                if num < 1 or num > 20:
                    self.warnings.append(
                        f"Linha {idx+2}: Saída {num} inválida para cartão 8-AIO (válido: 1-20)"
                    )
            elif 'AO' in cartao and 'AIO' not in cartao:
                # 8-AO
                if num < 1:
                    self.warnings.append(
                        f"Linha {idx+2}: Saída {num} inválida para cartão AO"
                    )
    
    def validate_borne_format(self):
        """Valida formato de BORNE"""
        df = pd.read_excel(self.excel_path, sheet_name='Acionamento CCM-1A')
        
        for idx, row in df.iterrows():
            borne = str(row.get('BORNE', ''))
            
            if pd.isna(borne) or borne == '':
                continue
            
            # Padrão comum: xNN ou xNNA (ex: x20A, x21B)
            if not re.match(r'^x\d+[A-Z]?$', borne):
                self.warnings.append(
                    f"Linha {idx+2}: BORNE '{borne}' formato incomum (esperado: x20A, x21B, etc)"
                )
    
    def validate_nomenclatura_patterns(self):
        """
        Valida padrões de nomenclatura esperados pelo C#
        
        O C# tem métodos específicos para:
        - AT: Atuadores
        - SS-: Soft Starters
        - IF-: Inversores
        - EL-: Elevadores
        - FR-EL: Freio Elevador
        - CAR: Reversão
        - FDC: Fonte Atuador
        - COMANDO: Página de comando
        """
        df_desc = pd.read_excel(self.excel_path, sheet_name='Descrição de Projeto CCM-1A')
        
        recognized_patterns = [
            r'^AT-\d+$',        # Atuador
            r'^SS-',            # Soft Starter
            r'^IF-',            # Inversor
            r'^EL-\d+$',        # Elevador
            r'^FR-EL-\d+$',     # Freio Elevador
            r'CAR',             # Reversão (contains)
            r'^FDC-\d+$',       # Fonte Atuador
            r'COMANDO',         # Comando
            r'^K-AT-\d+[AF]$',  # Contator Atuador
        ]
        
        for idx, row in df_desc.iterrows():
            nom = str(row.get('NOMENCLATURA', ''))
            
            if pd.isna(nom) or nom == '':
                continue
            
            # Verificar se match algum padrão conhecido
            matches = any(
                re.match(pattern, nom) or pattern in nom
                for pattern in recognized_patterns
            )
            
            if not matches:
                self.warnings.append(
                    f"Descrição linha {idx+2}: NOMENCLATURA '{nom}' pode não ser reconhecida por métodos C# específicos (IsAtuadorPage, IsSoftStarterPage, etc)"
                )
    
    def validate_sheet_structure(self):
        """Valida estrutura das abas do Excel"""
        
        required_sheets = {
            'Descrição de Projeto CCM-1A': ['NOMENCLATURA', 'DESCRICAO'],
            'Acionamento CCM-1A': [
                'NOMENCLATURA', 'TIPO', 'DESCRICAO', 'CARTAO',
                'ANILHA-CARTAO', 'ANILHA-RELE', 'RELE', 'CAVALO',
                'BORNE', 'CABEAMENTO', 'FUSIVEL'
            ],
            'Reconhecimento CCM-1A': [
                'NOMENCLATURA', 'TIPO', 'DESCRICAO', 'CARTAO',
                'ANILHA-CARTAO', 'BORNE', 'FUSIVEL'
            ],
            'Informações Especiais CCM-1A': ['INFORMACAO', 'VALOR']
        }
        
        try:
            xl_file = pd.ExcelFile(self.excel_path)
            
            # Validar abas obrigatórias
            for sheet_name, required_cols in required_sheets.items():
                if sheet_name not in xl_file.sheet_names:
                    self.errors.append(
                        f"Aba obrigatória '{sheet_name}' não encontrada (C# ExcelRepository espera essa aba)"
                    )
                    continue
                
                df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                
                # Validar colunas obrigatórias
                for col in required_cols:
                    if col not in df.columns:
                        self.errors.append(
                            f"Aba '{sheet_name}': coluna '{col}' não encontrada (C# espera exatamente esse nome)"
                        )
        
        except Exception as e:
            self.errors.append(f"Erro ao validar estrutura: {str(e)}")
    
    def print_report(self):
        """Imprime relatório de validação"""
        print("\n" + "="*80)
        print("RELATÓRIO DE COMPATIBILIDADE C# - ProjetosEletricosAutomacao")
        print("="*80)
        
        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("\n✅ NENHUM PROBLEMA ENCONTRADO!")
            print("   Excel 100% compatível com sistema C#")
        else:
            if self.errors:
                print(f"\n❌ ERROS CRÍTICOS ({len(self.errors)}):")
                print("   Estes problemas QUEBRARÃO o sistema C#:\n")
                for error in self.errors:
                    print(f"   • {error}")
            
            if self.warnings:
                print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
                print("   Podem causar comportamento inesperado:\n")
                for warning in self.warnings:
                    print(f"   • {warning}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Teste do validador"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python validador_csharp.py <arquivo.xlsx>")
        sys.exit(1)
    
    validator = CSharpCompatibilityValidator(sys.argv[1])
    is_valid, errors, warnings = validator.validate_all()
    validator.print_report()
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
