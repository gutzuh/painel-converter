# 🎯 Sistema Adaptável v2.0 - Guia de Uso

## 📋 Visão Geral

O conversor HB → Painel CCM agora possui **aprendizado automático** que detecta padrões de qualquer arquivo de referência e os aplica automaticamente em conversões futuras.

---

## 🚀 Modo de Uso

### 1️⃣ **Conversão Básica (Sem Aprendizado)**
```bash
python main.py "HB.xlsx"
```
- Usa apenas os padrões manuais definidos em `config/patterns.yaml`
- Gera saída baseada 100% no arquivo HB de entrada

---

### 2️⃣ **Conversão com Aprendizado Automático**
```bash
python main.py "HB.xlsx" -r "Referencia.xlsx" -o "Saida.xlsx"
```

**O que acontece:**
1. Sistema analisa o arquivo de referência
2. Detecta automaticamente:
   - Transformações de nomenclatura (K-AT-1A → AT-1)
   - Padrões de ANILHA (1A-CT-X.Y → 1A-AT-X.Y)
   - Fórmulas de BORNE (x{19+N}A)
   - Regras de expansão (2 linhas → 4 linhas)
3. Aplica os padrões aprendidos na conversão
4. Salva padrões em `config/learned_patterns.yaml` para reutilização

---

### 3️⃣ **Apenas Aprender Padrões (Sem Converter)**
```bash
python main.py "HB.xlsx" -r "Referencia.xlsx" --learn-only
```

**Útil para:**
- Analisar um exemplo de referência
- Salvar padrões para usar em múltiplas conversões futuras
- Validar padrões antes de aplicar

---

### 4️⃣ **Usar Padrões Previamente Aprendidos**

Depois de executar o modo `--learn-only` uma vez:

```bash
python main.py "NovoHB.xlsx" -o "NovaSaida.xlsx"
```

O sistema automaticamente:
- Carrega `config/learned_patterns.yaml`
- Aplica os padrões aprendidos anteriormente
- **Funciona com qualquer HB novo!**

---

## 🧠 O Que o Sistema Aprende?

### ✅ Transformações de Nomenclatura
Detecta padrões como:
- `K-AT-1A` → `AT-1`
- `K-EL-5A` → `SENS-EL-5`
- `M-CA-1` → `CA-1`

**Como funciona:**
- Compara nomenclaturas no HB vs Referência
- Identifica prefixos/sufixos a remover
- Cria regras genéricas aplicáveis a qualquer número

### ✅ Padrões de ANILHA-CARTAO
Detecta transformações como:
- `1A-CT-1.12` → `1A-AT-1.1`
- `1A-CT-2.34` → `1A-AT-2.2`

**Regra aprendida:**
```yaml
pattern: "1A-CT-{N}.{S}"
transform: "1A-AT-{N}.{NEW_S}"
```

### ✅ Fórmulas de BORNE
Detecta progressões aritméticas:
- AT-1 → `x20A`
- AT-2 → `x21A`
- AT-3 → `x22A`

**Fórmula detectada:**
```
BORNE = x{19 + N}A
Onde N = número da nomenclatura
```

### ✅ Regras de Expansão
Detecta quando 1 linha HB vira N linhas no Painel:
- HB: 2 linhas (K-AT-1A, K-AT-1F)
- Painel: 4 linhas (K-AT-1A, K-AT-1F, AT-1, AT-1)

**Regra aprendida:**
```yaml
expansion_factor: 2
generates:
  - K-AT-{N}A (Contator)
  - K-AT-{N}F (Contator)
  - AT-{N} (Atuador) x2
```

---

## ⚙️ Configuração Adaptativa

### Arquivo: `config/patterns.yaml`

```yaml
# Modo de operação
mode:
  learning_mode: auto_learn  # ou 'manual'
  reference_file: null       # Opcional
  apply_learned_patterns: true

# Padrões adaptativos
adaptive_patterns:
  anilha_transforms:
    enabled: true
    rules:
      - pattern: "1A-CT-{N}.{S}"
        transform: "1A-AT-{N}.{S}"
  
  calculated_fields:
    BORNE:
      enabled: true
      formula: "x{19+N}{SUFFIX}"
      applies_to: ["AT-*"]
  
  expansion_rules:
    enabled: true
    rules:
      AT:
        from_hb_lines: 2
        to_panel_lines: 4
```

---

## 🔥 Teste de Fogo - Novo Projeto

### Cenário: Novo cliente com HB diferente

```bash
# Passo 1: Aprender do primeiro projeto (se houver referência)
python main.py "ProjetoA_HB.xlsx" -r "ProjetoA_Referencia.xlsx" --learn-only

# Passo 2: Converter novo projeto usando padrões aprendidos
python main.py "ProjetoB_HB.xlsx" -o "ProjetoB_Painel.xlsx"
```

**O sistema aplicará automaticamente:**
- ✅ Mesmas transformações de nomenclatura
- ✅ Mesmas fórmulas de ANILHA/BORNE
- ✅ Mesmas regras de expansão
- ✅ **Sem modificar código!**

---

## 📊 Validação e Debug

### Ver padrões aprendidos:
```bash
cat config/learned_patterns.yaml
```

### Comparar saída com referência:
```bash
python scripts/comparar_rapido.py
```

### Análise detalhada:
```bash
python scripts/resumo_diferencas.py
```

---

## 🎓 Vantagens do Sistema Adaptável

### ✅ **Genérico**
- Funciona com qualquer HB futuro
- Não precisa modificar código
- Padrões reutilizáveis

### ✅ **Automático**
- Detecta padrões sozinho
- Aplica transformações complexas
- Salva conhecimento para reutilizar

### ✅ **Transparente**
- Mostra o que aprendeu
- Padrões em YAML legível
- Fácil de validar e ajustar

### ✅ **Evolutivo**
- Aprende com cada novo projeto
- Melhora continuamente
- Acumula conhecimento

---

## 🛠️ Troubleshooting

### Problema: Padrões não sendo aplicados
**Solução:**
```bash
# Verificar configuração
cat config/patterns.yaml | grep "apply_learned_patterns"

# Deve estar: true
```

### Problema: Quero resetar aprendizado
**Solução:**
```bash
# Deletar padrões aprendidos
rm config/learned_patterns.yaml

# Aprender novamente
python main.py HB.xlsx -r Ref.xlsx --learn-only
```

### Problema: Padrões específicos não detectados
**Solução:**
1. Verificar arquivo de referência está correto
2. Executar scripts de análise para ver diferenças
3. Adicionar regra manual em `config/patterns.yaml`

---

## 📈 Próximos Passos

1. **Teste com novo projeto** - Validar adaptabilidade
2. **Refinar detecção** - Melhorar precisão
3. **Adicionar mais padrões** - Expansão de capabilities
4. **UI Web** - Interface gráfica para não-programadores

---

## 💡 Filosofia do Sistema

> **"Aprenda uma vez, use para sempre"**

O sistema não hardcoda regras específicas. Ele **observa exemplos reais** e extrai **padrões genéricos** aplicáveis a qualquer projeto futuro.

**Resultado:** Conversor que melhora sozinho e se adapta a diferentes clientes/projetos.

---

## 🤝 Contribuindo

Ao encontrar novos padrões em projetos:

1. Salvar HB original + Excel de referência
2. Executar: `python main.py HB.xlsx -r Ref.xlsx --learn-only`
3. Validar: `cat config/learned_patterns.yaml`
4. Compartilhar padrões aprendidos

O conhecimento acumulado beneficia todos os projetos futuros! 🚀
