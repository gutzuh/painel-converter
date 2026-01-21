"""
Análise Comparativa - Compara arquivo gerado com referência
para descobrir padrões de expansão faltantes
"""

import openpyxl
from collections import Counter, defaultdict

def carregar_excel(path, sheet_name):
    """Carrega dados de uma aba Excel"""
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet_name]
    
    dados = []
    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if row[0] and str(row[0]).strip() != 'NOMENCLATURA':
            dados.append({
                'linha': idx,
                'nomenclatura': str(row[0]).strip(),
                'descricao': str(row[1]).strip() if row[1] else '',
                'cartao': str(row[2]).strip() if row[2] else '',
                'anilha1': str(row[3]).strip() if row[3] else '',
                'anilha2': str(row[4]).strip() if row[4] else '',
                'tensao': str(row[5]).strip() if row[5] else '',
            })
    return dados

def agrupar_por_nomenclatura(dados):
    """Agrupa linhas por nomenclatura"""
    grupos = defaultdict(list)
    for d in dados:
        grupos[d['nomenclatura']].append(d)
    return dict(grupos)

def comparar_arquivos(ref_path, gen_path):
    """Compara arquivo gerado com referência"""
    
    print("=" * 100)
    print("ANÁLISE COMPARATIVA - DESCOBRINDO PADRÕES FALTANTES")
    print("=" * 100)
    
    # Carregar dados
    print("\n[1/5] Carregando arquivos...")
    ref_dados = carregar_excel(ref_path, 'Acionamento CCM-1A')
    gen_dados = carregar_excel(gen_path, 'Acionamento CCM-1A')
    
    print(f"      Referência: {len(ref_dados)} linhas")
    print(f"      Gerado:     {len(gen_dados)} linhas")
    print(f"      Diferença:  {len(ref_dados) - len(gen_dados)} linhas faltando")
    
    # Agrupar por nomenclatura
    print("\n[2/5] Agrupando por nomenclatura...")
    ref_grupos = agrupar_por_nomenclatura(ref_dados)
    gen_grupos = agrupar_por_nomenclatura(gen_dados)
    
    print(f"      Nomenclaturas únicas REF: {len(ref_grupos)}")
    print(f"      Nomenclaturas únicas GEN: {len(gen_grupos)}")
    
    # Comparar contadores
    print("\n[3/5] Comparando contadores...")
    ref_counter = Counter([d['nomenclatura'] for d in ref_dados])
    gen_counter = Counter([d['nomenclatura'] for d in gen_dados])
    
    # Encontrar diferenças
    print("\n[4/5] Identificando diferenças...")
    
    faltantes = {}
    for nom, count_ref in ref_counter.items():
        count_gen = gen_counter.get(nom, 0)
        if count_gen < count_ref:
            faltantes[nom] = {
                'ref': count_ref,
                'gen': count_gen,
                'diff': count_ref - count_gen,
                'linhas_ref': ref_grupos[nom],
                'linhas_gen': gen_grupos.get(nom, [])
            }
    
    extras = {}
    for nom, count_gen in gen_counter.items():
        count_ref = ref_counter.get(nom, 0)
        if count_gen > count_ref:
            extras[nom] = {
                'ref': count_ref,
                'gen': count_gen,
                'diff': count_gen - count_ref
            }
    
    # Gerar relatório detalhado
    print("\n[5/5] Gerando relatório de padrões...")
    
    print("\n" + "=" * 100)
    print(f"NOMENCLATURAS FALTANDO ({len(faltantes)} tipos, {sum(f['diff'] for f in faltantes.values())} linhas)")
    print("=" * 100)
    
    for nom in sorted(faltantes.keys()):
        info = faltantes[nom]
        print(f"\n{nom}: REF={info['ref']}, GEN={info['gen']}, FALTA={info['diff']}")
        print(f"  Estrutura na Referência ({len(info['linhas_ref'])} linhas):")
        
        # Mostrar padrão de cartões na referência
        cartoes_ref = [l['cartao'] for l in info['linhas_ref'] if l['cartao']]
        if cartoes_ref:
            cartoes_unicos = list(dict.fromkeys(cartoes_ref))  # Manter ordem
            print(f"    Cartões: {cartoes_unicos[:10]}")  # Primeiros 10
        
        # Mostrar alguns exemplos de linhas
        for i, linha in enumerate(info['linhas_ref'][:3], 1):
            cart_short = linha['cartao'][:30] if linha['cartao'] else ''
            anilha2_short = linha['anilha2'][:20] if linha['anilha2'] else ''
            print(f"    Ex{i}: Cartao=[{cart_short}] Anilha2=[{anilha2_short}]")
        
        if info['linhas_gen']:
            print(f"  No Gerado ({len(info['linhas_gen'])} linhas - deveria ter {info['ref']}):")
            for i, linha in enumerate(info['linhas_gen'][:2], 1):
                cart_short = linha['cartao'][:30] if linha['cartao'] else ''
                print(f"    Ex{i}: Cartao=[{cart_short}]")
    
    if extras:
        print("\n" + "=" * 100)
        print(f"NOMENCLATURAS EXTRAS ({len(extras)} tipos)")
        print("=" * 100)
        for nom in sorted(extras.keys()):
            info = extras[nom]
            print(f"  {nom}: REF={info['ref']}, GEN={info['gen']}, EXTRA=+{info['diff']}")
    
    # Análise de padrões de expansão
    print("\n" + "=" * 100)
    print("ANÁLISE DE PADRÕES DE EXPANSÃO")
    print("=" * 100)
    
    for nom in sorted(faltantes.keys()):
        info = faltantes[nom]
        
        # Detectar padrão
        linhas_ref = info['linhas_ref']
        
        # Verificar se tem padrão de "Borne"
        tem_borne = any('BORNE' in l['cartao'].upper() for l in linhas_ref)
        
        # Verificar se multiplica por sub-items
        cartoes_base = [l['cartao'] for l in linhas_ref if 'BORNE' not in l['cartao'].upper() and l['cartao']]
        cartoes_borne = [l['cartao'] for l in linhas_ref if 'BORNE' in l['cartao'].upper()]
        
        if tem_borne and cartoes_base:
            num_base = len(cartoes_base)
            num_borne = len(cartoes_borne)
            print(f"\n{nom}:")
            print(f"  Padrão DESCOBERTO: {num_base} linhas base + {num_borne} linhas borne = {len(linhas_ref)} total")
            
            if num_borne % num_base == 0:
                bornes_por_item = num_borne // num_base
                print(f"  Regra: Cada item base gera {bornes_por_item} linhas de borne adicionais")
                
                # Mostrar padrão dos bornes
                for i in range(min(num_base, 2)):  # Primeiros 2 itens
                    print(f"    Item {i+1}: {cartoes_base[i]}")
                    start_borne = i * bornes_por_item
                    end_borne = start_borne + bornes_por_item
                    for b in cartoes_borne[start_borne:end_borne]:
                        print(f"      -> {b}")
        elif info['diff'] > 1:
            # Outro tipo de padrão
            print(f"\n{nom}:")
            print(f"  Padrão: Replicação simples de {info['gen']} para {info['ref']} linhas")
            
            # Ver se há variação nos cartões
            cartoes_unicos = list(set([l['cartao'] for l in linhas_ref if l['cartao']]))
            if len(cartoes_unicos) > 1:
                print(f"  Cartões variados: {cartoes_unicos[:5]}")
            else:
                print(f"  Cartão fixo: {cartoes_unicos[0] if cartoes_unicos else 'vazio'}")
    
    print("\n" + "=" * 100)
    print("RESUMO FINAL")
    print("=" * 100)
    print(f"Total de nomenclaturas com diferenças: {len(faltantes)}")
    print(f"Total de linhas a adicionar: {sum(f['diff'] for f in faltantes.values())}")
    print(f"Total de nomenclaturas extras a remover: {len(extras)}")
    print(f"Total de linhas extras: {sum(e['diff'] for e in extras.values())}")
    print(f"\nDiferença líquida: {len(ref_dados) - len(gen_dados)} linhas")
    
    return faltantes, extras


if __name__ == "__main__":
    ref_path = r'Painel - referncia.xlsx'
    gen_path = r'Painel_Gerado_V4.xlsx'  # Arquivo gerado mais recente
    
    faltantes, extras = comparar_arquivos(ref_path, gen_path)
