"""
Pattern Learner - Aprende padrões automaticamente de arquivos de referência
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import yaml


class PatternLearner:
    """Aprende padrões de transformação comparando HB original com Excel de referência"""
    
    def __init__(self):
        self.nomenclature_transforms = []
        self.anilha_patterns = []
        self.borne_patterns = []
        self.expansion_rules = {}
        self.field_mappings = {}
        
    def learn_from_files(self, hb_path: str, reference_path: str) -> Dict[str, Any]:
        """
        Analisa HB original e referência para extrair padrões automaticamente
        
        Returns:
            Dict com todos os padrões aprendidos
        """
        print("🧠 Iniciando aprendizado automático...")
        
        # Carregar arquivos
        hb_df = self._load_hb(hb_path)
        ref_acio = pd.read_excel(reference_path, sheet_name='Acionamento CCM-1A')
        ref_desc = pd.read_excel(reference_path, sheet_name='Descrição de Projeto CCM-1A')
        
        # Aprender diferentes tipos de padrões
        self._learn_nomenclature_transforms(hb_df, ref_acio)
        self._learn_anilha_patterns(hb_df, ref_acio)
        self._learn_borne_patterns(ref_acio)
        self._learn_expansion_rules(hb_df, ref_acio)
        self._learn_field_formulas(ref_acio)
        
        patterns = {
            'nomenclature_transforms': self.nomenclature_transforms,
            'anilha_patterns': self.anilha_patterns,
            'borne_patterns': self.borne_patterns,
            'expansion_rules': self.expansion_rules,
            'field_formulas': self.field_mappings
        }
        
        print(f"✅ Aprendizado completo: {len(self.nomenclature_transforms)} transformações detectadas")
        return patterns
    
    def _load_hb(self, hb_path: str) -> pd.DataFrame:
        """Carrega e normaliza arquivo HB"""
        df = pd.read_excel(hb_path, sheet_name='HB')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    
    def _learn_nomenclature_transforms(self, hb_df: pd.DataFrame, ref_df: pd.DataFrame):
        """Detecta transformações de nomenclatura (ex: K-AT-1A -> AT-1)"""
        print("  📝 Aprendendo transformações de nomenclatura...")
        
        hb_noms = set(hb_df['NOMENCLATURA'].dropna().astype(str))
        ref_noms = set(ref_df['NOMENCLATURA'].dropna().astype(str))
        
        # Detectar padrões de transformação
        for hb_nom in hb_noms:
            # Tentar encontrar correspondências parciais
            for ref_nom in ref_noms:
                if self._is_transformation(hb_nom, ref_nom):
                    pattern = self._extract_pattern(hb_nom, ref_nom)
                    if pattern and pattern not in self.nomenclature_transforms:
                        self.nomenclature_transforms.append(pattern)
    
    def _is_transformation(self, hb_nom: str, ref_nom: str) -> bool:
        """Verifica se duas nomenclaturas são transformações uma da outra"""
        # Ex: K-AT-1A e AT-1 compartilham números
        hb_nums = re.findall(r'\d+', hb_nom)
        ref_nums = re.findall(r'\d+', ref_nom)
        
        if not hb_nums or not ref_nums:
            return False
        
        # Se compartilham números, pode ser transformação
        return any(num in hb_nums for num in ref_nums)
    
    def _extract_pattern(self, hb_nom: str, ref_nom: str) -> Dict[str, str]:
        """Extrai padrão de transformação genérico"""
        # Substituir números por {N} para criar template
        hb_template = re.sub(r'\d+', '{N}', hb_nom)
        ref_template = re.sub(r'\d+', '{N}', ref_nom)
        
        # Extrair letras variáveis (A, F, etc)
        hb_letter = re.findall(r'[A-Z]$', hb_nom)
        ref_letter = re.findall(r'[A-Z]$', ref_nom)
        
        return {
            'hb_pattern': hb_template,
            'ref_pattern': ref_template,
            'hb_example': hb_nom,
            'ref_example': ref_nom,
            'has_suffix': bool(hb_letter)
        }
    
    def _learn_anilha_patterns(self, hb_df: pd.DataFrame, ref_df: pd.DataFrame):
        """Detecta padrões de transformação em ANILHA-CARTAO"""
        print("  🔢 Aprendendo padrões de ANILHA...")
        
        if 'ANILHA-CARTAO' not in ref_df.columns:
            return
        
        # Procurar padrões de transformação
        for _, ref_row in ref_df.head(50).iterrows():
            nom_ref = ref_row['NOMENCLATURA']
            anilha_ref = ref_row.get('ANILHA-CARTAO', '')
            
            if pd.isna(anilha_ref) or anilha_ref == '':
                continue
            
            # Extrair padrão numérico
            match = re.search(r'(\d+A)-([A-Z]+)-(\d+)\.(\d+)', str(anilha_ref))
            if match:
                pattern = {
                    'nomenclature_pattern': self._normalize_pattern(nom_ref),
                    'anilha_template': f'{match.group(1)}-{match.group(2)}-{{N}}.{{SUFFIX}}',
                    'example': str(anilha_ref)
                }
                if pattern not in self.anilha_patterns:
                    self.anilha_patterns.append(pattern)
    
    def _learn_borne_patterns(self, ref_df: pd.DataFrame):
        """Detecta padrões de BORNE (ex: x20A, x21B)"""
        print("  🔌 Aprendendo padrões de BORNE...")
        
        if 'BORNE' not in ref_df.columns:
            return
        
        bornes = ref_df['BORNE'].dropna().unique()
        
        # Detectar fórmula matemática (ex: x{19+N}A)
        borne_nums = []
        for borne in bornes:
            match = re.search(r'x(\d+)([A-Z])', str(borne))
            if match:
                borne_nums.append((int(match.group(1)), match.group(2)))
        
        if len(borne_nums) >= 2:
            # Verificar se há progressão aritmética
            nums = sorted([n[0] for n in borne_nums])
            if len(set([nums[i+1] - nums[i] for i in range(len(nums)-1)])) == 1:
                diff = nums[1] - nums[0]
                base = nums[0] - diff  # Estimar base da fórmula
                
                self.borne_patterns.append({
                    'formula': f'x{{{base}+N}}{{SUFFIX}}',
                    'base': base,
                    'increment': diff,
                    'examples': [str(b) for b in bornes[:5]]
                })
    
    def _learn_expansion_rules(self, hb_df: pd.DataFrame, ref_df: pd.DataFrame):
        """Detecta regras de expansão (1 linha HB -> N linhas REF)"""
        print("  📈 Aprendendo regras de expansão...")
        
        # Agrupar por nomenclatura base
        ref_counts = ref_df.groupby('NOMENCLATURA').size()
        
        # Identificar padrões de expansão
        for nom, count in ref_counts.items():
            if count > 1:
                # Detectar tipo de equipamento
                equip_type = self._detect_equipment_type(str(nom))
                
                if equip_type not in self.expansion_rules:
                    self.expansion_rules[equip_type] = {
                        'expansion_factor': count,
                        'examples': []
                    }
                
                self.expansion_rules[equip_type]['examples'].append({
                    'nomenclature': str(nom),
                    'lines': int(count)
                })
    
    def _learn_field_formulas(self, ref_df: pd.DataFrame):
        """Detecta fórmulas em campos (relações entre colunas)"""
        print("  🧮 Aprendendo fórmulas de campos...")
        
        # Analisar correlações entre campos
        for col in ['TIPO', 'DESCRICAO', 'CARTAO', 'ANILHA-RELE', 'RELE']:
            if col in ref_df.columns:
                # Detectar padrões de preenchimento
                non_empty = ref_df[ref_df[col].notna() & (ref_df[col] != '')]
                
                if len(non_empty) > 0:
                    self.field_mappings[col] = {
                        'fill_rate': len(non_empty) / len(ref_df),
                        'common_values': list(non_empty[col].value_counts().head(3).index)
                    }
    
    def _normalize_pattern(self, nom: str) -> str:
        """Normaliza nomenclatura para padrão genérico"""
        # Substituir números e letras variáveis
        pattern = re.sub(r'\d+', '{N}', str(nom))
        pattern = re.sub(r'[A-Z]$', '{SUFFIX}', pattern)
        return pattern
    
    def _detect_equipment_type(self, nom: str) -> str:
        """Detecta tipo de equipamento da nomenclatura"""
        # Extrair prefixo (AT, DESP, EL, etc)
        match = re.match(r'([A-Z-]+)', nom)
        if match:
            return match.group(1).rstrip('-')
        return 'UNKNOWN'
    
    def save_patterns(self, output_path: str):
        """Salva padrões aprendidos em arquivo YAML"""
        patterns = {
            'version': '1.0',
            'learned_patterns': {
                'nomenclature_transforms': self.nomenclature_transforms,
                'anilha_patterns': self.anilha_patterns,
                'borne_patterns': self.borne_patterns,
                'expansion_rules': self.expansion_rules,
                'field_formulas': self.field_mappings
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(patterns, f, allow_unicode=True, sort_keys=False)
        
        print(f"💾 Padrões salvos em: {output_path}")
    
    def apply_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Aplica padrões aprendidos a novos dados"""
        result = data.copy()
        
        # Aplicar transformações de nomenclatura
        for transform in self.nomenclature_transforms:
            # Implementar lógica de aplicação
            pass
        
        # Aplicar padrões de ANILHA
        # Aplicar padrões de BORNE
        # etc...
        
        return result


def main():
    """Teste do sistema de aprendizado"""
    learner = PatternLearner()
    
    patterns = learner.learn_from_files(
        'HB - Zanchetta - Blancheamento 10.02.2025.xlsx',
        'Painel - referncia.xlsx'
    )
    
    learner.save_patterns('config/learned_patterns.yaml')
    
    print("\n📊 Resumo do Aprendizado:")
    print(f"  • Transformações de nomenclatura: {len(patterns['nomenclature_transforms'])}")
    print(f"  • Padrões ANILHA: {len(patterns['anilha_patterns'])}")
    print(f"  • Padrões BORNE: {len(patterns['borne_patterns'])}")
    print(f"  • Regras de expansão: {len(patterns['expansion_rules'])}")
    print(f"  • Fórmulas de campos: {len(patterns['field_formulas'])}")


if __name__ == '__main__':
    main()
