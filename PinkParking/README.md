# 🌸 Vagas Rosa — Sistema de Gestão de Estacionamento Feminino

> Sistema desktop para gerenciamento de vagas exclusivas para mulheres, desenvolvido em Python com interface gráfica moderna e banco de dados local.

---

## 📸 Visão Geral

O **Vagas Rosa** é uma aplicação desktop completa para estacionamentos que oferecem vagas preferenciais femininas. Ele permite registrar entradas e saídas de veículos, calcular valores automaticamente com base no tempo de permanência, e gerar relatórios em PDF.

---

## ✨ Funcionalidades

- **Registro de Entrada** — cadastro de placa, modelo do veículo, nome da cliente e contato de emergência
- **Gestão do Pátio** — visualização em tempo real de todos os veículos presentes
- **Registro de Saída** — cálculo automático do tempo e valor a pagar (R$ 15,00/hora)
- **Histórico Completo** — todas as movimentações com status (Ativo / Finalizado)
- **Faturamento Acumulado** — total arrecadado exibido em tempo real
- **Exportação em PDF** — relatório completo com layout formatado (requer `reportlab`) ou PDF simples como fallback
- **Banco de dados local** — armazenamento em SQLite, sem necessidade de servidor

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| Python 3.x | Linguagem principal |
| Tkinter + ttk | Interface gráfica |
| SQLite3 | Banco de dados local |
| ReportLab *(opcional)* | Exportação de PDF com layout |

---

## 🚀 Como Executar

### Pré-requisitos

- [Python 3.8+](https://www.python.org/downloads/) instalado
- Marcar a opção **"Add Python to PATH"** durante a instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/vagas-rosa.git
cd vagas-rosa
```

### 2. (Opcional) Instale dependências para PDF com layout

```bash
pip install -r requirements.txt
```

> Sem o `reportlab`, o sistema ainda funciona normalmente e gera PDFs em formato simplificado.

### 3. Execute o sistema

**Windows — via arquivo batch:**
```
executar.bat
```

**Qualquer sistema — via terminal:**
```bash
python estacionamento_rosa.py
```

---

## 📁 Estrutura do Projeto

```
vagas-rosa/
├── estacionamento_rosa.py   # Código-fonte principal
├── executar.bat             # Atalho de execução para Windows
├── requirements.txt         # Dependências opcionais
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Este arquivo
```

> O arquivo `estacionamento_rosa.db` é gerado automaticamente na primeira execução e **não é versionado** (está no `.gitignore`).

---

## 💰 Tabela de Tarifas

| Cobrança | Valor |
|---|---|
| Tarifa por hora | R$ 15,00 |
| Mínimo cobrado | 1 minuto |
| Cálculo | Proporcional ao tempo de permanência |

---

## 🖥️ Interface

O sistema é organizado em três abas:

1. **🚗 Entrada** — formulário para registrar a chegada de um veículo
2. **🅿 Gestão do Pátio** — lista de veículos ativos com opção de registrar saída
3. **📋 Relatórios** — histórico completo, faturamento total e exportação em PDF

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

<p align="center">Feito com 🌸 para a segurança e conforto das mulheres</p>
