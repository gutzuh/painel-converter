# Conversor HB → Painel CCM

Sistema automatizado para conversão de listas de I/O (formato HB) para diagramas de bornes (formato Painel CCM).

## 📋 Visão Geral

Este conversor transforma arquivos Excel no formato "HB - Lista de I/O" para o formato padronizado "Painel CCM", aplicando automaticamente:

- **Normalização de nomenclaturas** (remoção de prefixos, sufixos de direção)
- **Mapeamento de cartões I/O** (16 DO → 16-DO-P05)
- **Determinação de cabeamento** (baseado em CV e tabela de peças)
- **Atribuição de fusíveis** (baseado em potência)
- **Formatação profissional** do Excel de saída

## 🚀 Instalação

```bash
# Clonar/copiar o projeto
cd conversor_painel

# Instalar dependências
pip install -r requirements.txt
```

## 📖 Uso

### Uso Básico

```bash
python main.py "HB - Cliente - Projeto.xlsx"
```

### Com Arquivo de Saída Específico

```bash
python main.py input.xlsx -o "Painel_CCM_Final.xlsx"
```

### Com Informações do Projeto

```bash
python main.py input.xlsx \
    --cliente "Nome do Cliente" \
    --projeto "Nome do Projeto" \
    --local "Cidade - UF"
```

### Com Configuração Personalizada

```bash
python main.py input.xlsx -c config/patterns_custom.yaml
```

## 📁 Estrutura do Projeto

```
conversor_painel/
├── config/
│   └── patterns.yaml          # Configurações e padrões de mapeamento
├── src/
│   ├── parser/
│   │   └── hb_parser.py       # Parser do arquivo HB
│   ├── transformer/
│   │   └── transformers.py    # Transformadores de dados
│   ├── generator/
│   │   └── excel_generator.py # Gerador do Excel final
│   └── validator/
│       └── (validações)
├── main.py                    # Script principal
├── requirements.txt           # Dependências
└── README.md                  # Esta documentação
```

## ⚙️ Configuração (patterns.yaml)

O arquivo `config/patterns.yaml` contém todas as regras de mapeamento:

### Mapeamento de Nomenclaturas

```yaml
nomenclatura:
  remove_prefixes:
    - "K-"
    - "M-"
  
  specific_mappings:
    "CIC-1": "SS-CIC-1"      # Soft Starter
    "PC-1": "IF-PC-1"        # Inversor
```

### Mapeamento de Cartões

```yaml
cartao:
  mapping:
    "16 DO": "16-DO-P05"
    "20 DI PF": "20-DI-PF"
    "4 AI PTNI": "4-AI-PTNI"
```

### Tabela de Cabeamento

```yaml
cabeamento:
  por_cv:
    2.0: "Cabo PP 4x2,5mm²"
    5.5: "Cabo PP 4x2,5mm²"
    12.5: "Cabo PP 4x4mm²"
    25.0: "Cabo PP 4x10mm²"
```

### Fusíveis por Potência

```yaml
fusivel:
  por_cv:
    - cv_max: 2.0
      fusivel: "F1...F6"
    - cv_max: 5.5
      fusivel: "F7...F16"
```

## 📊 Formato de Entrada (HB)

O arquivo HB deve conter as seguintes abas:

| Aba | Descrição |
|-----|-----------|
| Acionamento 1A | Saídas digitais (DO) |
| Status 1A | Entradas digitais (DI) |
| Peças CCM 1A | Tabela de peças/cabos |
| Borne 1A | Mapa de bornes (opcional) |

### Colunas Esperadas

**Acionamento:**
- NOMENCLATURA
- DESCRIÇÃO
- CARTÃO
- ANILHA 1 / ANILHA 2
- RELE
- CV
- BORNE

**Status:**
- NOMENCLATURA
- DESCRIÇÃO
- CARTÃO
- ANILHA
- BORNE

## 📄 Formato de Saída (Painel CCM)

O arquivo gerado contém as abas:

1. **Descrição de Projeto CCM-1A** - Lista de nomenclaturas únicas
2. **Acionamento CCM-1A** - Tabela de acionamentos formatada
3. **Reconhecimento CCM-1A** - Tabela de status formatada
4. **Informações Especiais CCM-1A** - Metadados do projeto

### Exemplo de Saída (Acionamento)

| NOMENCLATURA | TIPO | DESCRICAO | CARTAO | ANILHA-CARTAO | RELE | CAVALO | CABEAMENTO | FUSÍVEL |
|--------------|------|-----------|--------|---------------|------|--------|------------|---------|
| SS-VA-1-CA1 | MOTOR | Ventilador Ar 1 | 16-DO-P05 | 1A-CT-1.1 | RL01 | 12.5 | Cabo PP 4x4mm² | F17...F26 |
| AT-1 | ATUADOR | Atuador Damper 1 | 16-DO-P05 | 1A-CT-2.1 | | | | F7...F16 |

## 🔄 Fluxo de Processamento

```
┌─────────────────┐
│   ARQUIVO HB    │
│   (Entrada)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    PARSING      │
│ • Detecta abas  │
│ • Identifica    │
│   cabeçalhos    │
│ • Extrai dados  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TRANSFORMAÇÃO   │
│ • Nomenclatura  │
│ • Cartão        │
│ • Cabeamento    │
│ • Fusível       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VALIDAÇÃO     │
│ • Campos obrig. │
│ • Consistência  │
│ • Relatório     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    GERAÇÃO      │
│ • Cria Excel    │
│ • Formata       │
│ • Salva         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PAINEL CCM     │
│   (Saída)       │
└─────────────────┘
```

## ✅ Validações Realizadas

O conversor verifica automaticamente:

- ⚠️ Motores sem CV definido
- ⚠️ CV sem cabo correspondente
- ⚠️ Cartão não identificado
- ❌ Descrição vazia (obrigatória)
- ❌ Nomenclatura duplicada com dados diferentes

## 📝 Relatório de Validação

Após cada conversão, um relatório é gerado:

```
============================================================
RELATÓRIO DE VALIDAÇÃO
============================================================

⚠️  AVISOS (3):
   • [Linha 15] Motor 'VA-3-CA1' sem CV definido
   • [Linha 23] 'AT-5' sem cartão identificado

ℹ️  INFORMAÇÕES (3):
   • Total de acionamentos: 45
   • Total de status: 32
   • Nomenclaturas únicas: 28

============================================================
```

## 🛠️ Personalização

### Adicionar Novo Mapeamento de Nomenclatura

Edite `config/patterns.yaml`:

```yaml
nomenclatura:
  specific_mappings:
    "MINHA-TAG": "NOVO-PREFIXO-MINHA-TAG"
```

### Adicionar Novo Tipo de Cartão

```yaml
cartao:
  mapping:
    "NOVO CARTÃO": "NOVO-CODIGO"
```

### Ajustar Tabela de Cabos

```yaml
cabeamento:
  por_cv:
    150.0: "Cabo PP 4x70mm²"  # Novo valor
```

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique o relatório de validação gerado
- Confirme que o arquivo de entrada segue o padrão HB
- Ajuste as configurações em `patterns.yaml` conforme necessário

---

**J.Cortiça Automação Industrial** | Versão 1.0 | 2025
