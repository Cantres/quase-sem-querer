# Quase Sem Querer

**Sistema de Apoio à Decisão para Composição de Custos e Formação de Preços**

---

## 1. Apresentação

O **Quase Sem Querer** é um sistema desenvolvido para **apoiar gestores públicos e equipes técnicas** na elaboração, análise e auditoria da **planilha de custos e formação de preços**, conforme a metodologia estabelecida pela Instrução Normativa nº 05/2017 (SEGES).

O sistema foi concebido para enfrentar dificuldades recorrentes na prática administrativa, tais como:

* dependência excessiva de planilhas manuais;
* dificuldade de rastrear fundamentos legais de cada valor;
* baixa reprodutibilidade de cálculos ao longo do tempo;
* esforço elevado para auditoria e reprocessamento de cenários.

O **Quase Sem Querer** não substitui o gestor público nem emite decisões jurídicas ou administrativas.
Seu papel é **formalizar o cálculo**, registrar decisões humanas e **produzir resultados auditáveis**, de forma transparente e reproduzível.

> **O sistema calcula; o gestor decide.**

---

## 2. Público-alvo

O sistema é direcionado principalmente a:

* gestores públicos responsáveis por contratações;
* fiscais e gestores de contratos administrativos;
* equipes de planejamento e orçamento;
* órgãos de controle interno;
* equipes técnicas de apoio à tomada de decisão.

Não é necessário conhecimento avançado de programação para utilização da interface principal.

---

## 3. Finalidade e benefícios

O sistema permite:

* estruturar cálculos conforme a metodologia da IN nº 05/2017;
* separar claramente **regras normativas**, **valores aplicados** e **resultados obtidos**;
* registrar decisões humanas inevitáveis (ex.: percentuais, bases de cálculo);
* gerar trilha completa de cálculo, célula a célula;
* reprocessar cenários de forma confiável;
* apoiar auditorias internas e externas com documentação consistente.

---

## 4. Requisitos técnicos

* Python **3.11** ou superior
* Sistema operacional compatível com Python (Windows, Linux ou macOS)

Dependências principais:

* `streamlit`
* `pandas`

---

## 5. Instalação

### 5.1 Obter o sistema

```bash
git clone <url-do-repositorio>
cd quase-sem-querer
```

### 5.2 Preparar o ambiente (recomendado)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 5.3 Instalar

```bash
pip install -e .
```

Esse procedimento registra o comando `qsk`, utilizado para iniciar a aplicação.

---

## 6. Utilização do sistema

### 6.1 Interface principal (Streamlit)

```bash
qsk
```

A aplicação será aberta no navegador, apresentando um **fluxo guiado de execução**, organizado em etapas:

1. **Seleção do modelo normativo**
   Define as regras de cálculo aplicáveis.

2. **Constantes legais**
   Permite selecionar valores dentro dos limites previstos em lei.

3. **Valores operacionais**
   Informações não definidas diretamente pela norma, como salários, benefícios e parâmetros contratuais.

4. **Consolidação e execução**
   Apresenta o contexto aplicado, executa o cálculo e gera o resultado final.

O fluxo é sequencial e impede execução sem que todas as decisões necessárias sejam explicitadas.

---

## 7. Fluxo de execução (visão simplificada)

O sistema possui **um único fluxo normativo de execução**, utilizado tanto pela interface gráfica quanto por chamadas técnicas.

1. Carregamento do modelo normativo
2. Carregamento do contexto de valores
3. Verificação estática do modelo
4. Avaliação da árvore de cálculo
5. Geração do resultado
6. Persistência opcional para auditoria

```
Usuário (UI ou CLI)
        ↓
   Orquestrador
        ↓
 Modelo + Contexto
        ↓
 Verificação Estática
        ↓
   Interpretação
        ↓
 Resultado Auditável
```

---

## 8. Visão geral da arquitetura

### 8.1 Princípios adotados

A arquitetura do sistema foi projetada com foco em:

* fidelidade normativa;
* transparência dos cálculos;
* rastreabilidade das decisões;
* separação entre cálculo e decisão humana;
* facilidade de auditoria.

---

### 8.2 Estrutura conceitual

O sistema trabalha com três artefatos distintos:

#### Modelo de Cálculo Normativo

Define **como calcular**.
É representado como uma árvore declarativa, contendo regras e fundamentos legais, sem valores numéricos.

#### Contexto de Valores

Define **quais valores são aplicados**.
Contém parâmetros, decisões humanas e referências documentais.

#### Resultado Canônico

Define **o que foi calculado**.
Inclui valores finais, intermediários e a trilha completa de cálculo, servindo como base para auditoria e memória de cálculo.

---

### 8.3 Componentes principais

* **Interfaces (Streamlit e CLI)**
  Coletam informações e acionam o fluxo de execução.

* **Carregadores**
  Leem e normalizam modelos e contextos.

* **Verificador Estático**
  Impede a execução de modelos inválidos.

* **Interpretador de Árvores Normativas**
  Executa o cálculo de forma determinística.

* **Persistência e Memória de Cálculo**
  Armazenam execuções e geram relatórios auditáveis.

---

## 9. Considerações finais

O **Quase Sem Querer** oferece uma abordagem estruturada e transparente para apoiar a composição de custos na administração pública, respeitando os limites legais e preservando a responsabilidade decisória do gestor.

O sistema não substitui o juízo humano, mas **qualifica a decisão**, fornecendo cálculos consistentes, documentados e auditáveis.
