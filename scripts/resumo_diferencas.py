import pandas as pd
import json

df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
df_gen = pd.read_excel('outputs/Painel_Aprendizado_V1.xlsx', sheet_name='Acionamento CCM-1A')

print("PRINCIPAIS DIFERENCAS ENCONTRADAS")
print("="*60)

# Contagens
noms_ref = [str(x) for x in df_ref['NOMENCLATURA'].unique() if pd.notna(x)]
noms_gen = [str(x) for x in df_gen['NOMENCLATURA'].unique() if pd.notna(x)]

# Faltam completamente
faltam = set(noms_ref) - set(noms_gen)
sobram = set(noms_gen) - set(noms_ref)

print(f"\n[1] FALTAM COMPLETAMENTE ({len(faltam)}):\n")
for nom in sorted(faltam):
    count = len(df_ref[df_ref['NOMENCLATURA'] == nom])
    print(f"  {nom}: {count} linhas")

print(f"\n[2] SOBRAM ({len(sobram)}):\n")
for nom in sorted(sobram):
    count = len(df_gen[df_gen['NOMENCLATURA'] == nom])
    print(f"  {nom}: {count} linhas")

print("\n[3] DIFERENCAS PARCIAIS:\n")
for nom in sorted(set(noms_ref) & set(noms_gen)):
    count_ref = len(df_ref[df_ref['NOMENCLATURA'] == nom])
    count_gen = len(df_gen[df_gen['NOMENCLATURA'] == nom])
    if count_ref != count_gen:
        print(f"  {nom}: REF={count_ref}, GEN={count_gen}, DIF={count_ref-count_gen}")

print("\n" + "="*60)
print(f"TOTAL:")
print(f"  Linhas REF: {len(df_ref)}")
print(f"  Linhas GEN: {len(df_gen)}")
print(f"  Diferenca: {len(df_ref) - len(df_gen)}")
