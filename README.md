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
bash
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

- **Trilha Sonora e Efeitos de Áudio Completos (`Sons/`):**
  - `menu_sound.mp3`: Trilha sonora contínua em loop nos menus de seleção.
  - `partida_sound.mp3`: Trilha de gameplay durante as partidas.
  - `3_seg_sound.mp3`: Som narrativo de contagem regressiva de 3 segundos para início da partida.
  - `ball_hit.mp3`: Efeito sonoro retrô a cada rebatida da bola nas paletes e colisão com paredes.
  - `button_sound.mp3`: Som de feedback ao clicar em botões, abas ou navegar pelo teclado.
  - `yourself_point.mp3`: Som vibrante de gol para quando você marca ponto (Modo 1P) ou quando qualquer um dos jogadores pontua (Modo 2P).
  - `enemy_point.mp3`: Som de ponto sofrido quando a CPU marca um gol contra o jogador (Modo 1P).
- **Controle Interativo de Volume nas Opções:**
  - Slider interativo com porcentagem visual em tempo real (0% a 100%).
  - Ajustável via botões `[-]` e `[+]`, clique/arrasto direto do mouse na barra ou teclas de seta `[Esquerda]` / `[Direita]`.
  - Regula proporcionalmente tanto as músicas de fundo quanto todos os efeitos sonoros.
- **Contador de 2 Segundos Pós-Ponto:**
  - A cada gol/ponto marcado, a bola é reposicionada no centro e uma contagem de 2 segundos ("PONTO!") é exibida na tela antes de lançar o próximo saque, permitindo que os jogadores se reposicionem estrategicamente.
- **Contagem Regressiva de 3 Segundos no Início:**
  - Ao iniciar ou reiniciar uma partida com `R`, uma contagem de 3 segundos sincronizada com o áudio prepara os jogadores.
- **Partida de Fundo Retrô nos Menus:**
  - Enquanto navega por qualquer menu (Abertura, Principal, Jogar, Opções e Como Jogar), uma partida autônoma de Pong (IA vs IA) acontece em segundo plano, com paletes animadas rebatendo a bolinha e marcando pontos em tempo real.
- **Estética Retrô CRT & Impactos Dinâmicos:**
  - **Partículas Quadradas de Impacto:** A cada colisão da bola com as paredes superior/inferior ou com as paletes, pequenas partículas quadradas explodem na direção do impacto e se dissolvem suavemente no ar.
  - **Tremor de Tela (Screen Shake):** Leve tremor na tela a cada colisão que traz peso e sensação física aos lances.
  - **Scanlines:** Linhas horizontais sutis simulam monitores de tubo (CRT) e arcades clássicos dos anos 70/80.
  - **Rastro de Fósforo (Ghosting):** A bolinha deixa um rastro de persistência luminosa e movimento fluido.
  - **Pixel Art Clássico:** Bolinha quadrada clássica do Pong original e rede pontilhada retrô.
- **Tela de Abertura:** Moldura retrô com título "Pong Clone" em destaque e aviso interativo *"Aperte qualquer tecla para iniciar"*.
- **Menu Principal:**
  - `1 - Jogar`: Submenu com opções para:
    - **1 Jogador (vs IA):** Enfrente a CPU com inteligência artificial humanizada, **rebatidas imprevisíveis com ângulos variados** (a CPU varia propositalmente o ponto de contato na palete para lançar diagonais altas, baixas e retas) e limite de velocidade balanceado.
    - **2 Jogadores:** Partida clássica local para dois jogadores no mesmo teclado.
  - `2 - Opções`: Personalização de cores exclusivas para as **Barras** (ambas compartilham a mesma cor), **Bolinha** e **Rede Central**, prévia em tempo real e controle de volume geral do jogo.
  - `3 - Como Jogar`: Tela com os controles e regras detalhadas do jogo sem estouro de layout.
  - `4 - Sair`: Encerra o jogo.

---

## ⌨️ Controles

- **Navegação pelos Menus:** Mouse (cliques nos botões e cores) ou teclado (`1`, `2`, `3`, `4` e `ESC` para voltar).
- **Controle de Volume (Opções):** Teclas `Seta Esquerda` / `-` para diminuir, `Seta Direita` / `+` para aumentar, ou botões na tela.
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
├── main.py              # Ponto de entrada do jogo Pong e sistema de menus
└── Sons/                # Arquivos de áudio (efeitos sonoros e trilha sonora)
    ├── 3_seg_sound.mp3   # Áudio da contagem de 3 segundos
    ├── ball_hit.mp3      # Som de impacto da bolinha
    ├── button_sound.mp3  # Som de clique dos botões e menus
    ├── enemy_point.mp3   # Som de gol marcado pela CPU
    ├── menu_sound.mp3    # Música ambiente dos menus
    ├── partida_sound.mp3 # Trilha sonora durante as partidas
    └── yourself_point.mp3# Som de gol marcado por você ou pelos jogadores
```
