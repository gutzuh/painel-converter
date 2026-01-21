"""
Análise Detalhada das Diferenças Restantes
Para alcançar 100% de identidade
"""

import pandas as pd

def analisar_diferencas_especificas():
    """Analisa cada aba em detalhe para identificar exatamente o que falta"""
    
    print("="*80)
    print("ANÁLISE DETALHADA - CAMINHO PARA 100% DE IDENTIDADE")
    print("="*80)
    
    # 1. DESCRIÇÃO DE PROJETO
    print("\n[1] ABA: Descrição de Projeto CCM-1A")
    print("-" * 60)
    
    df_desc_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Descrição de Projeto CCM-1A')
    df_desc_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Descrição de Projeto CCM-1A')
    
    print(f"  Referência: {len(df_desc_ref)} linhas")
    print(f"  Gerado: {len(df_desc_gen)} linhas")
    print(f"  Diferença: {len(df_desc_ref) - len(df_desc_gen)} linhas")
    
    # Verificar quais nomenclaturas faltam
    noms_ref = set(df_desc_ref['NOMENCLATURA'].dropna().astype(str))
    noms_gen = set(df_desc_gen['NOMENCLATURA'].dropna().astype(str))
    
    faltam_desc = noms_ref - noms_gen
    sobram_desc = noms_gen - noms_ref
    
    if faltam_desc:
        print(f"\n  Faltam ({len(faltam_desc)}):")
        for nom in sorted(faltam_desc):
            print(f"    - {nom}")
    
    if sobram_desc:
        print(f"\n  Sobram ({len(sobram_desc)}):")
        for nom in sorted(sobram_desc):
            print(f"    - {nom}")
    
    # 2. ACIONAMENTO
    print("\n\n[2] ABA: Acionamento CCM-1A")
    print("-" * 60)
    
    df_acio_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
    df_acio_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Acionamento CCM-1A')
    
    print(f"  Referência: {len(df_acio_ref)} linhas")
    print(f"  Gerado: {len(df_acio_gen)} linhas")
    print(f"  Diferença: {len(df_acio_ref) - len(df_acio_gen)} linhas")
    
    # Nomenclaturas faltantes
    noms_acio_ref = [str(x) for x in df_acio_ref['NOMENCLATURA'].unique() if pd.notna(x)]
    noms_acio_gen = [str(x) for x in df_acio_gen['NOMENCLATURA'].unique() if pd.notna(x)]
    
    faltam_acio = set(noms_acio_ref) - set(noms_acio_gen)
    
    if faltam_acio:
        print(f"\n  Faltam ({len(faltam_acio)}):")
        for nom in sorted(faltam_acio):
            count = len(df_acio_ref[df_acio_ref['NOMENCLATURA'] == nom])
            print(f"    - {nom}: {count} linhas")
    
    # 3. RECONHECIMENTO
    print("\n\n[3] ABA: Reconhecimento CCM-1A")
    print("-" * 60)
    
    df_rec_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Reconhecimento CCM-1A')
    df_rec_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Reconhecimento CCM-1A')
    
    print(f"  Referência: {len(df_rec_ref)} linhas")
    print(f"  Gerado: {len(df_rec_gen)} linhas")
    print(f"  Diferença: {len(df_rec_ref) - len(df_rec_gen)} linhas")
    
    noms_rec_ref = [str(x) for x in df_rec_ref['NOMENCLATURA'].unique() if pd.notna(x)]
    noms_rec_gen = [str(x) for x in df_rec_gen['NOMENCLATURA'].unique() if pd.notna(x)]
    
    faltam_rec = set(noms_rec_ref) - set(noms_rec_gen)
    
    if faltam_rec:
        print(f"\n  Faltam ({len(faltam_rec)}):")
        for nom in sorted(faltam_rec)[:15]:  # Primeiras 15
            count = len(df_rec_ref[df_rec_ref['NOMENCLATURA'] == nom])
            print(f"    - {nom}: {count} linhas")
        if len(faltam_rec) > 15:
            print(f"    ... e mais {len(faltam_rec) - 15}")
    
    # 4. INFORMAÇÕES ESPECIAIS
    print("\n\n[4] ABA: Informações Especiais CCM-1A")
    print("-" * 60)
    
    df_info_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Informações Especiais CCM-1A')
    df_info_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Informações Especiais CCM-1A')
    
    print(f"  Referência: {len(df_info_ref)} linhas")
    print(f"  Gerado: {len(df_info_gen)} linhas")
    
    # Comparar valores
    print("\n  Diferenças de conteúdo:")
    for idx in range(min(len(df_info_ref), len(df_info_gen))):
        info_ref = df_info_ref.iloc[idx]['INFORMACAO']
        val_ref = str(df_info_ref.iloc[idx]['VALOR'])
        val_gen = str(df_info_gen.iloc[idx]['VALOR'])
        
        if val_ref != val_gen:
            print(f"    {info_ref}:")
            print(f"      REF: {val_ref}")
            print(f"      GER: {val_gen}")
    
    # RESUMO
    print("\n\n" + "="*80)
    print("RESUMO - O QUE PRECISA SER FEITO PARA 100% IDENTIDADE")
    print("="*80)
    
    print("\n1. ADICIONAR ITENS DE RESERVA:")
    print("   - ACT-RES-1 (6 linhas)")
    print("   - ACT-RES-2 (2 linhas)")
    print("   - IF-RES-1 (3 linhas)")
    print("   - VAL-GAS-CA-1 (2 linhas)")
    print("   - FT-AT (1 linha)")
    print("   Total: 14 linhas")
    
    print("\n2. CORRIGIR ABA RECONHECIMENTO:")
    print("   - Adicionar linhas de status faltantes")
    print("   - Verificar PIS-X, sensores, etc")
    
    print("\n3. AJUSTAR INFORMAÇÕES ESPECIAIS:")
    print("   - Nome do projeto")
    print("   - Data")
    
    print("\n4. ADICIONAR NA DESCRIÇÃO:")
    print("   - Itens de reserva e sensores adicionais")

if __name__ == "__main__":
    analisar_diferencas_especificas()
