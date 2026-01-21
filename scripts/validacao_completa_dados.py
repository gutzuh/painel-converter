import pandas as pd
from collections import defaultdict

def comparar_abas_detalhado(ref_path, gen_path):
    """Compara todas as abas em detalhe"""
    
    abas = [
        'Descrição de Projeto CCM-1A',
        'Acionamento CCM-1A', 
        'Reconhecimento CCM-1A',
        'Informações Especiais CCM-1A'
    ]
    
    print("="*80)
    print("VALIDAÇÃO COMPLETA DE DADOS - COMPARAÇÃO DETALHADA")
    print("="*80)
    
    total_diferencas = 0
    
    for aba in abas:
        try:
            df_ref = pd.read_excel(ref_path, sheet_name=aba)
            df_gen = pd.read_excel(gen_path, sheet_name=aba)
            
            print(f"\n{'='*80}")
            print(f"ABA: {aba}")
            print(f"{'='*80}")
            
            # 1. Comparar dimensões
            print(f"\n[1] DIMENSÕES:")
            print(f"  Referência: {len(df_ref)} linhas x {len(df_ref.columns)} colunas")
            print(f"  Gerado:     {len(df_gen)} linhas x {len(df_gen.columns)} colunas")
            
            if len(df_ref) != len(df_gen):
                print(f"  ⚠️  DIFERENÇA: {abs(len(df_ref) - len(df_gen))} linhas")
                total_diferencas += abs(len(df_ref) - len(df_gen))
            else:
                print(f"  ✅ Mesmo número de linhas")
            
            # 2. Comparar nomes de colunas
            print(f"\n[2] COLUNAS:")
            colunas_ref = set(df_ref.columns)
            colunas_gen = set(df_gen.columns)
            
            if colunas_ref != colunas_gen:
                faltando = colunas_ref - colunas_gen
                extras = colunas_gen - colunas_ref
                if faltando:
                    print(f"  ⚠️  Faltando no gerado: {faltando}")
                if extras:
                    print(f"  ⚠️  Extras no gerado: {extras}")
                total_diferencas += len(faltando) + len(extras)
            else:
                print(f"  ✅ Mesmas colunas: {list(df_ref.columns)}")
            
            # 3. Comparar valores célula por célula
            print(f"\n[3] CONTEÚDO:")
            
            # Normalizar índices
            min_rows = min(len(df_ref), len(df_gen))
            diferencas_por_coluna = defaultdict(list)
            
            for col in df_ref.columns:
                if col not in df_gen.columns:
                    continue
                    
                for idx in range(min_rows):
                    val_ref = df_ref[col].iloc[idx]
                    val_gen = df_gen[col].iloc[idx]
                    
                    # Normalizar valores para comparação
                    val_ref_norm = str(val_ref).strip() if pd.notna(val_ref) else ""
                    val_gen_norm = str(val_gen).strip() if pd.notna(val_gen) else ""
                    
                    if val_ref_norm != val_gen_norm:
                        diferencas_por_coluna[col].append({
                            'linha': idx + 2,  # +2 porque Excel começa em 1 e tem header
                            'ref': val_ref_norm[:50],  # Limita tamanho
                            'gen': val_gen_norm[:50]
                        })
            
            if diferencas_por_coluna:
                print(f"  ⚠️  DIFERENÇAS ENCONTRADAS:")
                for col, difs in diferencas_por_coluna.items():
                    print(f"\n    Coluna '{col}': {len(difs)} diferenças")
                    # Mostra primeiras 3 diferenças
                    for dif in difs[:3]:
                        print(f"      • Linha {dif['linha']}:")
                        print(f"        REF: '{dif['ref']}'")
                        print(f"        GER: '{dif['gen']}'")
                    if len(difs) > 3:
                        print(f"      ... e mais {len(difs)-3} diferenças")
                    total_diferencas += len(difs)
            else:
                print(f"  ✅ Todos os valores são idênticos")
            
            # 4. Comparar nomenclaturas únicas (para abas principais)
            if 'NOMENCLATURA' in df_ref.columns:
                print(f"\n[4] NOMENCLATURAS:")
                noms_ref = set(df_ref['NOMENCLATURA'].dropna().astype(str))
                noms_gen = set(df_gen['NOMENCLATURA'].dropna().astype(str))
                
                faltando = noms_ref - noms_gen
                extras = noms_gen - noms_ref
                
                if faltando or extras:
                    if faltando:
                        print(f"  ⚠️  Faltando no gerado ({len(faltando)}): {sorted(faltando)}")
                    if extras:
                        print(f"  ⚠️  Extras no gerado ({len(extras)}): {sorted(extras)}")
                else:
                    print(f"  ✅ Mesmas nomenclaturas ({len(noms_ref)} únicas)")
                
                # Comparar contagens por nomenclatura
                counts_ref = df_ref['NOMENCLATURA'].value_counts()
                counts_gen = df_gen['NOMENCLATURA'].value_counts()
                
                dif_counts = []
                for nom in noms_ref | noms_gen:
                    c_ref = counts_ref.get(nom, 0)
                    c_gen = counts_gen.get(nom, 0)
                    if c_ref != c_gen:
                        dif_counts.append((nom, c_ref, c_gen))
                
                if dif_counts:
                    print(f"\n  ⚠️  DIFERENÇAS DE QUANTIDADE:")
                    for nom, c_ref, c_gen in sorted(dif_counts):
                        print(f"    {nom}: REF={c_ref}, GER={c_gen} [DIF={c_ref-c_gen}]")
        
        except Exception as e:
            print(f"\n⚠️  ERRO ao processar aba '{aba}': {e}")
            total_diferencas += 1
    
    # Resumo final
    print(f"\n{'='*80}")
    print(f"RESUMO FINAL")
    print(f"{'='*80}")
    
    if total_diferencas == 0:
        print(f"✅ PERFEITO! Os arquivos são 100% idênticos!")
    else:
        print(f"⚠️  Total de diferenças encontradas: {total_diferencas}")
        print(f"   Fidelidade estimada: {100 - min(total_diferencas * 0.5, 100):.1f}%")

if __name__ == "__main__":
    comparar_abas_detalhado(
        'Painel - referncia.xlsx',
        'Painel_FINAL_COMPATIVEL.xlsx'
    )
