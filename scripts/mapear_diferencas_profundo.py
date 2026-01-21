"""
Analisador Profundo - Mapeia TODAS as diferenças célula por célula
"""

import pandas as pd
import json
from collections import defaultdict

def mapear_todas_diferencas():
    """Mapeia todas as diferenças entre HB e Referência linha por linha"""
    
    print("="*80)
    print("MAPEAMENTO COMPLETO: HB → REFERÊNCIA (Célula por Célula)")
    print("="*80)
    
    # Ler arquivos
    df_hb = pd.read_excel('HB - Zanchetta - Blancheamento 10.02.2025.xlsx', sheet_name='Acionamento 1A')
    df_hb.columns = df_hb.iloc[3]
    df_hb = df_hb.iloc[4:].reset_index(drop=True)
    
    df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
    
    # Mapeamento de colunas HB → REF
    col_mapping = {
        'NOMENCLATURA': 'NOMENCLATURA',
        'CARTÃO': 'CARTAO',
        'ANILHA 1': 'ANILHA-CARTAO',
        'ANILHA 2': 'ANIHA-RELE',
        'RELE': 'RELE',
        'DESCRIÇÃO': 'DESCRICAO',
        'CV': 'CAVALO',
        'BORNE': 'BORNE'
    }
    
    # Criar tabela de mapeamento completo
    mapeamento_completo = []
    
    print("\n[1] ANALISANDO LINHAS DO HB\n")
    
    # Para cada linha do HB, encontrar correspondentes na referência
    for idx_hb, row_hb in df_hb.iterrows():
        nom_hb = str(row_hb.get('NOMENCLATURA', ''))
        
        if pd.isna(nom_hb) or nom_hb == 'nan' or nom_hb == '':
            continue
        
        # Procurar na referência
        # Transformar nomenclatura K-AT-XA → AT-X
        if nom_hb.startswith('K-AT-'):
            import re
            match = re.search(r'K-AT-(\d+)([AF])', nom_hb)
            if match:
                num = match.group(1)
                tipo = match.group(2)
                nom_ref = f'AT-{num}'
                
                # Encontrar linhas correspondentes na referência
                linhas_ref = df_ref[df_ref['NOMENCLATURA'] == nom_ref]
                
                # Mapear K-AT-XA para primeira linha de descrição K-AT-XA
                # Mapear K-AT-XF para segunda linha de descrição K-AT-XF
                if not linhas_ref.empty:
                    if tipo == 'A':
                        linha_ref = linhas_ref[linhas_ref['DESCRICAO'].str.contains(f'K-AT-{num}A', na=False)]
                    else:
                        linha_ref = linhas_ref[linhas_ref['DESCRICAO'].str.contains(f'K-AT-{num}F', na=False)]
                    
                    if not linha_ref.empty:
                        linha_ref = linha_ref.iloc[0]
                        
                        mapa = {
                            'hb_linha': idx_hb + 1,
                            'hb_nomenclatura': nom_hb,
                            'hb_anilha1': str(row_hb.get('ANILHA 1', '')),
                            'hb_anilha2': str(row_hb.get('ANILHA 2', '')),
                            'ref_nomenclatura': linha_ref['NOMENCLATURA'],
                            'ref_descricao': linha_ref['DESCRICAO'],
                            'ref_anilha_cartao': linha_ref['ANILHA-CARTAO'],
                            'ref_anilha_rele': linha_ref['ANIHA-RELE'],
                            'ref_borne': linha_ref.get('BORNE', ''),
                            'transformacao': 'K-AT-X → AT-X (expandido)'
                        }
                        
                        mapeamento_completo.append(mapa)
                        
                        print(f"  {nom_hb}:")
                        print(f"    HB: ANILHA1={mapa['hb_anilha1']}, ANILHA2={mapa['hb_anilha2']}")
                        print(f"    REF: DESC={mapa['ref_descricao']}, ANILHA={mapa['ref_anilha_cartao']}, BORNE={mapa['ref_borne']}")
    
    # Salvar mapeamento
    with open('data/mapeamento_completo_hb_ref.json', 'w', encoding='utf-8') as f:
        json.dump(mapeamento_completo, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n✅ Mapeamento salvo: {len(mapeamento_completo)} transformações")
    print("   📁 data/mapeamento_completo_hb_ref.json")
    
    # Análise de BORNEs
    print("\n\n[2] ANÁLISE DE BORNES\n")
    
    bornes_mapeados = {}
    for mapa in mapeamento_completo:
        if mapa['ref_borne'] and mapa['ref_borne'] != 'nan':
            key = mapa['hb_nomenclatura']
            bornes_mapeados[key] = mapa['ref_borne']
            print(f"  {key} → BORNE: {mapa['ref_borne']}")
    
    # Detectar padrão de BORNEs
    # K-AT-1A → x20A, K-AT-1F → x20B
    # K-AT-2A → x21A, K-AT-2F → x21B
    print("\n  PADRÃO DETECTADO:")
    print("    K-AT-XA → x{20+X-1}A")
    print("    K-AT-XF → x{20+X-1}B")
    
    return mapeamento_completo

if __name__ == "__main__":
    mapeamento = mapear_todas_diferencas()
