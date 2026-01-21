import pandas as pd

df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
df_gen = pd.read_excel('Painel_TESTE3.xlsx', sheet_name='Acionamento CCM-1A')

print(f'Referência: {len(df_ref)} linhas')
print(f'Gerado: {len(df_gen)} linhas')
print(f'Diferença: {len(df_ref) - len(df_gen)} linhas')
print(f'\n=== DIFERENÇAS ===')

ref_noms = [str(x) for x in df_ref['NOMENCLATURA'].unique() if pd.notna(x)]
gen_noms = [str(x) for x in df_gen['NOMENCLATURA'].unique() if pd.notna(x)]
all_noms = sorted(set(ref_noms + gen_noms))

for nom in all_noms:
    ref_count = len(df_ref[df_ref['NOMENCLATURA'] == nom]) if nom in df_ref['NOMENCLATURA'].values else 0
    gen_count = len(df_gen[df_gen['NOMENCLATURA'] == nom]) if nom in df_gen['NOMENCLATURA'].values else 0
    if ref_count != gen_count:
        print(f'{nom}: REF={ref_count}, GER={gen_count} [DIF={ref_count-gen_count}]')
