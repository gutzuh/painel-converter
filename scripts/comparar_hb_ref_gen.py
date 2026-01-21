import pandas as pd

print("=== COMPARAÇÃO: HB ORIGINAL vs REFERÊNCIA vs GERADO ===\n")

# HB Original
df_hb = pd.read_excel('HB - Zanchetta - Blancheamento 10.02.2025.xlsx', sheet_name='Acionamento 1A')
df_hb.columns = df_hb.iloc[3]
df_hb = df_hb.iloc[4:].reset_index(drop=True)

# Referência
df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')

# Gerado
df_gen = pd.read_excel('Painel_FINAL_COMPATIVEL.xlsx', sheet_name='Acionamento CCM-1A')

print("1. K-AT-1A\n")
print("HB ORIGINAL:")
kat1a_hb = df_hb[df_hb['NOMENCLATURA'].astype(str).str.contains('K-AT-1A', na=False)]
if not kat1a_hb.empty:
    print(f"  ANILHA 1: {kat1a_hb.iloc[0]['ANILHA 1']}")
    print(f"  ANILHA 2: {kat1a_hb.iloc[0]['ANILHA 2']}")

print("\nREFERÊNCIA (esperado):")
kat1a_ref = df_ref[df_ref['DESCRICAO'] == 'K-AT-1A']
if not kat1a_ref.empty:
    print(f"  ANILHA-CARTAO: {kat1a_ref.iloc[0]['ANILHA-CARTAO']}")
    print(f"  ANIHA-RELE: {kat1a_ref.iloc[0]['ANIHA-RELE']}")

print("\nGERADO:")
kat1a_gen = df_gen[df_gen['DESCRICAO'] == 'K-AT-1A']
if not kat1a_gen.empty:
    print(f"  ANILHA-CARTAO: {kat1a_gen.iloc[0]['ANILHA-CARTAO']}")
    print(f"  ANIHA-RELE: {kat1a_gen.iloc[0]['ANIHA-RELE']}")

print("\n" + "="*80)
print("ANÁLISE:")
print("="*80)

if not kat1a_hb.empty and not kat1a_gen.empty:
    hb_anilha1 = str(kat1a_hb.iloc[0]['ANILHA 1'])
    gen_anilha = str(kat1a_gen.iloc[0]['ANILHA-CARTAO'])
    
    if hb_anilha1 == gen_anilha:
        print("✅ GERADO está CORRETO - corresponde ao HB original")
        print(f"   HB tem: {hb_anilha1}")
        print(f"   GERADO tem: {gen_anilha}")
    else:
        print("⚠️  GERADO difere do HB original")
        print(f"   HB tem: {hb_anilha1}")
        print(f"   GERADO tem: {gen_anilha}")

if not kat1a_ref.empty and not kat1a_hb.empty:
    ref_anilha = str(kat1a_ref.iloc[0]['ANILHA-CARTAO'])
    hb_anilha1 = str(kat1a_hb.iloc[0]['ANILHA 1'])
    
    if ref_anilha != hb_anilha1:
        print("\n⚠️  REFERÊNCIA foi MODIFICADA - não reflete o HB original!")
        print(f"   HB original: {hb_anilha1}")
        print(f"   REFERÊNCIA: {ref_anilha}")
        print("\n   Conclusão: O arquivo de referência foi editado manualmente")
        print("   e contém dados diferentes do HB de entrada!")

print("\n\n2. VERIFICANDO MAIS NOMENCLATURAS\n")

test_cases = [
    ('K-AT-2A', 'K-AT-2A'),
    ('K-AT-3A', 'K-AT-3A'),
    ('Atuador 1', 'Atuador 1')
]

for hb_nom, desc in test_cases:
    print(f"\n{desc}:")
    
    # HB
    item_hb = df_hb[df_hb['NOMENCLATURA'].astype(str) == hb_nom]
    if not item_hb.empty:
        print(f"  HB: ANILHA 1 = {item_hb.iloc[0]['ANILHA 1']}")
    
    # Referência  
    item_ref = df_ref[df_ref['DESCRICAO'] == desc]
    if not item_ref.empty:
        print(f"  REF: ANILHA-CARTAO = {item_ref.iloc[0]['ANILHA-CARTAO']}")
    
    # Gerado
    item_gen = df_gen[df_gen['DESCRICAO'] == desc]
    if not item_gen.empty:
        print(f"  GER: ANILHA-CARTAO = {item_gen.iloc[0]['ANILHA-CARTAO']}")
