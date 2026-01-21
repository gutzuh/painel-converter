"""
Pattern Detector - Detecta fórmulas e padrões matemáticos automaticamente
"""

import re
from typing import List, Dict, Optional, Tuple
import pandas as pd


class FormulaDetector:
    """Detecta fórmulas matemáticas em transformações de dados"""
    
    @staticmethod
    def detect_numeric_formula(examples: List[Tuple[int, str]]) -> Optional[Dict]:
        """
        Detecta fórmula numérica a partir de exemplos
        
        Args:
            examples: Lista de tuplas (input_number, output_string)
            Ex: [(1, 'x20A'), (2, 'x21A'), (3, 'x22A')]
        
        Returns:
            Dict com fórmula detectada ou None
        """
        if len(examples) < 2:
            return None
        
        # Extrair números dos outputs
        output_nums = []
        suffixes = []
        
        for inp, out in examples:
            match = re.search(r'(\d+)([A-Z]?)', str(out))
            if match:
                output_nums.append((inp, int(match.group(1)), match.group(2)))
                if match.group(2):
                    suffixes.append(match.group(2))
        
        if len(output_nums) < 2:
            return None
        
        # Verificar padrão linear: output = a * input + b
        inp1, out1, _ = output_nums[0]
        inp2, out2, _ = output_nums[1]
        
        # Calcular coeficientes
        if inp2 != inp1:
            a = (out2 - out1) / (inp2 - inp1)
            b = out1 - a * inp1
            
            # Verificar se fórmula funciona para todos os exemplos
            valid = True
            for inp, out, _ in output_nums:
                expected = a * inp + b
                if abs(expected - out) > 0.01:
                    valid = False
                    break
            
            if valid:
                # Determinar formato da fórmula
                if a == 1 and b != 0:
                    formula = f'{{N}}+{int(b)}'
                elif a != 1 and b == 0:
                    formula = f'{int(a)}*{{N}}'
                elif a != 1 and b != 0:
                    formula = f'{int(a)}*{{N}}+{int(b)}'
                else:
                    formula = '{N}'
                
                return {
                    'type': 'linear',
                    'formula': formula,
                    'coefficient': a,
                    'constant': b,
                    'suffix_pattern': suffixes[0] if suffixes else None,
                    'confidence': 1.0
                }
        
        return None
    
    @staticmethod
    def detect_string_pattern(examples: List[Tuple[str, str]]) -> Optional[Dict]:
        """
        Detecta padrão de transformação de strings
        
        Args:
            examples: Lista de tuplas (input_string, output_string)
            Ex: [('K-AT-1A', 'AT-1'), ('K-AT-2F', 'AT-2')]
        
        Returns:
            Dict com padrão detectado
        """
        if len(examples) < 2:
            return None
        
        # Encontrar partes comuns e variáveis
        inp_parts = [inp for inp, _ in examples]
        out_parts = [out for _, out in examples]
        
        # Detectar formato de input
        inp_pattern = FormulaDetector._extract_pattern(inp_parts)
        out_pattern = FormulaDetector._extract_pattern(out_parts)
        
        if inp_pattern and out_pattern:
            return {
                'type': 'string_transform',
                'input_pattern': inp_pattern,
                'output_pattern': out_pattern,
                'examples': examples[:3]
            }
        
        return None
    
    @staticmethod
    def _extract_pattern(strings: List[str]) -> Optional[str]:
        """Extrai padrão comum de uma lista de strings"""
        if not strings:
            return None
        
        # Substituir números por {N}
        pattern = re.sub(r'\d+', '{N}', strings[0])
        
        # Substituir letras finais por {SUFFIX}
        pattern = re.sub(r'[A-Z]$', '{SUFFIX}', pattern)
        
        # Verificar se padrão funciona para todos
        for s in strings[1:]:
            test_pattern = re.sub(r'\d+', '{N}', s)
            test_pattern = re.sub(r'[A-Z]$', '{SUFFIX}', test_pattern)
            
            if test_pattern != pattern:
                return None
        
        return pattern
    
    @staticmethod
    def detect_expansion_pattern(hb_data: pd.DataFrame, ref_data: pd.DataFrame, 
                                 nomenclature: str) -> Optional[Dict]:
        """
        Detecta como uma nomenclatura do HB se expande na referência
        
        Returns:
            Dict com regra de expansão detectada
        """
        # Contar linhas no HB
        hb_lines = hb_data[hb_data['NOMENCLATURA'] == nomenclature]
        hb_count = len(hb_lines)
        
        # Procurar linhas correspondentes na referência
        # (pode ter nomenclatura modificada)
        ref_base = nomenclature.split('-')[-1]  # Ex: '1A' de 'K-AT-1A'
        ref_pattern = f'.*{ref_base}.*'
        
        ref_lines = ref_data[ref_data['NOMENCLATURA'].str.contains(ref_pattern, na=False, regex=True)]
        ref_count = len(ref_lines)
        
        if ref_count > hb_count:
            return {
                'nomenclature': nomenclature,
                'hb_lines': hb_count,
                'ref_lines': ref_count,
                'expansion_factor': ref_count / hb_count if hb_count > 0 else ref_count,
                'new_nomenclatures': list(ref_lines['NOMENCLATURA'].unique())
            }
        
        return None


class PatternApplier:
    """Aplica padrões aprendidos a novos dados"""
    
    def __init__(self, patterns: Dict):
        self.patterns = patterns
    
    def apply_anilha_transform(self, nomenclature: str, original_anilha: str) -> str:
        """Aplica transformação de ANILHA baseado em padrões"""
        # Verificar se há padrão aplicável
        for pattern in self.patterns.get('anilha_patterns', []):
            if self._matches_pattern(nomenclature, pattern['nomenclature_pattern']):
                # Aplicar transformação
                num = self._extract_number(nomenclature)
                suffix = self._extract_suffix(nomenclature)
                
                # Aplicar template
                return self._apply_template(pattern['anilha_template'], num, suffix)
        
        return original_anilha
    
    def apply_borne_formula(self, nomenclature: str) -> Optional[str]:
        """Calcula BORNE usando fórmula detectada"""
        for pattern in self.patterns.get('borne_patterns', []):
            num = self._extract_number(nomenclature)
            suffix = self._extract_suffix(nomenclature)
            
            if num is not None and 'formula' in pattern:
                # Aplicar fórmula
                base = pattern.get('base', 0)
                result_num = base + num
                
                return f'x{result_num}{suffix}'
        
        return None
    
    def should_expand(self, nomenclature: str) -> Tuple[bool, int]:
        """Verifica se nomenclatura deve ser expandida"""
        equip_type = self._detect_equipment_type(nomenclature)
        
        if equip_type in self.patterns.get('expansion_rules', {}):
            factor = self.patterns['expansion_rules'][equip_type]['expansion_factor']
            return True, factor
        
        return False, 1
    
    @staticmethod
    def _matches_pattern(text: str, pattern: str) -> bool:
        """Verifica se texto match com padrão"""
        regex = pattern.replace('{N}', r'\d+').replace('{SUFFIX}', r'[A-Z]?')
        return bool(re.match(regex, text))
    
    @staticmethod
    def _extract_number(text: str) -> Optional[int]:
        """Extrai número de uma string"""
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def _extract_suffix(text: str) -> str:
        """Extrai sufixo de letra final"""
        match = re.search(r'([A-Z])$', text)
        return match.group(1) if match else ''
    
    @staticmethod
    def _apply_template(template: str, num: int, suffix: str) -> str:
        """Aplica valores a um template"""
        result = template.replace('{N}', str(num))
        result = result.replace('{SUFFIX}', suffix)
        return result
    
    @staticmethod
    def _detect_equipment_type(nom: str) -> str:
        """Detecta tipo de equipamento"""
        match = re.match(r'([A-Z-]+)', nom)
        return match.group(1).rstrip('-') if match else 'UNKNOWN'


def main():
    """Testes do detector de fórmulas"""
    detector = FormulaDetector()
    
    # Teste 1: Detectar fórmula numérica (BORNE)
    print("🧪 Teste 1: Detectar fórmula BORNE")
    borne_examples = [(1, 'x20A'), (2, 'x21A'), (3, 'x22A'), (4, 'x23A')]
    formula = detector.detect_numeric_formula(borne_examples)
    print(f"   Fórmula detectada: {formula}")
    
    # Teste 2: Detectar padrão de string
    print("\n🧪 Teste 2: Detectar padrão de nomenclatura")
    nom_examples = [('K-AT-1A', 'AT-1'), ('K-AT-2F', 'AT-2'), ('K-AT-3A', 'AT-3')]
    pattern = detector.detect_string_pattern(nom_examples)
    print(f"   Padrão detectado: {pattern}")


if __name__ == '__main__':
    main()
