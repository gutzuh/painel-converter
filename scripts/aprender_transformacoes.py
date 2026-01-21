"""
Sistema de Aprendizado Automático - Comparação HB vs Referência

Este script analisa as diferenças entre o HB original e a referência
para aprender automaticamente todas as transformações necessárias.
"""

import pandas as pd
import json
from collections import defaultdict
import re

def analisar_transformacoes_completas():
    """Analisa todas as transformações do HB para a Referência"""
    
    print("="*80)
    print("ANÁLISE COMPLETA DE TRANSFORMAÇÕES HB → REFERÊNCIA")
    print("="*80)
    
    # 1. Ler HB original
    df_hb = pd.read_excel('HB - Zanchetta - Blancheamento 10.02.2025.xlsx', sheet_name='Acionamento 1A')
    df_hb.columns = df_hb.iloc[3]
    df_hb = df_hb.iloc[4:].reset_index(drop=True)
    
    # Limpar colunas
    df_hb = df_hb.dropna(how='all')
    
    # 2. Ler Referência
    df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
    
    # 3. Mapear transformações de nomenclatura
    transformacoes_nomenclatura = {}
    
    print("\n[1] TRANSFORMAÇÕES DE NOMENCLATURA\n")
    
    # Analisar nomenclaturas do HB
    noms_hb = df_hb['NOMENCLATURA'].dropna().unique()
    noms_ref = df_ref['NOMENCLATURA'].unique()
    
    # Detectar padrão: K-AT-XA/K-AT-XF → AT-X (expansão)
    for nom_hb in noms_hb:
        nom_str = str(nom_hb)
        
        # K-AT-XA, K-AT-XF → AT-X
        if nom_str.startswith('K-AT-'):
            base = re.search(r'K-AT-(\d+)[AF]', nom_str)
            if base:
                num = base.group(1)
                transformacoes_nomenclatura[nom_str] = f'AT-{num}'
                print(f"  {nom_str} → AT-{num}")
        
        # Outros padrões similares
        elif nom_str.startswith('K-'):
            # Remove K- prefix
            sem_k = nom_str.replace('K-', '')
            transformacoes_nomenclatura[nom_str] = sem_k
            print(f"  {nom_str} → {sem_k}")
    
    # 4. Analisar transformações de ANILHA
    print("\n\n[2] TRANSFORMAÇÕES DE ANILHA\n")
    
    # Padrão descoberto: 1A-CT-1.12 → 1A-AT-1.1 para K-AT-1A
    # Regra: Para K-AT-XA, ANILHA muda de 1A-CT-Y.Z para 1A-AT-X.1
    #        Para K-AT-XF, ANILHA muda de 1A-CT-Y.Z para 1A-AT-X.2
    
    transformacoes_anilha = {}
    
    for idx, row in df_hb.iterrows():
        nom = str(row['NOMENCLATURA'])
        
        if nom.startswith('K-AT-'):
            match = re.search(r'K-AT-(\d+)([AF])', nom)
            if match:
                num = match.group(1)
                tipo = match.group(2)
                suffix = '1' if tipo == 'A' else '2'
                
                anilha_nova = f'1A-AT-{num}.{suffix}'
                anilha_original = str(row['ANILHA 1'])
                
                transformacoes_anilha[f'{nom}|{anilha_original}'] = anilha_nova
                print(f"  {nom}: {anilha_original} → {anilha_nova}")
    
    # 5. Analisar expansões (1 linha HB → N linhas Referência)
    print("\n\n[3] PADRÕES DE EXPANSÃO\n")
    
    expansoes = defaultdict(lambda: {'count_hb': 0, 'count_ref': 0, 'fator': 0})
    
    # Contar por nomenclatura base (sem K- prefix)
    for nom_hb in noms_hb:
        nom_str = str(nom_hb)
        if pd.notna(nom_str) and nom_str != 'nan':
            count_hb = len(df_hb[df_hb['NOMENCLATURA'] == nom_str])
            
            # Encontrar correspondente na referência
            # K-AT-1A → AT-1
            if nom_str.startswith('K-AT-'):
                match = re.search(r'K-AT-(\d+)', nom_str)
                if match:
                    num = match.group(1)
                    nom_ref = f'AT-{num}'
                    count_ref = len(df_ref[df_ref['NOMENCLATURA'] == nom_ref])
                    
                    expansoes[nom_ref]['count_hb'] += 1
                    expansoes[nom_ref]['count_ref'] = count_ref
    
    # Calcular fatores
    for nom, data in expansoes.items():
        if data['count_hb'] > 0:
            data['fator'] = data['count_ref'] / data['count_hb']
            print(f"  {nom}: {data['count_hb']} linhas HB → {data['count_ref']} linhas REF (fator: {data['fator']:.1f}x)")
    
    # 6. Detectar campos que foram adicionados
    print("\n\n[4] CAMPOS ADICIONADOS/MODIFICADOS\n")
    
    # Exemplo: Borne foi adicionado na referência
    campos_novos = []
    
    # Verificar Borne
    bornes_ref = df_ref['BORNE'].dropna()
    if len(bornes_ref) > 0:
        print(f"  BORNE: {len(bornes_ref)} valores na referência")
        campos_novos.append('BORNE')
    
    # Verificar Cabeamento
    cab_ref = df_ref['CABEAMENTO'].dropna()
    if len(cab_ref) > 0:
        print(f"  CABEAMENTO: {len(cab_ref)} valores na referência")
        campos_novos.append('CABEAMENTO')
    
    # 7. Salvar aprendizado
    aprendizado = {
        'transformacoes_nomenclatura': transformacoes_nomenclatura,
        'transformacoes_anilha': transformacoes_anilha,
        'expansoes': dict(expansoes),
        'campos_novos': campos_novos,
        'versao': '2.0'
    }
    
    with open('data/aprendizado_transformacoes.json', 'w', encoding='utf-8') as f:
        json.dump(aprendizado, f, indent=2, ensure_ascii=False)
    
    print("\n\n[5] APRENDIZADO SALVO\n")
    print(f"  ✅ {len(transformacoes_nomenclatura)} transformações de nomenclatura")
    print(f"  ✅ {len(transformacoes_anilha)} transformações de anilha")
    print(f"  ✅ {len(expansoes)} padrões de expansão")
    print(f"  ✅ {len(campos_novos)} campos novos detectados")
    print(f"\n  📁 Salvo em: data/aprendizado_transformacoes.json")
    
    return aprendizado

if __name__ == "__main__":
    aprendizado = analisar_transformacoes_completas()
