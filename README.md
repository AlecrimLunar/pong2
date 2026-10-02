# Pong Clone (Pygame-CE)

Uma recriação clássica, customizável e com modo campanha Roguelite Arcade do jogo **Pong**, desenvolvida em Python utilizando a biblioteca **Pygame-CE (Community Edition)**.

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

## 🎮 Menus e Modos de Jogo

- **Campanha Roguelite Arcade (1 Jogador vs CPU):**
  - **Sistema de Vidas (Corações):** Jogador e CPU começam com 3 corações. Cada gol sofrido consome 1 vida.
  - **Progressão Infinita de Adversários:** Ao zerar os corações da CPU, você avança imediatamente para o próximo adversário! O jogador recupera todos os corações perdidos e o novo adversário ganha +1 coração máximo, maior velocidade e rebatidas mais fortes.
  - **Layout Inteligente de Vidas da CPU:** Para adversários avançados com mais de 5 corações de vida (ex: Adversário 20 com 22 vidas), o layout simplifica automaticamente para `♥ x[quantidade]`, mantendo o visual limpo e legível.
  - **Mecânica Exclusiva de Combo (Jogador):**
    - A cada ponto feito pelo jogador, um temporizador é iniciado (20 segundos no Combo 1, diminuindo até 6 segundos no Combo 5).
    - A cada nível de combo, as rebatidas do jogador impulsionam a bola com mais velocidade.
    - Ao atingir o **Combo 5**, cada ponto marcado causa **2 de dano** na CPU!
    - Se o tempo do combo esgotar ou a CPU pontuar, o combo é zerado.
  - **Registro de Recordes Arcade (Game Over):** Ao perder todas as 3 vidas, registre seu recorde com **3 letras** como nas máquinas clássicas de fliperama dos anos 80.
- **Tabela de Ranque Persistente (Hall da Fama):**
  - Acessível diretamente pelo Menu Inicial (`2 - Recordes`) ou ao final de cada partida.
  - Salva em disco (`highscores.json`) os melhores recordes de adversário alcançado e combo máximo.
- **Modo 2 Jogadores:**
  - Disputa local clássica para dois jogadores no mesmo teclado com placar tradicional.
- **Efeito Visual Aquático de Ponto (Gota d'Água):**
  - Ao fazer ponto, ondas concêntricas retrô se propagam suavemente a partir do ponto de impacto na tela.
- **Trilha Sonora e Efeitos de Áudio Completos (`Sons/`):**
  - `menu_sound.mp3`: Trilha sonora contínua em loop nos menus de seleção.
  - `partida_sound.mp3`: Trilha de gameplay durante as partidas.
  - `3_seg_sound.mp3`: Contagem regressiva de 3 segundos para início da partida.
  - `ball_hit.mp3`: Efeito sonoro retrô a cada rebatida da bola nas paletes e colisão com paredes.
  - `button_sound.mp3`: Som de feedback ao clicar em botões, abas ou navegar pelo teclado.
  - `yourself_point.mp3`: Som vibrante de gol ao pontuar contra a CPU (1P) ou pelos jogadores (2P).
  - `enemy_point.mp3`: Som de ponto sofrido quando a CPU marca um gol (1P).
- **Controle Interativo de Volume nas Opções:**
  - Slider interativo com porcentagem visual em tempo real (0% a 100%), ajustável via mouse ou teclado (`-` e `+` / Setas).
- **Partida de Fundo Retrô nos Menus:**
  - Uma simulação autônoma de Pong (IA vs IA) acontece em segundo plano nos menus com scanlines CRT, partículas e rastros luminosos.

---

## ⌨️ Controles

- **Navegação pelos Menus:** Mouse ou teclas numéricas (`1`, `2`, `3`, `4`, `5` e `ESC` para voltar).
- **Registro de Iniciais no Arcade:** `Setas Cima / Baixo` ou `W / S` para mudar a letra, `Setas Esquerda / Direita` para trocar de slot e `ENTER` ou `ESPAÇO` para confirmar.
- **Jogador 1 / Você (Esquerda):** `W` (Cima) / `S` (Baixo)
- **Jogador 2 (Direita - Modo 2P):** `Seta para Cima` / `Seta para Baixo`
- **Controle de Volume (Opções):** Teclas `Seta Esquerda` / `-` para diminuir, `Seta Direita` / `+` para aumentar.
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
├── .venv/               # Ambiente virtual Python
├── .gitignore           # Regras de exclusão do git
├── highscores.json      # Dados persistentes da Tabela de Recordes Arcade
├── requirements.txt     # Dependências (pygame-ce)
├── README.md            # Documentação completa do projeto
├── main.py              # Ponto de entrada do jogo Pong, campanhas e menus
└── Sons/                # Arquivos de áudio (efeitos sonoros e trilha sonora)
    ├── 3_seg_sound.mp3   # Áudio da contagem de 3 segundos
    ├── ball_hit.mp3      # Som de impacto da bolinha
    ├── button_sound.mp3  # Som de clique dos botões e menus
    ├── enemy_point.mp3   # Som de gol marcado pela CPU
    ├── menu_sound.mp3    # Música ambiente dos menus
    ├── partida_sound.mp3 # Trilha sonora durante as partidas
    └── yourself_point.mp3# Som de gol marcado por você ou pelos jogadores
```
