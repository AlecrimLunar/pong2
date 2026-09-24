# Pong Clone (Pygame)

Uma recriação clássica do jogo **Pong** desenvolvida em Python utilizando a biblioteca **Pygame**.

---

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Git

---

## 🚀 Como Executar o Projeto

### 1. Clonar o repositório
```bash
git clone https://github.com/<seu-usuario>/<nome-do-repositorio>.git
cd andrei
```

### 2. Criar e ativar o ambiente virtual

**No Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**No Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> **Nota:** Caso o PowerShell bloqueie a execução de scripts ao ativar o venv, execute:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar o jogo
```bash
python main.py
```

---

## 🎮 Controles

- **Jogador 1 (Esquerda):** `W` (Cima) / `S` (Baixo)
- **Jogador 2 (Direita):** `Seta para Cima` / `Seta para Baixo`
- **Sair do jogo:** Tecla `ESC` ou fechar a janela

---

## 📁 Estrutura do Projeto

```text
├── .venv/               # Ambiente virtual Python (ignorado pelo git)
├── .gitignore           # Regras de exclusão do git
├── requirements.txt     # Dependências do projeto
├── README.md            # Documentação do projeto
└── main.py              # Ponto de entrada do jogo Pong
```
