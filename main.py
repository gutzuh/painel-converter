#!/usr/bin/env python3
"""
Conversor HB -> Painel CCM
Script principal para conversão de listas de I/O para formato de diagrama de bornes

Autor: J.Cortiça Automação Industrial
Versão: 2.0 - Sistema Adaptável
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Adiciona diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.parser.hb_parser import HBParser, IOPoint
from src.transformer.transformers import (
    NomenclaturaTransformer,
    CartaoTransformer,
    CabeamentoTransformer,
    FusivelTransformer
)
from src.generator.excel_generator import (
    PainelExcelGenerator,
    ValidationReport
)


class PainelConverter:
    """Conversor principal HB -> Painel CCM - Versão Adaptável"""
    
    def __init__(self, config_path: str = None, reference_file: str = None):
        """
        Inicializa o conversor
        
        Args:
            config_path: Caminho para arquivo de configuração YAML
            reference_file: Arquivo de referência para aprendizado automático
        """
        self.config = self._load_config(config_path)
        self.reference_file = reference_file
        self.learned_patterns = None
        
        # Se modo aprendizado está ativo e há arquivo de referência
        if self.config.get('mode', {}).get('learning_mode') == 'auto_learn' and reference_file:
            print("🧠 Modo de aprendizado automático ativado")
            self.learned_patterns = self._learn_patterns(reference_file)
        
        # Inicializa transformadores
        self.nom_transformer = NomenclaturaTransformer(
            self.config.get('nomenclatura', {})
        )
        self.cartao_transformer = CartaoTransformer(
            self.config.get('cartao', {})
        )
        self.cabo_transformer = CabeamentoTransformer(
            self.config.get('cabeamento', {})
        )
        self.fusivel_transformer = FusivelTransformer(
            self.config.get('fusivel', {})
        )
        
        # Parser e gerador
        self.parser: Optional[HBParser] = None
        self.generator = PainelExcelGenerator(self.config.get('output', {}))
        
        # Relatório de validação
        self.report = ValidationReport()
    
    def _learn_patterns(self, reference_file: str) -> Optional[Dict]:
        """Aprende padrões do arquivo de referência"""
        try:
            from src.learning.pattern_learner import PatternLearner
            
            learner = PatternLearner()
            patterns = learner.learn_from_files(
                input_file=None,  # Será passado depois
                reference_path=reference_file
            )
            
            # Salvar padrões aprendidos
            learner.save_patterns('config/learned_patterns.yaml')
            
            print(f"✅ Padrões aprendidos e salvos em config/learned_patterns.yaml")
            return patterns
            
        except ImportError:
            print("⚠️  Módulo de aprendizado não disponível, usando padrões manuais")
            return None
        except Exception as e:
            print(f"⚠️  Erro ao aprender padrões: {e}")
            return None
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Carrega arquivo de configuração"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Tenta carregar configuração padrão
        default_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'config', 'patterns.yaml'
        )
        
        if os.path.exists(default_path):
            with open(default_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        return {}
    
    def convert(self, 
                input_file: str, 
                output_file: str = None,
                info_projeto: Dict = None) -> bool:
        """
        Executa a conversão completa
        
        Args:
            input_file: Caminho do arquivo HB de entrada
            output_file: Caminho do arquivo de saída (opcional)
            info_projeto: Informações do projeto (opcional)
        
        Returns:
            True se conversão bem sucedida
        """
        print("\n" + "=" * 60)
        print("CONVERSOR HB -> PAINEL CCM")
        print("=" * 60)
        
        # Valida arquivo de entrada
        if not os.path.exists(input_file):
            print(f"[ERRO] Arquivo nao encontrado: {input_file}")
            return False
        
        print(f"\n[INPUT] Arquivo de entrada: {input_file}")
        
        # Define arquivo de saída
        if not output_file:
            base_name = Path(input_file).stem
            output_file = f"Painel_CCM_Gerado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        print(f"📄 Arquivo de saída: {output_file}")
        
        # Etapa 1: Parsing
        print("\n[1/4] Carregando e parseando arquivo HB...")
        self.parser = HBParser(input_file, self.config)
        
        if not self.parser.load():
            return False
        
        sheets = self.parser.parse_all_sheets()
        print(f"      [OK] {len(sheets)} abas identificadas")
        
        for name, data in sheets.items():
            print(f"        • {name} ({data.tipo}): {len(data.points)} pontos")
        
        # Etapa 2: Transformação
        print("\n[2/4] Transformando dados...")
        acionamentos = self._transform_acionamentos()
        status = self._transform_status()
        
        # Expande acionamentos (gera linhas múltiplas para AT, PIS, etc)
        acionamentos = self._expand_acionamentos(acionamentos)
        
        print(f"      [OK] {len(acionamentos)} acionamentos processados")
        print(f"      [OK] {len(status)} status processados")
        
        # Etapa 3: Validação
        print("\n[3/4] Validando dados...")
        self._validate_data(acionamentos, status)
        
        if self.report.has_errors():
            print(self.report.get_summary())
            print("\n⚠️  Conversão concluída com erros. Verifique o relatório.")
        else:
            print("      [OK] Validação concluída sem erros")
        
        # Etapa 4: Geração
        print("\n[4/4] Gerando arquivo Excel...")
        
        # Prepara informações do projeto
        if not info_projeto:
            info_projeto = self._extract_project_info()
        
        info_projeto['painel'] = self.parser.painel_id
        
        success = self.generator.generate(
            acionamentos=acionamentos,
            status=status,
            info_projeto=info_projeto,
            output_path=output_file
        )
        
        # Salva relatório
        report_file = output_file.replace('.xlsx', '_relatorio.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Salva relatório de validação
            f.write(self.report.get_summary())
        
        print(f"📋 Relatório salvo em: {report_file}")
        
        print("\n" + "=" * 60)
        if success:
            print("[OK] CONVERSÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("[ERRO] CONVERSÃO FALHOU")
        print("=" * 60 + "\n")
        
        return success
    
    def _transform_acionamentos(self) -> List[Dict]:
        """Transforma pontos de acionamento (DO)"""
        results = []
        
        for point in self.parser.get_points_by_type('DO'):
            # Transforma nomenclatura
            nom, tipo = self.nom_transformer.transform(
                point.nomenclatura, 
                point.descricao
            )
            
            # Transforma cartão
            cartao = self.cartao_transformer.transform(point.cartao_raw)
            
            # Determina cabo
            cabo_pecas = self.parser.get_pecas_cabo(point.cv) if point.cv else ""
            cabeamento = self.cabo_transformer.get_cabo(
                point.cv, 
                tipo,
                cabo_pecas
            )
            
            # Determina fusível
            borne_info = self.parser.get_borne_info(point.borne)
            fusivel = self.fusivel_transformer.get_fusivel(point.cv, borne_info)
            
            results.append({
                'nomenclatura': nom,
                'tipo': tipo,
                'descricao': point.descricao,
                'cartao': cartao,
                'anilha_cartao': point.anilha_cartao,
                'anilha_rele': point.anilha_rele,
                'rele': point.rele,
                'cv': point.cv if point.cv else '',
                'borne': point.borne,
                'cabeamento': cabeamento,
                'fusivel': fusivel,
                '_row': point.row_index,
            })
        
        return results
    
    def _transform_status(self) -> List[Dict]:
        """Transforma pontos de status (DI)"""
        results = []
        
        for point in self.parser.get_points_by_type('DI'):
            # Transforma nomenclatura
            nom, tipo = self.nom_transformer.transform(
                point.nomenclatura, 
                point.descricao
            )
            
            # Transforma cartão
            cartao = self.cartao_transformer.transform(point.cartao_raw)
            
            # Determina fusível
            borne_info = self.parser.get_borne_info(point.borne)
            fusivel = self.fusivel_transformer.get_fusivel(None, borne_info)
            
            results.append({
                'nomenclatura': nom,
                'tipo': tipo if tipo else 'STATUS',
                'descricao': point.descricao,
                'cartao': cartao,
                'anilha_cartao': point.anilha_cartao,
                'borne': point.borne,
                'fusivel': fusivel,
                '_row': point.row_index,
            })
        
        return results
    
    def _expand_acionamentos(self, acionamentos: List[Dict]) -> List[Dict]:
        """
        Expande acionamentos gerando linhas múltiplas para equipamentos específicos
        - Atuadores (AT-*): Agrupa pares A/F e gera 4 linhas (K-AT-XA, K-AT-XF, Atuador X, Atuador X)
        - Pistões (PIS-*): Agrupa pares Abre/Fecha e gera 3 linhas (RXA, RXF, Registro X Abre/Fecha)
        - Motores Reserva (MT-RES-*): Duplica cada linha
        - Despeliculadoras (DESP-*): Gera 3 linhas por despeliculadora
        """
        import re
        
        # FILTRO: Remover APENAS cabeçalhos duplicados "NOMENCLATURA"
        # Mantém linhas vazias/sem nomenclatura pois podem ser importantes na estrutura
        acionamentos = [
            item for item in acionamentos 
            if item.get('nomenclatura') != 'NOMENCLATURA'  # Remove apenas cabeçalhos
        ]
        
        # Agrupa equipamentos por número
        atuadores_dict = {}  # {numero: [items]}
        pistoes_dict = {}    # {numero: [items]}
        motores_res_dict = {}  # {numero: [items]}
        desp_dict = {}  # {numero: [items]}
        if_pc_list = []  # Lista de inversores porta carga
        if_e_list = []  # Lista de inversores esteira
        el_dict = {}  # {numero: [items]} - Elevadores (EL-X) que geram SENS-EL-X
        sens_el_dict = {}  # {numero: [items]}
        act_res_dict = {}  # {numero: [items]} - Acionamento Reserva
        if_res_dict = {}  # {numero: [items]} - Inversor Reserva
        val_gas_list = []  # Válvula Gás
        aut_est_list = []  # Autorização Esteira
        ign_ca_dict = {}  # {numero: [items]} - Ignição Câmara
        ft_at_list = []  # Fotocelula Atuadores
        outros = []
        
        for item in acionamentos:
            nom = item.get('nomenclatura', '')
            desc = str(item.get('descricao', ''))
            
            # Atuadores (AT-1, AT-2, etc)
            if nom and nom.startswith('AT-'):
                if re.search(r'(ATUADOR|AT-)\s*\d+[AF]', desc.upper()):
                    match = re.search(r'AT-(\d+)', nom)
                    if match:
                        num = match.group(1)
                        if num not in atuadores_dict:
                            atuadores_dict[num] = []
                        atuadores_dict[num].append(item)
                        continue
            
            # Pistões (PIS-1, PIS-2, etc)
            elif nom and nom.startswith('PIS-'):
                match = re.search(r'PIS-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in pistoes_dict:
                        pistoes_dict[num] = []
                    pistoes_dict[num].append(item)
                    continue
            
            # Motores Reserva (MT-RES-1, MT-RES-2, etc)
            elif nom and nom.startswith('MT-RES-'):
                match = re.search(r'MT-RES-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in motores_res_dict:
                        motores_res_dict[num] = []
                    motores_res_dict[num].append(item)
                    continue
            
            # Despeliculadoras (DESP-1, DESP-2, etc)
            elif nom and nom.startswith('DESP-'):
                match = re.search(r'DESP-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in desp_dict:
                        desp_dict[num] = []
                    desp_dict[num].append(item)
                    continue
            
            # Inversores Porta Carga (IF-PC-1)
            elif nom and nom.startswith('IF-PC-'):
                if_pc_list.append(item)
                continue
            
            # Inversores Esteira (IF-E-1)
            elif nom and nom.startswith('IF-E-'):
                if_e_list.append(item)
                continue
            
            # Elevadores (EL-1, EL-2, etc) - Geram SENS-EL automaticamente
            # Não usa 'continue' para que EL-X também seja mantido
            if nom and nom.startswith('EL-') and not nom.startswith('EL-CA'):
                match = re.search(r'EL-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in el_dict:
                        el_dict[num] = []
                    el_dict[num].append(item)
                    # NÃO usa continue - deixa cair em 'outros' para manter EL-X também
            
            # Sensores Elevador (SENS-EL-1, etc)
            elif nom and nom.startswith('SENS-EL-'):
                match = re.search(r'SENS-EL-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in sens_el_dict:
                        sens_el_dict[num] = []
                    sens_el_dict[num].append(item)
                    continue
            
            # Acionamento Reserva (ACT-RES-1, ACT-RES-2)
            elif nom and nom.startswith('ACT-RES-'):
                match = re.search(r'ACT-RES-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in act_res_dict:
                        act_res_dict[num] = []
                    act_res_dict[num].append(item)
                    continue
            
            # Inversor Reserva (IF-RES-1)
            elif nom and nom.startswith('IF-RES-'):
                match = re.search(r'IF-RES-(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in if_res_dict:
                        if_res_dict[num] = []
                    if_res_dict[num].append(item)
                    continue
            
            # Válvula Gás (VAL-GAS-CA-1)
            elif nom and nom.startswith('VAL-GAS-'):
                val_gas_list.append(item)
                continue
            
            # Autorização Esteira (AUT-EST)
            elif nom and nom == 'AUT-EST':
                aut_est_list.append(item)
                continue
            
            # Ignição Câmara (IGN-CA-1 ou IGN-CA1)
            elif nom and (nom.startswith('IGN-CA-') or nom.startswith('IGN-CA')):
                # Aceita tanto IGN-CA-1 quanto IGN-CA1 (com ou sem hífen)
                match = re.search(r'IGN-CA-?(\d+)', nom)
                if match:
                    num = match.group(1)
                    if num not in ign_ca_dict:
                        ign_ca_dict[num] = []
                    ign_ca_dict[num].append(item)
                    continue
            
            # Fotocelula Atuadores (FT-AT)
            elif nom and nom == 'FT-AT':
                ft_at_list.append(item)
                continue
            
            # Inversores Esteira (IF-E-1)
            elif nom and nom.startswith('IF-E-'):
                if_e_list.append(item)
                continue
            
            # Outros acionamentos normais
            outros.append(item)
        
        # Monta resultado expandido
        expanded = []
        
        # Atuadores expandidos (4 linhas por atuador)
        # Aplica transformações aprendidas: ANILHA e BORNE customizados
        for num in sorted(atuadores_dict.keys(), key=lambda x: int(x)):
            items = atuadores_dict[num]
            if len(items) >= 2:
                num_int = int(num)
                base_item = items[0]
                
                # K-AT-XA: ANILHA=1A-AT-X.1, BORNE=x{19+X}A
                expanded.append({
                    **base_item, 
                    'descricao': f'K-AT-{num}A',
                    'anilha_cartao': f'1A-AT-{num}.1',
                    'anilha_rele': '',
                    'rele': '',
                    'borne': f'x{19+num_int}A'
                })
                
                # K-AT-XF: ANILHA=1A-AT-X.2, BORNE=x{19+X}B
                expanded.append({
                    **base_item, 
                    'descricao': f'K-AT-{num}F',
                    'anilha_cartao': f'1A-AT-{num}.2',
                    'anilha_rele': '',
                    'rele': '',
                    'borne': f'x{19+num_int}B'
                })
                
                # Atuador X (2 linhas): mantém ANILHA original do item[0] e item[1]
                for i, item in enumerate(items[:2]):
                    expanded.append({
                        **item,
                        'descricao': f'Atuador {num}'
                    })
            else:
                expanded.extend(items)
        
        # Pistões expandidos (3 linhas por pistão)
        for num in sorted(pistoes_dict.keys(), key=lambda x: int(x)):
            items = pistoes_dict[num]
            if len(items) >= 2:
                base_item = items[0]
                expanded.append({**base_item, 'descricao': f'R{num}A'})
                expanded.append({**base_item, 'descricao': f'R{num}F'})
                expanded.append({**base_item, 'descricao': f'Acionamento / Status Registro {num} Abre / Fecha'})
            else:
                expanded.extend(items)
        
        # Motores Reserva (2 linhas cada - DM e CONTATOR)
        for num in sorted(motores_res_dict.keys(), key=lambda x: int(x)):
            items = motores_res_dict[num]
            for item in items:
                expanded.append({**item, 'descricao': f'Motor Reserva {num} (DM)'})
                expanded.append({**item, 'descricao': f'Motor Reserva {num} (CONTATOR)'})
        
        # Despeliculadoras - PADRÃO DESCOBERTO AUTOMATICAMENTE
        # DESP-1: 3 base (Desp 1,2,3) + 9 bornes (3 bornes × 3 items) = 12 linhas
        # DESP-2: 2 base (Desp 4, Autorização) + 3 bornes (3 bornes × 1 item) = 5 linhas
        for num in sorted(desp_dict.keys(), key=lambda x: int(x)):
            items = desp_dict[num]
            if not items:
                continue
            
            base_item = items[0]
            
            if num == '1':
                # DESP-1: Despeliculadoras 1, 2, 3 + bornes
                for i in range(1, 4):
                    expanded.append({**base_item, 'nomenclatura': 'DESP-1', 'descricao': '', 
                                   'cartao': f'Despeliculadora {i}'})
                for i in range(1, 4):
                    expanded.append({**base_item, 'nomenclatura': 'DESP-1', 'descricao': '',
                                   'cartao': f'Despeliculadora {i} Borne Rele 8', 'anilha_cartao': '', 'anilha_rele': ''})
                    expanded.append({**base_item, 'nomenclatura': 'DESP-1', 'descricao': '',
                                   'cartao': f'Despeliculadora {i} Borne Rele 9', 'anilha_cartao': '', 'anilha_rele': ''})
                    expanded.append({**base_item, 'nomenclatura': 'DESP-1', 'descricao': '',
                                   'cartao': f'Despeliculadora {i} Borne  0V2', 'anilha_cartao': '', 'anilha_rele': ''})
            elif num == '2':
                # DESP-2: Despeliculadora 4 + Autorização + bornes
                expanded.append({**base_item, 'nomenclatura': 'DESP-2', 'descricao': '',
                               'cartao': 'Despeliculadora 4'})
                expanded.append({**base_item, 'nomenclatura': 'DESP-2', 'descricao': '',
                               'cartao': 'Autorização Despeliculadora'})
                expanded.append({**base_item, 'nomenclatura': 'DESP-2', 'descricao': '',
                               'cartao': 'Despeliculadora 4 Borne Rele 8', 'anilha_cartao': '', 'anilha_rele': ''})
                expanded.append({**base_item, 'nomenclatura': 'DESP-2', 'descricao': '',
                               'cartao': 'Despeliculadora 4 Borne Rele 9', 'anilha_cartao': '', 'anilha_rele': ''})
                expanded.append({**base_item, 'nomenclatura': 'DESP-2', 'descricao': '',
                               'cartao': 'Despeliculadora 4 Borne  0V2', 'anilha_cartao': '', 'anilha_rele': ''})
            # NOTA: Apenas DESP-1 e DESP-2 são válidos. Outros números (DESP-3, DESP-4, etc) são ignorados.
        
        # Inversores Porta Carga - PADRÃO DESCOBERTO: 5 linhas (Forno, Máximo, Mínimo, Positivo, Negativo)
        # IMPORTANTE: Apenas expande o PRIMEIRO item, ignorando duplicações vindas de descrições transformadas
        if if_pc_list:
            item = if_pc_list[0]  # Usa apenas o primeiro item real
            expanded.append({**item, 'descricao': '', 'cartao': 'Porta Carga (Forno)'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Porta Carga (Máximo)'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Porta Carga (Mínimo)'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Porta Carga(Positivo)'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Porta Carga(Negativo)'})
        
        # Inversores Esteira - PADRÃO DESCOBERTO: 3 linhas (Forno, Positivo, Negativo)
        # IMPORTANTE: Apenas expande o PRIMEIRO item, ignorando duplicações vindas de descrições transformadas
        if if_e_list:
            item = if_e_list[0]  # Usa apenas o primeiro item real
            expanded.append({**item, 'descricao': '', 'cartao': 'Esteira (Forno)'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Esteira (Positivo)'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Esteira(Negativo)'})
        
        # Elevadores (EL-X) -> Gerar SENS-EL-X automaticamente
        # 2 linhas cada: K-EL-X + Módulo de freio
        for num in sorted(el_dict.keys(), key=lambda x: int(x)):
            items = el_dict[num]
            if items:
                base_item = items[0]  # Usa apenas primeiro item
                expanded.append({**base_item, 'nomenclatura': f'SENS-EL-{num}', 'descricao': '',
                               'cartao': f'K-EL-{num}', 'anilha_cartao': '', 'anilha_rele': ''})
                expanded.append({**base_item, 'nomenclatura': f'SENS-EL-{num}', 'descricao': '',
                               'cartao': f'Módulo de freio do motor (EL-{num})', 'anilha_cartao': '', 'anilha_rele': ''})
        
        # Sensores Elevador - Caso já venham explícitos no HB (raro)
        for num in sorted(sens_el_dict.keys(), key=lambda x: int(x)):
            items = sens_el_dict[num]
            for item in items:
                expanded.append({**item, 'nomenclatura': f'SENS-EL-{num}', 'descricao': '',
                               'cartao': f'K-EL-{num}', 'anilha_cartao': '', 'anilha_rele': ''})
                expanded.append({**item, 'nomenclatura': f'SENS-EL-{num}', 'descricao': '',
                               'cartao': f'Módulo de freio do motor (EL-{num})', 'anilha_cartao': '', 'anilha_rele': ''})
        
        # Acionamento Reserva - PADRÃO DESCOBERTO
        # ACT-RES-1: 6 linhas (Acionamento Reserva 1-6)
        # ACT-RES-2: 2 linhas (Acionamento Reserva 7-8)
        for num in sorted(act_res_dict.keys(), key=lambda x: int(x)):
            items = act_res_dict[num]
            if not items:
                continue
            base_item = items[0]
            if num == '1':
                for i in range(1, 7):
                    expanded.append({**base_item, 'nomenclatura': 'ACT-RES-1', 'descricao': '',
                                   'cartao': f'Acionamento Reserva {i}'})
            elif num == '2':
                for i in range(7, 9):
                    expanded.append({**base_item, 'nomenclatura': 'ACT-RES-2', 'descricao': '',
                                   'cartao': f'Acionamento Reserva {i}'})
        
        # Inversor Reserva - PADRÃO DESCOBERTO: 3 linhas (base + POSITIVO + NEGATIVO)
        for num in sorted(if_res_dict.keys(), key=lambda x: int(x)):
            items = if_res_dict[num]
            for item in items:
                expanded.append({**item, 'descricao': '', 'cartao': f'Inversor Reserva {num}'})
                expanded.append({**item, 'descricao': '', 'cartao': f'Inversor Reserva {num} (POSITIVO)'})
                expanded.append({**item, 'descricao': '', 'cartao': f'Inversor Reserva {num} (NEGATIVO)'})
        
        # Válvula Gás - PADRÃO DESCOBERTO: 2 linhas (mesmo cartão duplicado)
        for item in val_gas_list:
            cartao_base = item.get('cartao', 'Servo Gás Câmara 1')
            expanded.append({**item, 'descricao': '', 'cartao': cartao_base})
            expanded.append({**item, 'descricao': '', 'cartao': cartao_base})
        
        # Autorização Esteira - PADRÃO DESCOBERTO: 3 linhas (Autorização + Borne Saída + Sirene)
        for item in aut_est_list:
            expanded.append({**item, 'descricao': '', 'cartao': 'Autorização Esteira'})
            expanded.append({**item, 'descricao': '', 'cartao': 'Autorização Esteira Borne Saida', 'anilha_cartao': '', 'anilha_rele': ''})
            expanded.append({**item, 'descricao': '', 'cartao': 'Autorização Sirene'})
        
        # Ignição Câmara - PADRÃO DESCOBERTO: 2 linhas (Ignição + Reset)
        # Usa apenas PRIMEIRO item para evitar duplicação
        for num in sorted(ign_ca_dict.keys(), key=lambda x: int(x)):
            items = ign_ca_dict[num]
            if items:
                item = items[0]  # PRIMEIRO item apenas
                expanded.append({**item, 'nomenclatura': f'IGN-CA-{num}', 'descricao': '', 'cartao': f'Ignição Camara {num}'})
                expanded.append({**item, 'nomenclatura': f'IGN-CA-{num}', 'descricao': '', 'cartao': f'Reset Ignição  Camara {num}'})
        
        # Fotocelula Atuadores - PADRÃO DESCOBERTO: 1 linha mantida
        for item in ft_at_list:
            expanded.append({**item, 'descricao': '', 'cartao': 'Acionamento Contator da Fonte'})
        
        # Adiciona outros acionamentos (mantém TUDO, inclusive linhas vazias)
        # Apenas remove nomenclaturas específicas que são duplicatas de expansões
        outros_limpos = [
            item for item in outros
            if item.get('nomenclatura') not in ['DESP', 'FDC-2']  # Remove apenas duplicatas conhecidas
        ]
        expanded.extend(outros_limpos)
        
        return expanded
    
    def _validate_data(self, acionamentos: List[Dict], status: List[Dict]):
        """Valida os dados processados"""
        # Valida acionamentos
        for item in acionamentos:
            row = item.get('_row', 0)
            
            # Descrição obrigatória
            if not item.get('descricao'):
                self.report.add_error("Descrição vazia", row)
            
            # Motor sem CV
            tipo = item.get('tipo', '').upper()
            if 'MOTOR' in tipo and not item.get('cv'):
                self.report.add_warning(
                    f"Motor '{item.get('nomenclatura')}' sem CV definido", 
                    row
                )
            
            # CV sem cabo
            if item.get('cv') and not item.get('cabeamento'):
                self.report.add_warning(
                    f"'{item.get('nomenclatura')}' com CV mas sem cabo definido",
                    row
                )
            
            # Cartão não identificado
            if not item.get('cartao'):
                self.report.add_warning(
                    f"'{item.get('nomenclatura')}' sem cartão identificado",
                    row
                )
        
        # Valida status
        for item in status:
            row = item.get('_row', 0)
            
            if not item.get('descricao'):
                self.report.add_error("Descrição vazia", row)
        
        # Informações gerais
        self.report.add_info(f"Total de acionamentos: {len(acionamentos)}")
        self.report.add_info(f"Total de status: {len(status)}")
        
        # Nomenclaturas únicas
        noms = set()
        for item in acionamentos + status:
            if item.get('nomenclatura'):
                noms.add(item['nomenclatura'])
        self.report.add_info(f"Nomenclaturas únicas: {len(noms)}")
    
    def _extract_project_info(self) -> Dict:
        """Extrai informações do projeto do arquivo"""
        info = {
            'local': 'Borborema - SP',  # Valor padrão baseado no cliente Zanchetta
            'cliente': '',
            'nome_projeto': '',
            'desenhado': 'Leonardo',  # Nome padrão do desenhista
            'conferido': 'André Luiz',  # Nome padrão do conferente
        }
        
        # Tenta extrair do nome do arquivo
        if self.parser and self.parser.filepath:
            filename = Path(self.parser.filepath).stem
            
            # Padrões comuns: "HB - Cliente - Projeto"
            parts = filename.split('-')
            if len(parts) >= 2:
                info['cliente'] = parts[1].strip()
            if len(parts) >= 3:
                info['nome_projeto'] = parts[2].strip()
        
        return info


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Conversor HB -> Painel CCM - Sistema Adaptável v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Conversão básica
  python main.py input.xlsx
  
  # Com arquivo de saída customizado
  python main.py input.xlsx -o output.xlsx
  
  # Com aprendizado automático de referência
  python main.py input.xlsx -r reference.xlsx
  
  # Com configuração customizada
  python main.py input.xlsx --config config/custom.yaml
  
  # Com informações do projeto
  python main.py input.xlsx --cliente "Nome Cliente" --projeto "Nome Projeto"
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Arquivo HB de entrada (.xlsx)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Arquivo de saída (.xlsx)',
        default=None
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Arquivo de configuração (.yaml)',
        default=None
    )
    
    parser.add_argument(
        '-r', '--reference',
        help='Arquivo de referência para aprendizado automático (.xlsx)',
        default=None
    )
    
    parser.add_argument(
        '--learn-only',
        help='Apenas aprende padrões sem converter (salva em config/learned_patterns.yaml)',
        action='store_true'
    )
    
    parser.add_argument(
        '--cliente',
        help='Nome do cliente',
        default=None
    )
    
    parser.add_argument(
        '--projeto',
        help='Nome do projeto',
        default=None
    )
    
    parser.add_argument(
        '--local',
        help='Local da instalação',
        default=None
    )
    
    args = parser.parse_args()
    
    # Modo somente aprendizado
    if args.learn_only:
        if not args.reference:
            print("❌ Erro: --learn-only requer --reference")
            return 1
        
        from src.learning.pattern_learner import PatternLearner
        learner = PatternLearner()
        patterns = learner.learn_from_files(args.input_file, args.reference)
        learner.save_patterns('config/learned_patterns.yaml')
        
        print("\n✅ Aprendizado completo!")
        print(f"   Padrões salvos em: config/learned_patterns.yaml")
        print(f"\n   Use: python main.py {args.input_file} -o output.xlsx")
        print(f"   Os padrões serão aplicados automaticamente")
        return 0
    
    # Prepara informações do projeto
    info_projeto = {}
    if args.cliente:
        info_projeto['cliente'] = args.cliente
    if args.projeto:
        info_projeto['nome_projeto'] = args.projeto
    if args.local:
        info_projeto['local'] = args.local
    
    # Executa conversão
    converter = PainelConverter(
        config_path=args.config,
        reference_file=args.reference
    )
if __name__ == '__main__':
    main()


