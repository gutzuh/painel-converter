"""
Sistema de Iteração Automática - Aprende e Corrige até ficar 100% igual

Este script vai:
1. Comparar referência vs gerado
2. Detectar TODAS as diferenças
3. Aprender os padrões
4. Atualizar o código
5. Regenerar
6. Repetir até ficar 100% igual
"""

import pandas as pd
import json
from collections import defaultdict
import re

def analisar_todas_diferencas_sistema():
    """Analisa TODAS as diferenças sistemáticas restantes"""
    
    print("="*80)
    print("ANÁLISE COMPLETA DE TODAS AS DIFERENÇAS RESTANTES")
    print("="*80)
    
    df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
    df_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Acionamento CCM-1A')
    
    # Agrupar por nomenclatura e analisar
    noms_ref = [str(x) for x in df_ref['NOMENCLATURA'].unique() if pd.notna(x)]
    noms_gen = [str(x) for x in df_gen['NOMENCLATURA'].unique() if pd.notna(x)]
    noms = sorted(set(noms_ref + noms_gen))
    
    padroes_faltantes = []
    
    for nom in noms:
        if pd.isna(nom) or nom == 'nan':
            continue
        
        linhas_ref = df_ref[df_ref['NOMENCLATURA'] == nom]
        linhas_gen = df_gen[df_gen['NOMENCLATURA'] == nom]
        
        count_ref = len(linhas_ref)
        count_gen = len(linhas_gen)
        
        if count_ref != count_gen:
            padrao = {
                'nomenclatura': nom,
                'count_ref': count_ref,
                'count_gen': count_gen,
                'diferenca': count_ref - count_gen
            }
            
            # Analisar primeiras linhas
            if count_ref > 0:
                primeira_ref = linhas_ref.iloc[0]
                padrao['exemplo_descricao'] = primeira_ref.get('DESCRICAO', '')
                padrao['exemplo_cartao'] = primeira_ref.get('CARTAO', '')
                padrao['exemplo_borne'] = primeira_ref.get('BORNE', '')
                padrao['exemplo_fusivel'] = primeira_ref.get('FUSÍVEL', '')
            
            padroes_faltantes.append(padrao)
            
            print(f"\n{nom}:")
            print(f"  Referência: {count_ref} linhas")
            print(f"  Gerado: {count_gen} linhas")
            print(f"  Diferença: {count_ref - count_gen}")
            
            if count_ref > 0 and count_ref <= 5:
                print(f"  Descrições na referência:")
                for desc in linhas_ref['DESCRICAO'].tolist():
                    print(f"    - {desc}")
    
    # Salvar análise
    with open('data/padroes_faltantes.json', 'w', encoding='utf-8') as f:
        json.dump(padroes_faltantes, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n✅ Análise salva: {len(padroes_faltantes)} padrões diferentes")
    print("   📁 data/padroes_faltantes.json")
    
    # Agrupar por tipo de diferença
    print("\n\n=== CATEGORIZAÇÃO DAS DIFERENÇAS ===\n")
    
    faltam_completos = [p for p in padroes_faltantes if p['count_gen'] == 0]
    faltam_parciais = [p for p in padroes_faltantes if p['count_gen'] > 0 and p['diferenca'] > 0]
    sobram = [p for p in padroes_faltantes if p['diferenca'] < 0]
    
    print(f"1. Faltam completamente ({len(faltam_completos)}):")
    for p in faltam_completos[:10]:
        print(f"   - {p['nomenclatura']}: {p['count_ref']} linhas")
    
    print(f"\n2. Faltam parcialmente ({len(faltam_parciais)}):")
    for p in faltam_parciais[:10]:
        print(f"   - {p['nomenclatura']}: tem {p['count_gen']}, faltam {p['diferenca']}")
    
    print(f"\n3. Sobram ({len(sobram)}):")
    for p in sobram[:10]:
        print(f"   - {p['nomenclatura']}: tem {p['count_gen']}, sobram {-p['diferenca']}")
    
    return padroes_faltantes

if __name__ == "__main__":
    padroes = analisar_todas_diferencas_sistema()
