"""
Transformador de Nomenclatura
Responsável por limpar, padronizar e mapear nomenclaturas
"""

import re
from typing import Dict, List, Optional, Tuple


class NomenclaturaTransformer:
    """Transformador de nomenclaturas para padrão do Painel CCM"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Prefixos a remover
        self.remove_prefixes = self.config.get('remove_prefixes', [
            "K-", "M-", "RL-", "CMD-", "ST-"
        ])
        
        # Mapeamentos específicos - mais completos
        self.specific_mappings = self.config.get('specific_mappings', {
            # Soft Starters
            "CIC-1": "SS-CIC-1",
            "VA-1-CA1": "SS-VA-1-CA1",
            "VA-2-CA1": "SS-VA-2-CA1",
            "VR-1-CR-1": "SS-VR-1-CR-1",
            "VR-2-CR-1": "SS-VR-2-CR-1",
            "VE-1-CA1": "SS-VE-1-CA1",
            "VE-2-CA1": "SS-VE-2-CA1",
            # Inversores
            "PC-1": "IF-PC-1",
            "E-1": "IF-E-1",
            "BC-1": "IF-BC-1",
            # Atuadores - manter original sem sufixo de direção
            "AT-1A": "AT-1",
            "AT-1F": "AT-1",
            "AT-2A": "AT-2",
            "AT-2F": "AT-2",
            "AT-3A": "AT-3",
            "AT-3F": "AT-3",
            "AT-4A": "AT-4",
            "AT-4F": "AT-4",
            "AT-5A": "AT-5",
            "AT-5F": "AT-5",
            "AT-6A": "AT-6",
            "AT-6F": "AT-6",
        })
        
        # Padrões para identificar tipo de equipamento
        self.equipment_patterns = {
            'motor': [
                r'^M-',
                r'MOTOR',
                r'VENTILADOR',
                r'BOMBA',
                r'ROSCA',
                r'EXAUSTOR',
                r'REDUTOR',
                r'TRANSPORTADOR'
            ],
            'atuador': [
                r'^AT-',
                r'ATUADOR',
                r'VALVULA',
                r'DAMPER'
            ],
            'soft_starter': [
                r'^SS-',
                r'SOFT\s*START'
            ],
            'inversor': [
                r'^IF-',
                r'INVERSOR',
                r'VFD',
                r'FREQUENCIA'
            ],
            'sensor': [
                r'^S-',
                r'SENSOR',
                r'TRANSMISSOR',
                r'INDICADOR'
            ]
        }
    
    def transform(self, nomenclatura: str, descricao: str = "") -> Tuple[str, str]:
        """
        Transforma nomenclatura e retorna (nomenclatura_limpa, tipo_equipamento)
        
        Args:
            nomenclatura: Nomenclatura original do arquivo HB
            descricao: Descrição do equipamento (usada para inferir nomenclatura se vazia)
        
        Returns:
            Tupla (nomenclatura_transformada, tipo_equipamento)
        """
        original_nom = nomenclatura
        
        if not nomenclatura or str(nomenclatura).strip() == '' or str(nomenclatura).lower() == 'nan':
            # Tenta extrair da descrição
            nomenclatura = self._extract_from_description(descricao)
        
        if not nomenclatura or str(nomenclatura).strip() == '':
            # Ainda vazio - retorna vazio mas com tipo se possível
            tipo = self._identify_equipment_type('', descricao)
            return ("", tipo)
        
        # Limpa a nomenclatura
        clean_nom = self._clean(nomenclatura)
        
        # Aplica mapeamentos específicos
        mapped_nom = self._apply_mappings(clean_nom)
        
        # Identifica tipo de equipamento
        tipo = self._identify_equipment_type(mapped_nom, descricao)
        
        return (mapped_nom, tipo)
    
    def _clean(self, nomenclatura: str) -> str:
        """Limpa e padroniza a nomenclatura"""
        text = str(nomenclatura).strip().upper()
        
        # Remove prefixos
        for prefix in self.remove_prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
        
        # Remove sufixos de direção para atuadores (A/F)
        if re.match(r'^AT-\d+[AF]$', text):
            text = text[:-1]
        
        # Remove sufixos numéricos redundantes após painel
        # Ex: "AT-1-1A" → "AT-1" se já temos o painel identificado
        text = re.sub(r'-\d+[A-Z]$', '', text)
        
        # Normaliza espaços
        text = re.sub(r'\s+', '-', text)
        
        return text
    
    def _apply_mappings(self, nomenclatura: str) -> str:
        """Aplica mapeamentos específicos de nomenclatura"""
        # Verifica mapeamento direto
        if nomenclatura in self.specific_mappings:
            return self.specific_mappings[nomenclatura]
        
        # Tenta match parcial
        for orig, mapped in self.specific_mappings.items():
            if nomenclatura.endswith(orig) or nomenclatura.startswith(orig):
                return mapped
        
        return nomenclatura
    
    def _identify_equipment_type(self, nomenclatura: str, descricao: str = "") -> str:
        """Identifica o tipo de equipamento baseado na nomenclatura e descrição"""
        combined = f"{nomenclatura} {descricao}".upper()
        
        for eq_type, patterns in self.equipment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    return eq_type.upper()
        
        return ""
    
    def _extract_from_description(self, descricao: str) -> str:
        """Extrai nomenclatura da descrição quando não está disponível"""
        if not descricao:
            return ""
        
        text = str(descricao).upper()
        
        # Mapeamentos específicos baseados em palavras-chave na descrição
        desc_mappings = {
            'VENTILADOR EXTRAÇÃO DE FUMAÇA': 'EF-CA1',
            'EXTRACAO DE FUMACA': 'EF-CA1',
            'VENTILADOR DO QUEIMADOR': 'VQ-CA1',
            'TRANSPORTE VIBRATORIO SAÍDA FORNO': 'TV-1',
            'TRANSPORTE VIBRATORIO SAIDA FORNO': 'TV-1',
            'TRANSPORTE VIBRATORIO SAÍDA DESPELICULADORAS': 'TV-2',
            'TRANSPORTE VIBRATORIO SAIDA DESPELICULADORAS': 'TV-2',
            'TRANSPORTE VIBRATORIO SAÍDA MESA': 'TV-3',
            'TRANSPORTE VIBRATORIO SAIDA MESA': 'TV-3',
            'ESCOVA ROTATIVA': 'ER-1',
            'ELEVADOR SAÍDA FORNO': 'EL-1',
            'ELEVADOR SAIDA FORNO': 'EL-1',
            'ELEVADOR CAIXA ELETRONICA': 'EL-2',
            'ELEVADOR DE CORRENTE DESCARTE': 'EL-3',
            'ELEVADOR ENSAQUE FINAL DE GRÃOS': 'EL-4',
            'ELEVADOR ENSAQUE FINAL DE GRAOS': 'EL-4',
            'ELEVADOR ENSAQUE FINAL BANDA': 'EL-5',
            'MOTOR RESERVA 1': 'MT-RES-1',
            'MOTO RESERVA 1': 'MT-RES-1',
            'MOTOR RESERVA 2': 'MT-RES-2',
            'MOTO RESERVA 2': 'MT-RES-2',
            'MOTOR RESERVA 3': 'MT-RES-3',
            'MOTO RESERVA 3': 'MT-RES-3',
            'MOTOR RESERVA 4': 'MT-RES-4',
            'MOTO RESERVA 4': 'MT-RES-4',
            'MOTOR RESERVA 5': 'MT-RES-5',
            'MOTO RESERVA 5': 'MT-RES-5',
            'SENSOR ROTONIVEL': 'SENS-ROT',
            'SENSOR PISTÃO': 'PIS',
            'SENSOR PISTAO': 'PIS',
            'PISTÃO': 'PIS',  # Adiciona mapeamento direto para pistão sem "SENSOR"
            'PISTAO': 'PIS',  # Versão sem acento
            'DESPELICULADORA': 'DESP',
            'SENSOR ELEVADOR': 'SENS-EL',
            'ELEVADOR LIGADO': 'SENS-EL',
            'AUTORIZAÇÃO ESTEIRA': 'AUT-EST',
            'AUTORIZACAO ESTEIRA': 'AUT-EST',
            'VALVULA GAS': 'VAL-GAS-CA-1',
            'FOTOCELULA ATUADORES': 'FT-AT',
            'ACIONAMENTO RESERVA': 'ACT-RES',
            'INVERSOR RESERVA': 'IF-RES',
            # REMOVIDO: 'PORTA CARGA': 'IF-PC-1' - PC-1 já é mapeado em specific_mappings
            # REMOVIDO: 'ESTEIRA': 'IF-E-1' - E-1 já é mapeado em specific_mappings
            'CICLONE': 'SS-CIC-1',
            'IGNIÇÃO': 'IGN-CA-1',
            'IGNICAO': 'IGN-CA-1',
        }
        
        # Primeiro tenta detectar padrões com números
        # Pistão X
        pistao_match = re.search(r'PIST[AÃ]O\s*(\d+)', text)
        if pistao_match:
            num = pistao_match.group(1)
            return f'PIS-{num}'
        
        # Despeliculadora X
        desp_match = re.search(r'DESPELICULADORA\s*(\d+)', text)
        if desp_match:
            num = desp_match.group(1)
            return f'DESP-{num}'
        
        # Motor Reserva X
        mt_res_match = re.search(r'MOTOR\s+RESERVA\s+(\d+)', text)
        if mt_res_match:
            num = mt_res_match.group(1)
            return f'MT-RES-{num}'
        
        # Sensor Elevador - mapeia por descrição específica
        if 'ELEVADOR' in text and ('SENSOR' in text or 'LIGADO' in text):
            if 'SAIDA FORNO' in text or 'SAÍDA FORNO' in text:
                return 'SENS-EL-1'
            elif 'CAIXA' in text:
                return 'SENS-EL-2'
            elif 'CORRENTE' in text or 'DESCARTE' in text:
                return 'SENS-EL-3'
            elif 'GRAO' in text or 'GRÃO' in text:
                return 'SENS-EL-4'
            elif 'BANDA' in text:
                return 'SENS-EL-5'
        
        # Acionamento Reserva X
        act_res_match = re.search(r'ACIONAMENTO\s+RESERVA\s+(\d+)', text)
        if act_res_match:
            num = act_res_match.group(1)
            return f'ACT-RES-{num}'
        
        # Inversor Reserva X
        if_res_match = re.search(r'INVERSOR\s+RESERVA\s+(\d+)', text)
        if if_res_match:
            num = if_res_match.group(1)
            return f'IF-RES-{num}'
        
        # Procura mapeamentos específicos
        for pattern, nom in desc_mappings.items():
            if pattern in text:
                # Para pistões, extrai o número da descrição
                if 'PIST' in pattern:
                    match = re.search(r'PIST[AÃ]O\s*(\d+)', text)
                    if match:
                        num = match.group(1)
                        return f'PIS-{num}'
                    # Se não achar número, retorna apenas PIS
                    return 'PIS'
                return nom
        
        # Padrões regex para encontrar nomenclatura na descrição
        patterns = [
            r'([A-Z]+-\d+-[A-Z]+\d*)',      # Ex: VA-1-CA1
            r'([A-Z]+-\d+-[A-Z]+-\d+)',      # Ex: VR-1-CR-1
            r'([A-Z]{2,3}-\d+)',              # Ex: AT-1, CIC-1
            r'([A-Z]-\d+)',                   # Ex: E-1
            r'K-([A-Z]+-\d+[A-Z]?)',          # Ex: K-AT-1A → AT-1A
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                result = match.group(1)
                # Remove K- se ainda presente
                if result.startswith('K-'):
                    result = result[2:]
                return result
        
        return ""
    
    def batch_transform(self, items: List[Dict]) -> List[Dict]:
        """
        Transforma uma lista de itens em lote
        
        Args:
            items: Lista de dicionários com 'nomenclatura' e 'descricao'
        
        Returns:
            Lista de dicionários com campos transformados
        """
        results = []
        
        for item in items:
            nom = item.get('nomenclatura', '')
            desc = item.get('descricao', '')
            
            transformed_nom, tipo = self.transform(nom, desc)
            
            result = item.copy()
            result['nomenclatura'] = transformed_nom
            result['tipo'] = tipo
            results.append(result)
        
        return results
    
    def get_grouped_nomenclaturas(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa itens por nomenclatura base (sem sufixos de direção)
        
        Útil para agrupar atuadores AT-1A e AT-1F sob AT-1
        """
        groups = {}
        
        for item in items:
            nom = item.get('nomenclatura', '')
            base_nom = self._get_base_nomenclatura(nom)
            
            if base_nom not in groups:
                groups[base_nom] = []
            groups[base_nom].append(item)
        
        return groups
    
    def _get_base_nomenclatura(self, nomenclatura: str) -> str:
        """Retorna nomenclatura base (sem sufixos de direção)"""
        if not nomenclatura:
            return ""
        
        # Remove sufixos de direção
        base = re.sub(r'[AF]$', '', nomenclatura)
        return base


class CartaoTransformer:
    """Transformador de códigos de cartão I/O"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Mapeamento atualizado com códigos completos
        self.cartao_mapping = self.config.get('mapping', {
            # DO - Saídas Digitais
            "16 DO": "16-DO-P05",
            "16DO": "16-DO-P05",
            "16-DO": "16-DO-P05",
            # DI - Entradas Digitais  
            "20 DI PF": "20-DI-PF",
            "20 DI PCNT": "20-DI-PCNT",
            "20DI PF": "20-DI-PF",
            "20DI": "20-DI-PF",
            "20 DI": "20-DI-PF",
            "20-DI": "20-DI-PF",
            # AI - Entradas Analógicas
            "4 AI PTNI": "4-AI-PTNI",
            "4 AI": "4-AI-PTNI",
            "4AI": "4-AI-PTNI",
            "4-AI": "4-AI-PTNI",
            # AO - Saídas Analógicas
            "8 AO U2": "8-AO-U2",
            "8 AO": "8-AO-U2",
            "8AO": "8-AO-U2",
            "8-AO": "8-AO-U2",
            "4 AO": "4-AO-U1",
            "4AO": "4-AO-U1",
        })
    
    def transform(self, cartao_raw: str) -> str:
        """Transforma código de cartão para formato padrão"""
        if not cartao_raw:
            return ""
        
        text = str(cartao_raw).strip().upper()
        
        # Tenta match direto
        if text in self.cartao_mapping:
            return self.cartao_mapping[text]
        
        # Tenta match parcial (ordem importa - do mais específico ao menos)
        for pattern in sorted(self.cartao_mapping.keys(), key=len, reverse=True):
            if pattern in text:
                return self.cartao_mapping[pattern]
        
        # Extrai padrão genérico e adiciona sufixo padrão
        match = re.search(r'(\d+)\s*(DO|DI|AI|AO)', text)
        if match:
            num, tipo = match.groups()
            # Adiciona sufixos padrão baseado no tipo
            sufixos = {
                'DO': 'P05',
                'DI': 'PF',
                'AI': 'PTNI',
                'AO': 'U2'
            }
            sufixo = sufixos.get(tipo, '')
            if sufixo:
                return f"{num}-{tipo}-{sufixo}"
            return f"{num}-{tipo}"
        
        return text


class CabeamentoTransformer:
    """Transformador para determinação de cabeamento"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Tabela padrão de CV → Cabo
        self.cabo_por_cv = self.config.get('por_cv', {
            0.5: "Cabo PP 4x1,5mm²",
            0.75: "Cabo PP 4x1,5mm²",
            1.0: "Cabo PP 4x1,5mm²",
            1.5: "Cabo PP 4x2,5mm²",
            2.0: "Cabo PP 4x2,5mm²",
            3.0: "Cabo PP 4x2,5mm²",
            4.0: "Cabo PP 4x2,5mm²",
            5.0: "Cabo PP 4x2,5mm²",
            5.5: "Cabo PP 4x2,5mm²",
            7.5: "Cabo PP 4x4mm²",
            10.0: "Cabo PP 4x4mm²",
            12.5: "Cabo PP 4x4mm²",
            15.0: "Cabo PP 4x6mm²",
            20.0: "Cabo PP 4x6mm²",
            25.0: "Cabo PP 4x10mm²",
            30.0: "Cabo PP 4x10mm²",
            40.0: "Cabo PP 4x16mm²",
            50.0: "Cabo PP 4x16mm²",
            60.0: "Cabo PP 4x25mm²",
            75.0: "Cabo PP 4x35mm²",
            100.0: "Cabo PP 4x50mm²",
        })
    
    def get_cabo(self, cv: Optional[float], tipo_equipamento: str = "", 
                 cabo_pecas: str = "") -> str:
        """
        Determina o cabo apropriado
        
        Args:
            cv: Potência em CV
            tipo_equipamento: Tipo do equipamento (INVERSOR, SOFT_STARTER, etc.)
            cabo_pecas: Cabo definido na tabela de peças (tem prioridade)
        
        Returns:
            String com especificação do cabo
        """
        # Prioridade 1: Tabela de peças
        if cabo_pecas:
            cabo = cabo_pecas
        elif cv is not None:
            # Prioridade 2: Tabela padrão por CV
            cabo = self._get_cabo_por_cv(cv)
        else:
            return ""
        
        # Aplica modificadores por tipo de equipamento
        cabo = self._apply_equipment_modifiers(cabo, tipo_equipamento)
        
        return cabo
    
    def _get_cabo_por_cv(self, cv: float) -> str:
        """Obtém cabo da tabela padrão baseado no CV"""
        # Converte chaves para float para comparação
        cv_values = sorted([float(k) for k in self.cabo_por_cv.keys()])
        
        # Encontra o menor CV que é >= ao CV solicitado
        for cv_ref in cv_values:
            if cv <= cv_ref:
                return self.cabo_por_cv.get(cv_ref, self.cabo_por_cv.get(int(cv_ref), ""))
        
        # Se CV maior que todos, retorna o maior
        if cv_values:
            max_cv = cv_values[-1]
            return self.cabo_por_cv.get(max_cv, self.cabo_por_cv.get(int(max_cv), ""))
        
        return "Verificar especificação"
    
    def _apply_equipment_modifiers(self, cabo: str, tipo: str) -> str:
        """Aplica modificadores baseado no tipo de equipamento"""
        tipo_upper = str(tipo).upper()
        
        # Inversores usam cabo blindado
        if 'INVERSOR' in tipo_upper or 'IF-' in tipo_upper:
            if 'Blindado' not in cabo:
                cabo = cabo.replace('Cabo PP', 'Cabo PP Blindado')
        
        return cabo


class FusivelTransformer:
    """Transformador para determinação de fusíveis"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Faixas de CV → Fusível
        self.fusivel_por_cv = self.config.get('por_cv', [
            {'cv_max': 2.0, 'fusivel': 'F1...F6'},
            {'cv_max': 5.5, 'fusivel': 'F7...F16'},
            {'cv_max': 12.5, 'fusivel': 'F17...F26'},
            {'cv_max': 25.0, 'fusivel': 'F27...F36'},
            {'cv_max': 50.0, 'fusivel': 'F37...F46'},
        ])
        
        self.default_fusivel = self.config.get('default', 'F7...F16')
    
    def get_fusivel(self, cv: Optional[float], borne_info: Dict = None) -> str:
        """
        Determina o fusível apropriado
        
        Args:
            cv: Potência em CV
            borne_info: Informações do borne (pode conter fusível definido)
        
        Returns:
            String com especificação do fusível
        """
        # Prioridade 1: Info do borne
        if borne_info and borne_info.get('fusivel'):
            return borne_info['fusivel']
        
        # Prioridade 2: Baseado no CV
        if cv is not None:
            for faixa in self.fusivel_por_cv:
                if cv <= faixa['cv_max']:
                    return faixa['fusivel']
        
        return self.default_fusivel
