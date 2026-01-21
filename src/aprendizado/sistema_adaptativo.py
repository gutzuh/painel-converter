"""
Sistema de Aprendizado Adaptativo
Aprende padrões de expansão mantendo fidelidade aos dados originais
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd


class SistemaAprendizadoAdaptativo:
    """
    Sistema que equilibra aprendizado automático com fidelidade aos dados.
    
    Princípios:
    1. Conservadorismo: Só expande quando há certeza
    2. Fidelidade: Mantém estrutura original do HB
    3. Adaptabilidade: Aprende novos padrões de referências
    4. Transparência: Registra todas as decisões tomadas
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'aprendizado_config.yaml'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.log_decisoes = []
        
    def _load_config(self) -> Dict:
        """Carrega configuração de aprendizado"""
        if not self.config_path.exists():
            return self._get_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """Configuração padrão conservadora"""
        return {
            'aprendizado': {
                'modo': 'conservador',
                'auto_aprender': True,
                'confianca_minima': {'conservador': 1.0}
            },
            'qualidade': {
                'remover_cabecalhos_duplicados': True,
                'manter_linhas_vazias': True
            }
        }
    
    def deve_expandir(self, nomenclatura: str, tipo_expansao: str) -> Tuple[bool, float, str]:
        """
        Decide se deve aplicar expansão baseado em confiança
        
        Returns:
            (deve_expandir, confianca, motivo)
        """
        expansoes = self.config.get('expansoes', {})
        
        # Busca configuração da expansão
        expansao_config = expansoes.get(tipo_expansao, {})
        
        # Se não está habilitado, não expande
        if not expansao_config.get('enabled', False):
            return False, 0.0, f"Expansão '{tipo_expansao}' desabilitada"
        
        # Verifica confiança
        confianca = expansao_config.get('confianca', 0.0)
        modo = self.config['aprendizado']['modo']
        confianca_minima = self.config['aprendizado']['confianca_minima'].get(modo, 1.0)
        
        if confianca >= confianca_minima:
            motivo = f"Confiança {confianca:.1%} >= {confianca_minima:.1%} (modo: {modo})"
            self._log_decisao('expandir', nomenclatura, tipo_expansao, motivo)
            return True, confianca, motivo
        else:
            motivo = f"Confiança {confianca:.1%} < {confianca_minima:.1%}"
            self._log_decisao('manter_original', nomenclatura, tipo_expansao, motivo)
            return False, confianca, motivo
    
    def _log_decisao(self, acao: str, nomenclatura: str, tipo: str, motivo: str):
        """Registra decisão tomada"""
        self.log_decisoes.append({
            'acao': acao,
            'nomenclatura': nomenclatura,
            'tipo': tipo,
            'motivo': motivo
        })
    
    def detectar_padroes_novos(self, hb_data: List[Dict], referencia_data: List[Dict] = None):
        """
        Detecta padrões novos comparando HB com referência
        Atualiza config apenas se modo auto_aprender está ativo
        """
        if not self.config['aprendizado'].get('auto_aprender', False):
            return
        
        if referencia_data is None:
            return
        
        # Analisa diferenças e sugere novos padrões
        padroes_detectados = self._analisar_diferencas(hb_data, referencia_data)
        
        # Salva padrões com confiança calculada
        if self.config['aprendizado'].get('salvar_padroes', False):
            self._salvar_padroes_detectados(padroes_detectados)
    
    def _analisar_diferencas(self, hb_data: List[Dict], ref_data: List[Dict]) -> Dict:
        """Analisa diferenças entre HB e referência para detectar padrões"""
        # Converte para DataFrames
        df_hb = pd.DataFrame(hb_data)
        df_ref = pd.DataFrame(ref_data)
        
        # Conta nomenclaturas
        hb_counts = df_hb['nomenclatura'].value_counts() if 'nomenclatura' in df_hb.columns else {}
        ref_counts = df_ref['nomenclatura'].value_counts() if 'nomenclatura' in df_ref.columns else {}
        
        padroes = {}
        
        # Detecta nomenclaturas que existem na referência mas não no HB
        for nom in ref_counts.index:
            if nom not in hb_counts.index:
                padroes[nom] = {
                    'existe_em_hb': False,
                    'linhas_ref': int(ref_counts[nom]),
                    'confianca': 0.0,  # Sem dados no HB = confiança zero
                    'recomendacao': 'nao_aplicar_sem_dados'
                }
            elif ref_counts[nom] != hb_counts[nom]:
                # Existe em ambos mas com contagens diferentes = padrão de expansão
                fator = ref_counts[nom] / hb_counts[nom]
                padroes[nom] = {
                    'existe_em_hb': True,
                    'linhas_hb': int(hb_counts[nom]),
                    'linhas_ref': int(ref_counts[nom]),
                    'fator_expansao': fator,
                    'confianca': 1.0 if fator == int(fator) else 0.8,  # Confiança alta se fator é inteiro
                    'recomendacao': 'aplicar_expansao'
                }
        
        return padroes
    
    def _salvar_padroes_detectados(self, padroes: Dict):
        """Salva padrões detectados no arquivo de log"""
        log_path = self.config_path.parent / 'padroes_aprendidos.yaml'
        
        with open(log_path, 'w', encoding='utf-8') as f:
            yaml.dump({
                'timestamp': pd.Timestamp.now().isoformat(),
                'padroes_detectados': padroes,
                'total': len(padroes)
            }, f, allow_unicode=True, default_flow_style=False)
    
    def get_relatorio_decisoes(self) -> str:
        """Gera relatório das decisões tomadas"""
        if not self.log_decisoes:
            return "Nenhuma decisão registrada"
        
        expandidas = [d for d in self.log_decisoes if d['acao'] == 'expandir']
        mantidas = [d for d in self.log_decisoes if d['acao'] == 'manter_original']
        
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE DECISÕES DO SISTEMA DE APRENDIZADO")
        report.append("=" * 80)
        report.append(f"\nModo: {self.config['aprendizado']['modo']}")
        report.append(f"Total de decisões: {len(self.log_decisoes)}")
        report.append(f"  • Expansões aplicadas: {len(expandidas)}")
        report.append(f"  • Mantidas originais: {len(mantidas)}")
        
        if expandidas:
            report.append("\n[EXPANSÕES APLICADAS]")
            for d in expandidas[:10]:  # Mostra primeiras 10
                report.append(f"  • {d['nomenclatura']} ({d['tipo']}): {d['motivo']}")
        
        if mantidas:
            report.append("\n[MANTIDAS ORIGINAIS]")
            for d in mantidas[:5]:  # Mostra primeiras 5
                report.append(f"  • {d['nomenclatura']} ({d['tipo']}): {d['motivo']}")
        
        return "\n".join(report)
    
    def modo_conservador(self):
        """Ativa modo conservador (máxima fidelidade)"""
        self.config['aprendizado']['modo'] = 'conservador'
    
    def modo_balanceado(self):
        """Ativa modo balanceado (equilibra aprendizado e fidelidade)"""
        self.config['aprendizado']['modo'] = 'balanceado'
    
    def modo_agressivo(self):
        """Ativa modo agressivo (máximo aprendizado)"""
        self.config['aprendizado']['modo'] = 'agressivo'


# Singleton global
_sistema = None


def get_sistema_aprendizado() -> SistemaAprendizadoAdaptativo:
    """Retorna instância única do sistema de aprendizado"""
    global _sistema
    if _sistema is None:
        _sistema = SistemaAprendizadoAdaptativo()
    return _sistema
