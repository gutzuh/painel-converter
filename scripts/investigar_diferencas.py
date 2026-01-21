import pandas as pd

print("=== INVESTIGAÇÃO DETALHADA ===\n")

# 1. Comparar primeiras 10 linhas de Acionamento
print("1. PRIMEIRAS 10 LINHAS DE ACIONAMENTO\n")
print("REFERÊNCIA:")
df_ref = pd.read_excel('Painel - referncia.xlsx', sheet_name='Acionamento CCM-1A')
print(df_ref[['NOMENCLATURA', 'DESCRICAO', 'CARTAO']].head(10).to_string(index=False))

print("\n\nGERADO:")
df_gen = pd.read_excel('Painel_FINAL_COMPATIVEL.xlsx', sheet_name='Acionamento CCM-1A')
print(df_gen[['NOMENCLATURA', 'DESCRICAO', 'CARTAO']].head(10).to_string(index=False))

# 2. Verificar se AT-1 está correto
print("\n\n2. EXPANSÃO DE AT-1\n")
print("REFERÊNCIA (AT-1):")
at1_ref = df_ref[df_ref['NOMENCLATURA'] == 'AT-1']
print(at1_ref[['NOMENCLATURA', 'DESCRICAO', 'ANILHA-CARTAO']].to_string(index=False))

print("\n\nGERADO (AT-1):")
at1_gen = df_gen[df_gen['NOMENCLATURA'] == 'AT-1']
print(at1_gen[['NOMENCLATURA', 'DESCRICAO', 'ANILHA-CARTAO']].to_string(index=False))

# 3. Verificar nomenclaturas de Status (Reconhecimento)
print("\n\n3. ABA RECONHECIMENTO - PRIMEIRAS 10 LINHAS\n")
print("REFERÊNCIA:")
df_ref_status = pd.read_excel('Painel - referncia.xlsx', sheet_name='Reconhecimento CCM-1A')
print(df_ref_status[['NOMENCLATURA', 'DESCRIÇÃO']].head(10).to_string(index=False))

print("\n\nGERADO:")
df_gen_status = pd.read_excel('Painel_FINAL_COMPATIVEL.xlsx', sheet_name='Reconhecimento CCM-1A')
print(df_gen_status[['NOMENCLATURA', 'DESCRIÇÃO']].head(10).to_string(index=False))

# 4. Verificar EL-1 e SENS-EL-1
print("\n\n4. ELEVADORES (EL-1) E SENSORES (SENS-EL-1)\n")
print("GERADO - EL-1:")
el1 = df_gen[df_gen['NOMENCLATURA'] == 'EL-1']
if not el1.empty:
    print(el1[['NOMENCLATURA', 'DESCRICAO', 'CARTAO']].to_string(index=False))
else:
    print("  Não encontrado")

print("\n\nGERADO - SENS-EL-1:")
sensel1 = df_gen[df_gen['NOMENCLATURA'] == 'SENS-EL-1']
if not sensel1.empty:
    print(sensel1[['NOMENCLATURA', 'DESCRICAO', 'CARTAO']].to_string(index=False))
else:
    print("  Não encontrado")
