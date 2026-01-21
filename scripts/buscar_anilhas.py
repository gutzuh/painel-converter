import pandas as pd

# Ler a aba Acionamento 1A
acionamento = pd.read_excel('HB - Zanchetta - Blancheamento 10.02.2025.xlsx', sheet_name='Acionamento 1A', skiprows=3)
acionamento.columns = acionamento.iloc[0]
acionamento = acionamento[1:].reset_index(drop=True)

# Anilhas que queremos encontrar
anilhas_procuradas = ['1A-ACT-44', '1A-ACT-45', '1A-ACT-46', '1A-ACT-47', '1A-ACT-48']

# Filtrar as linhas que contêm as anilhas procuradas
resultados = acionamento[acionamento['ANILHA 2'].isin(anilhas_procuradas)]

print('=== TABELA FORMATADA ===\n')
print('| Anilha2    | Cartão      | Anilha1    | Descrição do Status             |')
print('|------------|-------------|------------|---------------------------------|')
for _, row in resultados.iterrows():
    anilha2 = row['ANILHA 2']
    cartao = row['CARTÃO']
    anilha1 = row['ANILHA 1']
    descricao = row.get('DESCRIÇÃO', '')
    if pd.isna(descricao):
        descricao = ''
    print(f'| {anilha2:<10} | {cartao:<11} | {anilha1:<10} | {descricao:<31} |')

print('\n=== DADOS COMPLETOS ===\n')
print(resultados[['CARTÃO', 'ANILHA 1', 'ANILHA 2', 'DESCRIÇÃO', 'NOMENCLATURA']].to_string())
