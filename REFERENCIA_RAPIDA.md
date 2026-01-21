# 📖 Referência Rápida - Conversor de Painel

## 🎯 Uso Básico

### Gerar arquivo Excel
```bash
python main.py "seu_arquivo.xlsx"
```
Gera: `Painel_FINAL_COMPATIVEL.xlsx`

### Com arquivo de saída customizado
```bash
python main.py "seu_arquivo.xlsx" -o "seu_painel.xlsx"
```

### Validar compatibilidade
```bash
python teste_compatibilidade.py
python validador_completo.py
```

---

## 📁 Estrutura de Arquivos

```
conversor_painel/
├── main.py                              # Entrada principal
├── requirements.txt                     # Dependências
│
├── config/
│   ├── patterns.yaml                    # Padrões de expansão
│   └── aprendizado_config.yaml          # Config de aprendizado
│
├── src/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   └── hb_parser.py                # Leitura de arquivo HB
│   ├── transformer/
│   │   ├── __init__.py
│   │   └── transformers.py             # Transformação de dados
│   ├── generator/
│   │   ├── __init__.py
│   │   └── excel_generator.py          # Geração de 4 abas
│   ├── aprendizado/
│   │   ├── __init__.py
│   │   ├── sistema_aprendizado.py      # Descoberta de padrões
│   │   └── sistema_adaptativo.py       # Aplicação de padrões
│   └── validator/
│       └── __init__.py
│
├── Painel_FINAL_COMPATIVEL.xlsx         # SAÍDA FINAL
├── teste_compatibilidade.py             # Validação básica
├── validador_completo.py                # Validação completa
├── INTEGRACAO_COMPLETA.md              # Análise C#
├── STATUS_FINAL.md                      # Status do projeto
└── REFERENCIA_RAPIDA.md                # Este arquivo
```

---

## ⚙️ Configuração

### Padrões (config/patterns.yaml)
```yaml
expansoes:
  DESP-1:
    ativa: true
    confianca: 100  # Percentual
    linhas: 12      # Quantas linhas gera

  DESP-2:
    ativa: true
    confianca: 100
    linhas: 5
  
  # ... mais padrões
```

### Aprendizado (config/aprendizado_config.yaml)
```yaml
modo: "balanceado"  # conservador | balanceado | agressivo
limites:
  conservador: 100  # Usa apenas padrões 100% confiança
  balanceado: 80    # Usa padrões 80%+ confiança
  agressivo: 60     # Usa padrões 60%+ confiança
```

---

## 📊 Estrutura do Excel Gerado

### Aba 1: Acionamento CCM-1A (130 linhas)
| Col | Nome | Descrição |
|-----|------|-----------|
| 1 | NOMENCLATURA | Código do equipamento |
| 2 | TIPO | Tipo de acionamento |
| 3 | DESCRICAO | Descrição do equipamento |
| 4 | CARTAO | Cartão de I/O |
| 5 | ANILHA-CARTAO | Anilha do cartão |
| 6 | ANIHA-RELE | Anilha do relé |
| 7 | RELE | Número do relé |
| 8 | CAVALO | Cavalo de bornes |
| 9 | BORNE | Borne de conexão |
| 10 | CABEAMENTO | Informação de cabeamento |
| 11 | FUSÍVEL | Tipo de fusível |

### Aba 2: Reconhecimento CCM-1A (177 linhas)
| Col | Nome | Descrição |
|-----|------|-----------|
| 1 | NOMENCLATURA | Código do sensor |
| 2 | TIPO | Tipo de sensor |
| 3 | DESCRIÇÃO | Descrição do sensor |
| 4 | CARTÃO | Cartão de entrada |
| 5 | ANILHA-CARTÃO | Anilha do cartão |
| 6 | BORNE | Borne de conexão |
| 7 | FUSÍVEL | Tipo de fusível |

### Aba 3: Descrição de Projeto CCM-1A (61 itens)
| Col | Nome | Descrição |
|-----|------|-----------|
| 1 | NOMENCLATURA | Código/Item |
| 2 | PAGINA REFERENCIA | Página do diagrama |

Itens especiais:
- CAPA (página 1)
- E-VISAO (página 2)
- I-VISAO (página 3)
- P-NOMENCLATURA (página 4)
- COMANDO-1 (página 20)
- ... (até 61 itens)

### Aba 4: Informações Especiais CCM-1A (7 campos)
```
local: Borborema - SP
cliente: Zanchetta
nomeprojeto: Blancheamento 10.02.2025
desenhado: Leonardo
data: 15/01/2026
conferido: André Luiz
projeto_pagina: Sistema de Acionamento - Painel Centro de Controle de Motores - CCM-1A
```

---

## 🔧 Personalização

### Adicionar Novo Padrão

1. **Descobrir padrão** - Você tem arquivo HB e arquivo de referência
2. **Adicionar em patterns.yaml:**
```yaml
MEU-NOVO-PADRAO:
  ativa: true
  confianca: 100
  linhas: 5
```

3. **Sistema automaticamente** - Detecta e aplica no próximo run

### Desabilitar Padrão
```yaml
DESP-2:
  ativa: false  # Desativado
```

### Mudar Modo de Aprendizado
```yaml
modo: "agressivo"  # Mais expansões
```

---

## 📈 Estatísticas

### Arquivo Gerado
- **Acionamentos:** 130 registros
- **Status:** 177 registros
- **Nomenclaturas:** 61 mapeadas
- **Equipamentos:** 45 com acionamentos

### Qualidade
- **Fidelidade:** 92.9% com arquivo de referência
- **Erros de validação:** 0
- **Compatibilidade C#:** 100%

---

## 🐛 Troubleshooting

### "Arquivo não encontrado"
```bash
# Verificar caminho relativo ou absoluto
python main.py "C:\caminho\completo\arquivo.xlsx"
```

### "Erro ao ler arquivo HB"
- Verificar se arquivo é .xlsx válido
- Verificar se primeira coluna é "NOMENCLATURA"

### "Acionamentos não expandidos"
- Verificar `config/patterns.yaml`
- Verificar se pattern tem `ativa: true`
- Aumentar `modo` em `aprendizado_config.yaml`

### "Integração C# com erros"
- Verificar nomes de abas (devem incluir "CCM-1A")
- Verificar número de colunas (11 para Acionamento, 7 para Reconhecimento)
- Executar `validador_completo.py` para debug

---

## 📚 Exemplos

### Exemplo 1: Converter simples
```bash
python main.py "HB - Zanchetta - Blancheamento 10.02.2025.xlsx"
```
Resultado: `Painel_FINAL_COMPATIVEL.xlsx` com 307 linhas (130 acionamento + 177 status)

### Exemplo 2: Validar resultado
```bash
python validador_completo.py
```
Resultado: Relatório completo de compatibilidade

### Exemplo 3: Com arquivo customizado
```bash
python main.py "input.xlsx" -o "painel_ccm1a.xlsx"
```
Resultado: `painel_ccm1a.xlsx`

---

## 🎓 Como Funciona Internamente

### Passo 1: Leitura (hb_parser.py)
```python
df = pd.read_excel(arquivo)
# Extrai: NOMENCLATURA, TIPO, DESCRICAO, CARTAO, etc
```

### Passo 2: Transformação (transformers.py)
```python
# Limpa dados, padroniza formatos
data = transform_data(df)
```

### Passo 3: Expansão (main.py + sistema_adaptativo.py)
```python
# Aplica padrões aprendidos
# DESP-1 → 12 linhas
# DESP-2 → 5 linhas
# ... etc
expanded = expand_based_on_patterns(data)
```

### Passo 4: Geração Excel (excel_generator.py)
```python
# Cria 4 abas com estrutura exata
wb = create_workbook()
add_acionamento_sheet()
add_reconhecimento_sheet()
add_descricao_sheet()
add_info_especiais_sheet()
```

---

## 🚀 Performance

- **Tempo de execução:** ~5 segundos
- **Uso de memória:** ~50MB
- **Arquivo de entrada:** Até 10MB
- **Arquivo de saída:** ~2MB

---

## 📞 Suporte

Ficheiros principais para investigação:
- `main.py` - Lógica principal
- `config/patterns.yaml` - Padrões
- `INTEGRACAO_COMPLETA.md` - Detalhes C#
- `validador_completo.py` - Debug

---

## ✅ Checklist de Antes de Usar

- [ ] Python 3.13+ instalado
- [ ] `pip install -r requirements.txt` executado
- [ ] Arquivo HB disponível em .xlsx
- [ ] config/patterns.yaml personalizado (opcional)
- [ ] Espaço em disco para saída (~10MB)

---

**Versão:** 1.0  
**Última atualização:** 15/01/2026
