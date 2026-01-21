import pandas as pd

df = pd.read_excel('HB - Zanchetta - Blancheamento 10.02.2025.xlsx', sheet_name='Acionamento 1A')
nomenclaturas = df.iloc[3:, 7].dropna().astype(str).tolist()

print('=== Todas Nomenclaturas no HB ===')
for nom in sorted(set(nomenclaturas)):
    if nom not in ['NOMENCLATURA', 'nan']:
        print(f'  {nom}')

print('\n=== Procurando padrões faltantes ===')
missing = ['ACT-RES', 'SENS-EL', 'IF-RES', 'VAL-GAS', 'FT-AT']
for pattern in missing:
    matches = [n for n in nomenclaturas if pattern in n]
    if matches:
        print(f'{pattern}: {set(matches)}')
    else:
        print(f'{pattern}: NÃO ENCONTRADO')
