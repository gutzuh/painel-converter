import pandas as pd

df = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
patterns = ['ACT-RES-1', 'ACT-RES-2', 'SENS-EL-1', 'IF-RES-1', 'VAL-GAS-CA-1', 'FT-AT', 'IGN-CA-1']

for p in patterns:
    subset = df[df['NOMENCLATURA'] == p]
    if not subset.empty:
        print(f'\n=== {p} ({len(subset)} linhas) ===')
        print(subset[['NOMENCLATURA', 'DESCRICAO', 'CARTAO', 'ANILHA-CARTAO']].to_string(index=False))
