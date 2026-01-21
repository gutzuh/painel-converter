import pandas as pd

df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
df_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Acionamento CCM-1A')

print("=== COMPARAÇÃO RÁPIDA: ATUADORES ===\n")

# AT-1
print("1. AT-1 (K-AT-1A)\n")
print("REFERÊNCIA:")
at1_ref = df_ref[(df_ref['NOMENCLATURA'] == 'AT-1') & (df_ref['DESCRICAO'] == 'K-AT-1A')]
if not at1_ref.empty:
    print(f"  ANILHA-CARTAO: {at1_ref.iloc[0]['ANILHA-CARTAO']}")
    print(f"  BORNE: {at1_ref.iloc[0]['BORNE']}")

print("\nGERADO:")
at1_gen = df_gen[(df_gen['NOMENCLATURA'] == 'AT-1') & (df_gen['DESCRICAO'] == 'K-AT-1A')]
if not at1_gen.empty:
    print(f"  ANILHA-CARTAO: {at1_gen.iloc[0]['ANILHA-CARTAO']}")
    print(f"  BORNE: {at1_gen.iloc[0]['BORNE']}")
    
    # Verificar se bateu
    if at1_ref.iloc[0]['ANILHA-CARTAO'] == at1_gen.iloc[0]['ANILHA-CARTAO']:
        print("  ✅ ANILHA CORRETO!")
    else:
        print(f"  ❌ ANILHA DIFERENTE")
    
    if at1_ref.iloc[0]['BORNE'] == at1_gen.iloc[0]['BORNE']:
        print("  ✅ BORNE CORRETO!")
    else:
        print(f"  ❌ BORNE DIFERENTE")

# Contar diferenças
print("\n\n=== RESUMO GERAL ===\n")

diferencas = 0
for col in ['ANILHA-CARTAO', 'BORNE']:
    if col in df_ref.columns and col in df_gen.columns:
        for idx in range(min(len(df_ref), len(df_gen))):
            val_ref = str(df_ref[col].iloc[idx]).strip()
            val_gen = str(df_gen[col].iloc[idx]).strip()
            if val_ref != val_gen and val_ref != 'nan' and val_gen != 'nan':
                diferencas += 1

print(f"Total de diferenças em ANILHA-CARTAO e BORNE: {diferencas}")
