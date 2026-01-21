import pandas as pd

df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
df_gen = pd.read_excel('Painel_TESTE3.xlsx', sheet_name='Acionamento CCM-1A')

print('=== Extras no gerado ===')
for nom in df_gen['NOMENCLATURA'].unique():
    if pd.notna(nom):
        ref_count = len(df_ref[df_ref['NOMENCLATURA'] == str(nom)])
        gen_count = len(df_gen[df_gen['NOMENCLATURA'] == nom])
        if gen_count > ref_count:
            print(f'  {nom}: REF={ref_count}, GER={gen_count} [EXTRA={gen_count-ref_count}]')

print('\n=== Resumo ===')
print(f'Referência: {len(df_ref)} linhas')
print(f'Gerado: {len(df_gen)} linhas')
print(f'Diferença: {len(df_ref) - len(df_gen)} linhas')

# Calcula totais
faltando_total = sum([
    6,  # ACT-RES-1
    2,  # ACT-RES-2
    3,  # IF-RES-1
    2,  # VAL-GAS-CA-1
    1   # FT-AT
])
print(f'\nFaltando (não no HB): {faltando_total} linhas')
print(f'Diferença real: {len(df_ref) - len(df_gen)} linhas')
print(f'Portanto: {faltando_total - (len(df_ref) - len(df_gen))} linhas extras sendo geradas')
