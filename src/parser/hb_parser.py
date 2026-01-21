"""
Parser para arquivos HB (Lista de I/O)
Responsável por ler e extrair dados do arquivo Excel de origem
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import re


@dataclass
class IOPoint:
    """Representa um ponto de I/O extraído do arquivo HB"""
    nomenclatura: str = ""
    descricao: str = ""
    tipo: str = ""
    tipo_io: str = ""  # DO, DI, AI, AO
    cartao: str = ""
    cartao_raw: str = ""
    anilha_cartao: str = ""
    anilha_rele: str = ""
    rele: str = ""
    cv: Optional[float] = None
    borne: str = ""
    conector: str = ""
    pino: str = ""
    observacao: str = ""
    painel: str = ""
    row_index: int = 0


@dataclass
class SheetData:
    """Dados extraídos de uma aba do Excel"""
    name: str
    tipo: str  # acionamento, status, analogico, borne, pecas
    header_row: int
    data: pd.DataFrame
    points: List[IOPoint] = field(default_factory=list)


class HBParser:
    """Parser principal para arquivos HB"""
    
    # Palavras-chave para identificar tipo de aba
    SHEET_KEYWORDS = {
        'acionamento': ['acionamento', 'do ', 'saida', 'output'],
        'status': ['status', 'di ', 'entrada', 'input', 'reconhecimento'],
        'analogico': ['analogic', 'ai ', 'ao ', 'analog'],
        'borne': ['borne', 'terminal', 'reglet'],
        'pecas': ['peça', 'peca', 'material', 'bom', 'lista']
    }
    
    # Palavras-chave para identificar cabeçalho
    HEADER_KEYWORDS = [
        'nomenclatura', 'tag', 'descrição', 'descricao', 
        'cartão', 'cartao', 'conector', 'anilha', 'rele',
        'cv', 'potencia', 'borne'
    ]
    
    def __init__(self, filepath: str, config: Dict = None):
        self.filepath = filepath
        self.config = config or {}
        self.excel_file: Optional[pd.ExcelFile] = None
        self.sheets: Dict[str, SheetData] = {}
        self.pecas_lookup: Dict[float, str] = {}
        self.borne_lookup: Dict[str, Dict] = {}
        self.painel_id: str = ""
        
    def load(self) -> bool:
        """Carrega o arquivo Excel"""
        try:
            self.excel_file = pd.ExcelFile(self.filepath)
            self._detect_painel_id()
            return True
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return False
    
    def _detect_painel_id(self):
        """Detecta o ID do painel a partir do nome das abas"""
        for sheet_name in self.excel_file.sheet_names:
            # Procura padrões como "1A", "1B", "2A" no nome da aba
            match = re.search(r'(\d+[A-Z])', sheet_name.upper())
            if match:
                self.painel_id = match.group(1)
                break
        
        if not self.painel_id:
            self.painel_id = "1A"  # Default
    
    def parse_all_sheets(self) -> Dict[str, SheetData]:
        """Parseia todas as abas relevantes do arquivo"""
        if not self.excel_file:
            raise ValueError("Arquivo não carregado. Execute load() primeiro.")
        
        for sheet_name in self.excel_file.sheet_names:
            sheet_type = self._identify_sheet_type(sheet_name)
            
            if sheet_type:
                sheet_data = self._parse_sheet(sheet_name, sheet_type)
                if sheet_data:
                    self.sheets[sheet_name] = sheet_data
        
        # Processa tabela de peças primeiro (para lookup de cabos)
        self._build_pecas_lookup()
        
        # Processa tabela de bornes
        self._build_borne_lookup()
        
        # Processa pontos de I/O
        self._process_io_points()
        
        return self.sheets
    
    def _identify_sheet_type(self, sheet_name: str) -> Optional[str]:
        """Identifica o tipo de uma aba baseado no nome"""
        name_lower = sheet_name.lower()
        
        for sheet_type, keywords in self.SHEET_KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return sheet_type
        
        return None
    
    def _find_header_row(self, df: pd.DataFrame) -> int:
        """Encontra a linha onde está o cabeçalho real"""
        for idx in range(min(20, len(df))):
            row_values = [str(v).lower() for v in df.iloc[idx].values if pd.notna(v)]
            row_text = ' '.join(row_values)
            
            matches = sum(1 for kw in self.HEADER_KEYWORDS if kw in row_text)
            if matches >= 2:  # Pelo menos 2 keywords do cabeçalho
                return idx
        
        return 0  # Default: primeira linha
    
    def _parse_sheet(self, sheet_name: str, sheet_type: str) -> Optional[SheetData]:
        """Parseia uma aba específica"""
        try:
            # Lê sem cabeçalho primeiro
            df_raw = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
            
            # Encontra o cabeçalho
            header_row = self._find_header_row(df_raw)
            
            # Relê com cabeçalho correto
            df = pd.read_excel(
                self.excel_file, 
                sheet_name=sheet_name, 
                header=header_row
            )
            
            # Limpa nomes de colunas
            df.columns = [self._clean_column_name(c) for c in df.columns]
            
            # Remove linhas completamente vazias
            df = df.dropna(how='all')
            
            return SheetData(
                name=sheet_name,
                tipo=sheet_type,
                header_row=header_row,
                data=df
            )
            
        except Exception as e:
            print(f"Erro ao parsear aba '{sheet_name}': {e}")
            return None
    
    def _clean_column_name(self, col_name) -> str:
        """Limpa e padroniza nome de coluna"""
        if pd.isna(col_name):
            return "UNNAMED"
        
        name = str(col_name).upper().strip()
        name = re.sub(r'\s+', ' ', name)  # Múltiplos espaços → um espaço
        name = name.replace('Ç', 'C').replace('Ã', 'A').replace('Õ', 'O')
        
        return name
    
    def _build_pecas_lookup(self):
        """Constrói dicionário de lookup CV → Cabo"""
        for sheet_name, sheet_data in self.sheets.items():
            if sheet_data.tipo != 'pecas':
                continue
            
            df = sheet_data.data
            
            # Procura colunas de CV e Cabo
            cv_col = self._find_column(df, ['cv', 'potencia', 'cavalo'])
            cabo_col = self._find_column(df, ['cabo', 'cabeamento', 'fio'])
            
            if cv_col and cabo_col:
                for _, row in df.iterrows():
                    cv_val = row.get(cv_col)
                    cabo_val = row.get(cabo_col)
                    
                    if pd.notna(cv_val) and pd.notna(cabo_val):
                        try:
                            cv = float(cv_val)
                            self.pecas_lookup[cv] = str(cabo_val).strip()
                        except:
                            continue
    
    def _build_borne_lookup(self):
        """Constrói dicionário de lookup para bornes"""
        for sheet_name, sheet_data in self.sheets.items():
            if sheet_data.tipo != 'borne':
                continue
            
            df = sheet_data.data
            
            # Procura colunas relevantes
            borne_col = self._find_column(df, ['borne', 'terminal'])
            desc_col = self._find_column(df, ['descricao', 'descrição', 'funcao'])
            fuse_col = self._find_column(df, ['fusivel', 'fuse', 'protecao'])
            
            if borne_col:
                for _, row in df.iterrows():
                    borne_val = row.get(borne_col)
                    
                    if pd.notna(borne_val):
                        borne_key = str(borne_val).strip()
                        self.borne_lookup[borne_key] = {
                            'descricao': str(row.get(desc_col, '')).strip() if desc_col else '',
                            'fusivel': str(row.get(fuse_col, '')).strip() if fuse_col else ''
                        }
    
    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Encontra uma coluna que contém alguma das keywords"""
        for col in df.columns:
            col_lower = str(col).lower()
            for kw in keywords:
                if kw in col_lower:
                    return col
        return None
    
    def _process_io_points(self):
        """Processa todas as abas e extrai pontos de I/O"""
        for sheet_name, sheet_data in self.sheets.items():
            if sheet_data.tipo in ['acionamento', 'status', 'analogico']:
                points = self._extract_io_points(sheet_data)
                sheet_data.points = points
    
    def _extract_io_points(self, sheet_data: SheetData) -> List[IOPoint]:
        """Extrai pontos de I/O de uma aba"""
        points = []
        df = sheet_data.data
        
        # Mapeia colunas disponíveis
        col_map = {
            'nomenclatura': self._find_column(df, ['nomenclatura', 'tag', 'nome']),
            'descricao': self._find_column(df, ['descricao', 'descrição']),
            'cartao': self._find_column(df, ['cartao', 'cartão', 'modulo']),
            'anilha1': self._find_column(df, ['anilha 1', 'anilha1', 'anilha']),
            'anilha2': self._find_column(df, ['anilha 2', 'anilha2']),
            'rele': self._find_column(df, ['rele', 'relé', 'relay']),
            'cv': self._find_column(df, ['cv', 'potencia', 'cavalo']),
            'borne': self._find_column(df, ['borne', 'terminal']),
            'conector': self._find_column(df, ['conector', 'connector']),
            'pino': self._find_column(df, ['pino', 'pin'])
        }
        
        # Determina tipo de I/O baseado no tipo da aba
        tipo_io_map = {
            'acionamento': 'DO',
            'status': 'DI',
            'analogico': 'AI/AO'
        }
        
        for idx, row in df.iterrows():
            # Verifica se linha tem dados relevantes
            descricao = self._get_value(row, col_map['descricao'])
            cartao = self._get_value(row, col_map['cartao'])
            anilha1 = self._get_value(row, col_map['anilha1'])
            
            # Linha válida se tiver descrição OU (cartão E anilha)
            if not descricao and not (cartao and anilha1):
                continue
            
            point = IOPoint(
                nomenclatura=self._get_value(row, col_map['nomenclatura']),
                descricao=descricao,
                tipo_io=tipo_io_map.get(sheet_data.tipo, ''),
                cartao_raw=self._get_value(row, col_map['cartao']),
                anilha_cartao=self._get_value(row, col_map['anilha1']),
                anilha_rele=self._get_value(row, col_map['anilha2']),
                rele=self._get_value(row, col_map['rele']),
                cv=self._get_float_value(row, col_map['cv']),
                borne=self._get_value(row, col_map['borne']),
                conector=self._get_value(row, col_map['conector']),
                pino=self._get_value(row, col_map['pino']),
                painel=self.painel_id,
                row_index=idx
            )
            
            points.append(point)
        
        return points
    
    def _get_value(self, row: pd.Series, col_name: Optional[str]) -> str:
        """Obtém valor de uma coluna de forma segura"""
        if not col_name or col_name not in row:
            return ""
        
        val = row.get(col_name)
        if pd.isna(val):
            return ""
        
        return str(val).strip()
    
    def _get_float_value(self, row: pd.Series, col_name: Optional[str]) -> Optional[float]:
        """Obtém valor float de uma coluna de forma segura"""
        if not col_name or col_name not in row:
            return None
        
        val = row.get(col_name)
        if pd.isna(val):
            return None
        
        try:
            return float(val)
        except:
            return None
    
    def get_all_points(self) -> List[IOPoint]:
        """Retorna todos os pontos de I/O de todas as abas"""
        all_points = []
        for sheet_data in self.sheets.values():
            all_points.extend(sheet_data.points)
        return all_points
    
    def get_points_by_type(self, tipo_io: str) -> List[IOPoint]:
        """Retorna pontos de I/O filtrados por tipo"""
        return [p for p in self.get_all_points() if p.tipo_io == tipo_io]
    
    def get_pecas_cabo(self, cv: float) -> str:
        """Retorna o cabo da tabela de peças para um dado CV"""
        if cv in self.pecas_lookup:
            return self.pecas_lookup[cv]
        
        # Procura valor mais próximo
        if self.pecas_lookup:
            closest_cv = min(self.pecas_lookup.keys(), key=lambda x: abs(x - cv))
            if abs(closest_cv - cv) < 1.0:  # Tolerância de 1 CV
                return self.pecas_lookup[closest_cv]
        
        return ""
    
    def get_borne_info(self, borne: str) -> Dict:
        """Retorna informações de um borne"""
        return self.borne_lookup.get(borne, {})
