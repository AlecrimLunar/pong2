# Pong Clone (Pygame)

Uma recriação clássica e customizável do jogo **Pong** desenvolvida em Python utilizando a biblioteca **Pygame**.

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

## 🎮 Menus e Funcionalidades

- **Tela de Abertura:** Nome "Pong Clone" em destaque com aviso interativo *"Aperte qualquer tecla para iniciar"*.
- **Menu Principal:**
  - `1 - Jogar`: Submenu com opções para:
    - **1 Jogador (vs IA):** Enfrente a CPU com inteligência artificial humanizada e limite de velocidade (balanceada para ser desafiadora, mas não invencível).
    - **2 Jogadores:** Partida clássica local para dois jogadores no mesmo teclado.
  - `2 - Opções`: Personalização de cores exclusivas para as **Barras** (ambas compartilham a mesma cor), **Bolinha** e **Rede Central**, com prévia em tempo real!
  - `3 - Como Jogar`: Tela com os controles e regras detalhadas do jogo.
  - `4 - Sair`: Encerra o jogo.
- **Contagem Regressiva de 3 Segundos:** Ao iniciar qualquer partida (1P ou 2P), um contador de 3 segundos aparece no centro para os jogadores se posicionarem antes da bola começar a se mover.

---

## ⌨️ Controles

- **Navegação pelos Menus:** Mouse (cliques nos botões e cores) ou teclado (`1`, `2`, `3`, `4` e `ESC` para voltar).
- **Jogador 1 / Você (Esquerda):** `W` (Cima) / `S` (Baixo)
- **Jogador 2 / CPU (Direita):** `Seta para Cima` / `Seta para Baixo` (no modo 2P) ou controlado pela IA (no modo 1P)
- **Reiniciar Partida:** Tecla `R`
- **Voltar ao Menu / Pausar:** Tecla `ESC`

---

## 🎨 Cores Disponíveis nas Opções

- Branco (Padrão)
- Azul (`#0f02bf`)
- Verde (`#0bba02`)
- Vermelho (`#cc1002`)
- Amarelo (`#d1c002`)
- Roxo (`#7002b5`)
- Rosa (`#a8009d`)
- Laranja (`#c97d02`)
- Cinza (`#787878`)

---

## 📁 Estrutura do Projeto

```text
├── .venv/               # Ambiente virtual Python (ignorado pelo git)
├── .gitignore           # Regras de exclusão do git
├── requirements.txt     # Dependências do projeto
├── README.md            # Documentação do projeto
└── main.py              # Ponto de entrada do jogo Pong e sistema de menus
```
