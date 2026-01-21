import pandas as pd

print("=== ANÁLISE DO HB ORIGINAL ===\n")

# Ler HB
df_hb = pd.read_excel('HB - Zanchetta - Blancheamento 10.02.2025.xlsx', sheet_name='Acionamento 1A')

# Encontrar header
print("1. ESTRUTURA DO HB\n")
print("Primeiras 10 linhas:")
print(df_hb.head(10).to_string())

# Encontrar linha com NOMENCLATURA
header_row = None
for idx, row in df_hb.iterrows():
    if 'NOMENCLATURA' in str(row.values):
        header_row = idx
        break

print(f"\n\nHeader encontrado na linha: {header_row}")

if header_row is not None:
    # Definir header corretamente
    df_hb.columns = df_hb.iloc[header_row]
    df_hb = df_hb.iloc[header_row+1:].reset_index(drop=True)
    
    print("\n\n2. DADOS DO HB APÓS HEADER\n")
    print("Primeiras 20 linhas:")
    print(df_hb[['NOMENCLATURA', 'ANILHA 1', 'ANILHA 2']].head(20).to_string(index=False))
    
    # Verificar AT-1
    print("\n\n3. AT-1 NO HB ORIGINAL\n")
    at1_hb = df_hb[df_hb['NOMENCLATURA'].astype(str).str.contains('AT-1', na=False)]
    if not at1_hb.empty:
        print(at1_hb[['NOMENCLATURA', 'ANILHA 1', 'ANILHA 2']].to_string(index=False))
    
    # Verificar K-AT-1A
    print("\n\n4. K-AT-1A NO HB ORIGINAL\n")
    kat1a = df_hb[df_hb['NOMENCLATURA'].astype(str).str.contains('K-AT-1A', na=False)]
    if not kat1a.empty:
        print(kat1a[['NOMENCLATURA', 'ANILHA 1', 'ANILHA 2']].to_string(index=False))
