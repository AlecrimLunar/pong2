import pygame
import sys
import random
import os

# ==========================================
# CONSTANTES DE CONFIGURAÇÃO
# ==========================================
LARGURA = 800
ALTURA = 600
TITULO = "Pong Clone"
FPS = 60

# Cores fixas do sistema
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA_FUNDO = (20, 20, 24)
CINZA_CARD = (32, 32, 40)
CINZA_BORDA = (65, 65, 80)
CINZA_TEXTO = (170, 170, 180)
AMARELO = (255, 220, 50)
VERDE_DESTAQUE = (50, 220, 100)

# Cores Pré-definidas para Customização
CORES_PRESET = [
    ("Branco", (255, 255, 255)),
    ("Azul", (15, 2, 191)),        # #0f02bf
    ("Verde", (11, 186, 2)),       # #0bba02
    ("Vermelho", (204, 16, 2)),    # #cc1002
    ("Amarelo", (209, 192, 2)),    # #d1c002
    ("Roxo", (112, 2, 181)),       # #7002b5
    ("Rosa", (168, 0, 157)),       # #a8009d
    ("Laranja", (201, 125, 2)),    # #c97d02
    ("Cinza", (120, 120, 120)),    # #787878
]

# Dimensões dos elementos de jogo
LARGURA_PALETE = 15
ALTURA_PALETE = 90
VEL_PALETE = 6
VEL_IA = 4.5  # Limite de velocidade da IA para não ser invencível

TAMANHO_BOLA = 15
VEL_INICIAL_BOLA = 5


class Particula:
    """Partículas quadradas retrô para efeito de impacto e faíscas."""
    def __init__(self, x, y, vel_x, vel_y, tamanho, cor, vida_maxima):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.tamanho = tamanho
        self.cor = cor
        self.vida = vida_maxima
        self.vida_maxima = vida_maxima

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= 0.92  # Desaceleração suave no ar
        self.vel_y *= 0.92
        self.vida -= 1
        return self.vida > 0

    def desenhar(self, tela):
        fator = max(0.0, self.vida / self.vida_maxima)
        tam = max(1, int(self.tamanho * (0.4 + 0.6 * fator)))
        cor_fade = (
            int(self.cor[0] * fator),
            int(self.cor[1] * fator),
            int(self.cor[2] * fator)
        )
        pygame.draw.rect(tela, cor_fade, (int(self.x - tam // 2), int(self.y - tam // 2), tam, tam))


class Botao:
    """Classe para renderização e interação com botões no Pygame."""
    def __init__(self, rect, texto, id_acao=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.id_acao = id_acao
        self.hover = False
        self.ativo = False

    def checar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)
        return self.hover

    def foi_clicado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)

    def desenhar(self, tela, fonte, cor_fundo=None, cor_borda=None, cor_texto=None):
        bg = cor_fundo if cor_fundo else (CINZA_CARD if (self.hover or self.ativo) else (15, 15, 20))
        borda = cor_borda if cor_borda else (AMARELO if self.ativo else (BRANCO if self.hover else CINZA_BORDA))
        txt_cor = cor_texto if cor_texto else (AMARELO if (self.hover or self.ativo) else BRANCO)

        pygame.draw.rect(tela, bg, self.rect, border_radius=8)
        pygame.draw.rect(tela, borda, self.rect, width=2, border_radius=8)

        surface_txt = fonte.render(self.texto, True, txt_cor)
        rect_txt = surface_txt.get_rect(center=self.rect.center)
        tela.blit(surface_txt, rect_txt)


class PartidaFundo:
    """Simulação autônoma de Pong para rodar no fundo dos menus com estilo retrô CRT."""
    def __init__(self):
        self.largura = LARGURA
        self.altura = ALTURA

        # Paletes de fundo
        self.palete_esq = pygame.Rect(20, (ALTURA - 90) // 2, 14, 90)
        self.palete_dir = pygame.Rect(LARGURA - 34, (ALTURA - 90) // 2, 14, 90)
        self.vel_ia = 4.3

        # Bola de fundo (quadrada retrô)
        self.tamanho_bola = 14
        self.bola = pygame.Rect((LARGURA - self.tamanho_bola) // 2, (ALTURA - self.tamanho_bola) // 2, self.tamanho_bola, self.tamanho_bola)
        self.vel_x = 0
        self.vel_y = 0
        self.rastro = []
        self.max_rastro = 7
        self.particulas = []
        self.reiniciar_bola()

        # Placar de fundo
        self.pontos_esq = 0
        self.pontos_dir = 0
        self.delay_ponto = 0

        # Superfície de Scanlines CRT retrô
        self.surf_scanlines = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for y in range(0, ALTURA, 3):
            pygame.draw.line(self.surf_scanlines, (0, 0, 0, 75), (0, y), (LARGURA, y), 1)

        # Superfície de escurecimento suave para os menus da frente terem leitura perfeita
        self.surf_overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.surf_overlay.fill((8, 8, 12, 180))

    def criar_impacto(self, x, y, dir_x, dir_y, cor, qtd=8):
        for _ in range(qtd):
            vx = dir_x * random.uniform(1.5, 3.8) + random.uniform(-1.5, 1.5)
            vy = dir_y * random.uniform(1.5, 3.8) + random.uniform(-1.5, 1.5)
            self.particulas.append(Particula(x, y, vx, vy, random.randint(2, 4), cor, random.randint(10, 18)))

    def reiniciar_bola(self):
        self.bola.center = (self.largura // 2, self.altura // 2)
        dir_x = random.choice([-1, 1])
        dir_y = random.choice([-0.75, -0.4, 0.4, 0.75])
        vel = 5.2
        self.vel_x = dir_x * vel
        self.vel_y = dir_y * vel
        self.rastro.clear()
        self.particulas.clear()

    def atualizar(self):
        # Atualizar partículas do fundo
        self.particulas = [p for p in self.particulas if p.atualizar()]

        if self.delay_ponto > 0:
            self.delay_ponto -= 1
            if self.delay_ponto == 0:
                self.reiniciar_bola()
            return

        # Registrar rastro de movimento (efeito ghosting de fósforo CRT)
        self.rastro.append(self.bola.center)
        if len(self.rastro) > self.max_rastro:
            self.rastro.pop(0)

        # Movimento inteligente da palete esquerda no fundo
        if self.vel_x < 0:
            alvo = self.bola.centery
            diff = alvo - self.palete_esq.centery
            if abs(diff) > 8:
                self.palete_esq.y += int(min(self.vel_ia, diff) if diff > 0 else max(-self.vel_ia, diff))
        else:
            diff_centro = (self.altura // 2) - self.palete_esq.centery
            if abs(diff_centro) > 12:
                self.palete_esq.y += int(min(2.0, diff_centro) if diff_centro > 0 else max(-2.0, diff_centro))

        # Movimento inteligente da palete direita no fundo
        if self.vel_x > 0:
            alvo = self.bola.centery
            diff = alvo - self.palete_dir.centery
            if abs(diff) > 8:
                self.palete_dir.y += int(min(self.vel_ia, diff) if diff > 0 else max(-self.vel_ia, diff))
        else:
            diff_centro = (self.altura // 2) - self.palete_dir.centery
            if abs(diff_centro) > 12:
                self.palete_dir.y += int(min(2.0, diff_centro) if diff_centro > 0 else max(-2.0, diff_centro))

        # Limitar dentro da tela
        self.palete_esq.top = max(0, min(self.altura - self.palete_esq.height, self.palete_esq.top))
        self.palete_dir.top = max(0, min(self.altura - self.palete_dir.height, self.palete_dir.top))

        # Mover a bola
        self.bola.x += int(self.vel_x)
        self.bola.y += int(self.vel_y)

        # Colisões com as bordas
        if self.bola.top <= 0:
            self.bola.top = 0
            self.vel_y *= -1
            self.criar_impacto(self.bola.centerx, self.bola.top, 0, 1, (200, 200, 200), qtd=6)
        elif self.bola.bottom >= self.altura:
            self.bola.bottom = self.altura
            self.vel_y *= -1
            self.criar_impacto(self.bola.centerx, self.bola.bottom, 0, -1, (200, 200, 200), qtd=6)

        # Colisão com paletes
        if self.bola.colliderect(self.palete_esq) and self.vel_x < 0:
            self.bola.left = self.palete_esq.right
            self.vel_x = -self.vel_x * 1.03
            offset = (self.bola.centery - self.palete_esq.centery) / (self.palete_esq.height / 2)
            self.vel_y = offset * abs(self.vel_x)
            self.criar_impacto(self.palete_esq.right, self.bola.centery, 1, 0, (220, 220, 220), qtd=8)

        if self.bola.colliderect(self.palete_dir) and self.vel_x > 0:
            self.bola.right = self.palete_dir.left
            self.vel_x = -self.vel_x * 1.03
            offset = (self.bola.centery - self.palete_dir.centery) / (self.palete_dir.height / 2)
            self.vel_y = offset * abs(self.vel_x)
            self.criar_impacto(self.palete_dir.left, self.bola.centery, -1, 0, (220, 220, 220), qtd=8)

        # Limite de velocidade no fundo para jogadas fluidas e visíveis
        self.vel_x = max(-9, min(9, self.vel_x))
        self.vel_y = max(-9, min(9, self.vel_y))

        # Pontuação
        if self.bola.left <= 0:
            self.pontos_dir += 1
            self.delay_ponto = 20
        elif self.bola.right >= self.largura:
            self.pontos_esq += 1
            self.delay_ponto = 20

    def desenhar(self, tela, cor_barras, cor_bola, cor_rede, fonte_placar):
        # Linha pontilhada retrô no centro
        passo = 15
        for y in range(0, self.altura, passo * 2):
            pygame.draw.rect(tela, cor_rede, (self.largura // 2 - 2, y, 4, passo))

        # Placar retrô de fundo
        placar_cor = (max(20, cor_barras[0] // 2), max(20, cor_barras[1] // 2), max(20, cor_barras[2] // 2))
        txt_esq = fonte_placar.render(str(self.pontos_esq), True, placar_cor)
        txt_dir = fonte_placar.render(str(self.pontos_dir), True, placar_cor)
        tela.blit(txt_esq, (self.largura // 4 - txt_esq.get_width() // 2, 25))
        tela.blit(txt_dir, (3 * self.largura // 4 - txt_dir.get_width() // 2, 25))

        # Paletes de fundo
        pygame.draw.rect(tela, cor_barras, self.palete_esq)
        pygame.draw.rect(tela, cor_barras, self.palete_dir)

        # Partículas de impacto no fundo
        for p in self.particulas:
            p.desenhar(tela)

        # Rastro fantasma de fósforo retrô da bola
        qtd = len(self.rastro)
        for i, pos in enumerate(self.rastro):
            fator = (i + 1) / (qtd + 1)
            tam = max(4, int(self.tamanho_bola * (0.35 + 0.65 * fator)))
            cor_rastro = (
                int(cor_bola[0] * fator * 0.7),
                int(cor_bola[1] * fator * 0.7),
                int(cor_bola[2] * fator * 0.7)
            )
            rect_r = pygame.Rect(0, 0, tam, tam)
            rect_r.center = pos
            pygame.draw.rect(tela, cor_rastro, rect_r)

        # Bola quadrada retrô no fundo
        pygame.draw.rect(tela, cor_bola, self.bola)

        # Escurecimento suave para os botões do menu ficarem perfeitamente legíveis
        tela.blit(self.surf_overlay, (0, 0))

        # Scanlines CRT retrô
        tela.blit(self.surf_scanlines, (0, 0))


class PongGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()

        # Fontes do sistema (tamanhos ajustados para perfeita diagramação na tela)
        self.fonte_titulo = pygame.font.SysFont("consolas", 56, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("consolas", 28, bold=True)
        self.fonte_botao = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_aba = pygame.font.SysFont("consolas", 20, bold=True)
        self.fonte_texto = pygame.font.SysFont("consolas", 16)
        self.fonte_contador = pygame.font.SysFont("consolas", 84, bold=True)
        self.fonte_placar = pygame.font.SysFont("consolas", 48, bold=True)

        # Estados: SPLASH, MENU_PRINCIPAL, MENU_JOGAR, MENU_OPCOES, MENU_COMO_JOGAR, JOGANDO
        self.estado = "SPLASH"

        # Cores Customizáveis (Branco por padrão)
        self.cor_barras = (255, 255, 255)
        self.cor_bola = (255, 255, 255)
        self.cor_rede = (255, 255, 255)

        # Elemento selecionado no menu de opções: 'barras', 'bola', 'rede'
        self.elemento_opcao = "barras"

        # Mensagem temporária (usada no aviso do modo 1 jogador)
        self.mensagem_aviso = ""
        self.tempo_aviso = 0

        # Configurações do jogo Pong
        self.palete_esq = pygame.Rect(30, (ALTURA - ALTURA_PALETE) // 2, LARGURA_PALETE, ALTURA_PALETE)
        self.palete_dir = pygame.Rect(LARGURA - 30 - LARGURA_PALETE, (ALTURA - ALTURA_PALETE) // 2, LARGURA_PALETE, ALTURA_PALETE)
        self.bola = pygame.Rect((LARGURA - TAMANHO_BOLA) // 2, (ALTURA - TAMANHO_BOLA) // 2, TAMANHO_BOLA, TAMANHO_BOLA)
        self.vel_bola_x = 0
        self.vel_bola_y = 0
        self.pontos_esq = 0
        self.pontos_dir = 0

        # Modo de jogo: 1 (1 Jogador vs IA), 2 (2 Jogadores)
        self.modo_jogo = 1

        # Partida autônoma em segundo plano e rastros retrô
        self.partida_fundo = PartidaFundo()
        self.rastro_bola_jogo = []

        # Partículas retrô e tremor de tela (Screen Shake)
        self.particulas = []
        self.tempo_tremida = 0
        self.intensidade_tremida = 0
        self.shake_x = 0
        self.shake_y = 0
        self.superficie_jogo = pygame.Surface((LARGURA, ALTURA))

        # Imprevisibilidade da IA (offset dinâmico do ponto de rebatida)
        self.ia_offset_alvo = 0
        self.sortear_estrategia_ia()

        # Controle da contagem regressiva de 3 segundos (início de partida)
        self.em_contagem = False
        self.tempo_inicio_contagem = 0
        self.segundos_restantes = 3

        # Controle da contagem regressiva de 2 segundos (após cada ponto marcado)
        self.em_contagem_ponto = False
        self.tempo_inicio_ponto = 0
        self.segundos_restantes_ponto = 2

        # Sistema de Áudio e Controle de Volume
        self.volume = 0.7  # 70% de volume inicial
        self.arrastando_volume = False
        self.carregar_sons()
        self.tocar_musica_menu()

        # Inicializar botões e interface dos menus
        self.criar_botoes()

    # ==========================================
    # SISTEMA DE ÁUDIO
    # ==========================================
    def carregar_sons(self):
        """Carrega todos os efeitos sonoros e músicas da pasta Sons/ com tratamento de exceções."""
        self.audio_disponivel = False
        self.som_botao = None
        self.som_impacto = None
        self.som_contagem_3s = None
        self.caminho_musica_menu = None
        self.caminho_musica_partida = None
        self.musica_atual = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.audio_disponivel = True
        except Exception as e:
            print(f"Aviso: Não foi possível inicializar o subsistema de áudio: {e}")
            return

        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_sons = os.path.join(diretorio_atual, "Sons")

        def carregar_efeito(arquivo):
            caminho = os.path.join(caminho_sons, arquivo)
            if os.path.exists(caminho):
                try:
                    snd = pygame.mixer.Sound(caminho)
                    snd.set_volume(self.volume)
                    return snd
                except Exception as e:
                    print(f"Erro ao carregar efeito {arquivo}: {e}")
            return None

        self.som_botao = carregar_efeito("button_sound.mp3")
        self.som_impacto = carregar_efeito("ball_hit.mp3")
        self.som_contagem_3s = carregar_efeito("3_seg_sound.mp3")

        c_menu = os.path.join(caminho_sons, "menu_sound.mp3")
        if os.path.exists(c_menu):
            self.caminho_musica_menu = c_menu

        c_partida = os.path.join(caminho_sons, "partida_sound.mp3")
        if os.path.exists(c_partida):
            self.caminho_musica_partida = c_partida

    def aplicar_volume(self, novo_volume):
        """Atualiza e aplica o volume geral para músicas e efeitos sonoros."""
        self.volume = max(0.0, min(1.0, round(novo_volume, 2)))
        if self.audio_disponivel:
            try:
                pygame.mixer.music.set_volume(self.volume)
                if self.som_botao:
                    self.som_botao.set_volume(self.volume)
                if self.som_impacto:
                    self.som_impacto.set_volume(self.volume)
                if self.som_contagem_3s:
                    self.som_contagem_3s.set_volume(self.volume)
            except Exception:
                pass

    def tocar_som(self, som):
        """Reproduz um efeito sonoro caso o áudio esteja ativo."""
        if self.audio_disponivel and som:
            try:
                som.play()
            except Exception:
                pass

    def tocar_musica_menu(self):
        """Toca a trilha sonora dos menus em loop contínuo."""
        if not self.audio_disponivel or not self.caminho_musica_menu:
            return
        if self.musica_atual == "menu":
            return
        try:
            pygame.mixer.music.load(self.caminho_musica_menu)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
            self.musica_atual = "menu"
        except Exception as e:
            print(f"Erro ao reproduzir música do menu: {e}")

    def tocar_musica_partida(self):
        """Toca a trilha sonora da partida em loop contínuo."""
        if not self.audio_disponivel or not self.caminho_musica_partida:
            return
        if self.musica_atual == "partida":
            return
        try:
            pygame.mixer.music.load(self.caminho_musica_partida)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
            self.musica_atual = "partida"
        except Exception as e:
            print(f"Erro ao reproduzir música da partida: {e}")

    def parar_musica(self):
        """Interrompe a reprodução da música atual."""
        if self.audio_disponivel:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.musica_atual = None

    # ==========================================
    # BOTÕES E INTERFACE
    # ==========================================
    def criar_botoes(self):
        # Botões do Menu Principal
        largura_btn = 300
        altura_btn = 50
        x_btn = (LARGURA - largura_btn) // 2
        self.botoes_menu_principal = [
            Botao((x_btn, 210, largura_btn, altura_btn), "1 - Jogar", "jogar"),
            Botao((x_btn, 275, largura_btn, altura_btn), "2 - Opções", "opcoes"),
            Botao((x_btn, 340, largura_btn, altura_btn), "3 - Como Jogar", "como_jogar"),
            Botao((x_btn, 405, largura_btn, altura_btn), "4 - Sair", "sair"),
        ]

        # Botões do Menu Jogar
        self.botoes_menu_jogar = [
            Botao((x_btn, 230, largura_btn, altura_btn), "1 - 1 Jogador", "1_jogador"),
            Botao((x_btn, 300, largura_btn, altura_btn), "2 - 2 Jogadores", "2_jogadores"),
            Botao((x_btn, 385, largura_btn, altura_btn), "ESC - Voltar", "voltar"),
        ]

        # Botões de Abas no Menu de Opções (largura aumentada para 220px para não cortar '3 - Rede Central')
        largura_aba = 220
        altura_aba = 38
        espaco_aba = 15
        x_aba_base = (LARGURA - (3 * largura_aba + 2 * espaco_aba)) // 2
        self.botoes_abas_opcoes = [
            Botao((x_aba_base, 98, largura_aba, altura_aba), "1 - Barras", "barras"),
            Botao((x_aba_base + largura_aba + espaco_aba, 98, largura_aba, altura_aba), "2 - Bolinha", "bola"),
            Botao((x_aba_base + 2 * (largura_aba + espaco_aba), 98, largura_aba, altura_aba), "3 - Rede Central", "rede"),
        ]

        # Botões das Cores Pré-setadas (3 colunas x 3 linhas)
        self.botoes_cores = []
        colunas = 3
        largura_cor = 180
        altura_cor = 32
        espaco_x = 20
        espaco_y = 6
        x_base_cor = (LARGURA - (colunas * largura_cor + (colunas - 1) * espaco_x)) // 2
        y_base_cor = 146

        for idx, (nome, cor_rgb) in enumerate(CORES_PRESET):
            col = idx % colunas
            lin = idx // colunas
            x = x_base_cor + col * (largura_cor + espaco_x)
            y = y_base_cor + lin * (altura_cor + espaco_y)
            self.botoes_cores.append({
                "rect": pygame.Rect(x, y, largura_cor, altura_cor),
                "nome": nome,
                "cor": cor_rgb,
                "idx": idx
            })

        # Controles de Volume no Menu de Opções
        x_centro = LARGURA // 2
        self.btn_vol_menos = Botao((x_centro - 160, 425, 42, 32), "-", "vol_menos")
        self.rect_barra_volume = pygame.Rect(x_centro - 105, 432, 210, 18)
        self.btn_vol_mais = Botao((x_centro + 118, 425, 42, 32), "+", "vol_mais")

        # Botões Voltar para Opções e Como Jogar
        self.btn_voltar_opcoes = Botao(((LARGURA - 200) // 2, 520, 200, 40), "ESC - Voltar", "voltar")
        self.btn_voltar_como_jogar = Botao(((LARGURA - 200) // 2, 525, 200, 42), "ESC - Voltar", "voltar")

    def sortear_estrategia_ia(self):
        """Define onde na palete a IA tentará rebater a bola para criar ângulos variados e imprevisíveis."""
        opcoes = [-32, -24, -14, 0, 14, 24, 32]
        self.ia_offset_alvo = random.choice(opcoes) + random.uniform(-4, 4)

    def ativar_tremida(self, intensidade=4, duracao=6):
        """Ativa a leve tremida de impacto na tela."""
        self.intensidade_tremida = intensidade
        self.tempo_tremida = duracao

    def criar_impacto(self, x, y, dir_x, dir_y, cor, qtd=12, shake_intensidade=4, shake_duracao=6):
        """Gera partículas quadradas de impacto no ar, aciona a tremida de tela e toca o som de impacto."""
        self.tocar_som(self.som_impacto)
        self.ativar_tremida(shake_intensidade, shake_duracao)
        for _ in range(qtd):
            vx = dir_x * random.uniform(2.0, 5.0) + random.uniform(-1.8, 1.8)
            vy = dir_y * random.uniform(2.0, 5.0) + random.uniform(-1.8, 1.8)
            tam = random.randint(3, 5)
            vida = random.randint(12, 22)
            self.particulas.append(Particula(x, y, vx, vy, tam, cor, vida))

    def reiniciar_bola(self):
        """Reinicia a bola no centro da quadra com direção aleatória."""
        self.bola.center = (LARGURA // 2, ALTURA // 2)
        direcao_x = random.choice([-1, 1])
        direcao_y = random.choice([-0.7, -0.4, 0.4, 0.7])
        self.vel_bola_x = direcao_x * VEL_INICIAL_BOLA
        self.vel_bola_y = direcao_y * VEL_INICIAL_BOLA
        self.rastro_bola_jogo = []
        self.particulas.clear()
        self.sortear_estrategia_ia()

    def iniciar_contagem_ponto(self):
        """Inicia a pausa e contagem regressiva de 2 segundos após um ponto marcado."""
        self.em_contagem_ponto = True
        self.tempo_inicio_ponto = pygame.time.get_ticks()
        self.segundos_restantes_ponto = 2
        self.bola.center = (LARGURA // 2, ALTURA // 2)
        self.vel_bola_x = 0
        self.vel_bola_y = 0
        self.rastro_bola_jogo.clear()
        self.particulas.clear()

    def iniciar_partida(self, modo=1):
        """Prepara o início da partida para 1 ou 2 jogadores com contagem regressiva de 3s."""
        self.modo_jogo = modo
        self.pontos_esq = 0
        self.pontos_dir = 0
        self.palete_esq.centery = ALTURA // 2
        self.palete_dir.centery = ALTURA // 2
        self.bola.center = (LARGURA // 2, ALTURA // 2)
        self.vel_bola_x = 0
        self.vel_bola_y = 0
        self.em_contagem = True
        self.tempo_inicio_contagem = pygame.time.get_ticks()
        self.segundos_restantes = 3
        self.em_contagem_ponto = False
        self.rastro_bola_jogo = []
        self.particulas.clear()
        self.sortear_estrategia_ia()
        self.estado = "JOGANDO"

        # Áudio: interrompe a música do menu e aciona a contagem regressiva de 3 segundos
        self.parar_musica()
        self.tocar_som(self.som_contagem_3s)

    def atualizar_ia(self):
        """Controla a palete direita com limites de velocidade, ângulos imprevisíveis e comportamento humanoide."""
        if self.vel_bola_x > 0:
            ponto_alvo_palete = self.palete_dir.centery + self.ia_offset_alvo
            diferenca = self.bola.centery - ponto_alvo_palete

            if abs(diferenca) > 8:
                if diferenca > 0:
                    movimento = min(VEL_IA, diferenca)
                    self.palete_dir.y += int(movimento)
                else:
                    movimento = max(-VEL_IA, diferenca)
                    self.palete_dir.y += int(movimento)
        else:
            centro_quadra = ALTURA // 2
            diferenca = centro_quadra - self.palete_dir.centery
            if abs(diferenca) > 15:
                vel_retorno = 2.5
                if diferenca > 0:
                    self.palete_dir.y += int(min(vel_retorno, diferenca))
                else:
                    self.palete_dir.y += int(max(-vel_retorno, diferenca))

        if self.palete_dir.top < 0:
            self.palete_dir.top = 0
        elif self.palete_dir.bottom > ALTURA:
            self.palete_dir.bottom = ALTURA

    def definir_cor_elemento(self, cor_rgb):
        """Aplica a cor selecionada ao elemento ativo nas opções."""
        if self.elemento_opcao == "barras":
            self.cor_barras = cor_rgb
        elif self.elemento_opcao == "bola":
            self.cor_bola = cor_rgb
        elif self.elemento_opcao == "rede":
            self.cor_rede = cor_rgb

    def cor_atual_elemento(self):
        """Retorna a cor atual do elemento ativo nas opções."""
        if self.elemento_opcao == "barras":
            return self.cor_barras
        elif self.elemento_opcao == "bola":
            return self.cor_bola
        elif self.elemento_opcao == "rede":
            return self.cor_rede
        return BRANCO

    # ==========================================
    # PROCESSAMENTO DE EVENTOS
    # ==========================================
    def processar_eventos(self):
        pos_mouse = pygame.mouse.get_pos()

        # Atualizar hover dos botões relevantes para o estado atual
        if self.estado == "MENU_PRINCIPAL":
            for btn in self.botoes_menu_principal:
                btn.checar_hover(pos_mouse)
        elif self.estado == "MENU_JOGAR":
            for btn in self.botoes_menu_jogar:
                btn.checar_hover(pos_mouse)
        elif self.estado == "MENU_OPCOES":
            for btn in self.botoes_abas_opcoes:
                btn.checar_hover(pos_mouse)
                btn.ativo = (btn.id_acao == self.elemento_opcao)
            self.btn_vol_menos.checar_hover(pos_mouse)
            self.btn_vol_mais.checar_hover(pos_mouse)
            self.btn_voltar_opcoes.checar_hover(pos_mouse)
        elif self.estado == "MENU_COMO_JOGAR":
            self.btn_voltar_como_jogar.checar_hover(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            # --- TELA INICIAL (SPLASH) ---
            if self.estado == "SPLASH":
                if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                    self.tocar_som(self.som_botao)
                    self.estado = "MENU_PRINCIPAL"

            # --- MENU PRINCIPAL ---
            elif self.estado == "MENU_PRINCIPAL":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for btn in self.botoes_menu_principal:
                        if btn.foi_clicado(pos_mouse):
                            self.tocar_som(self.som_botao)
                            if btn.id_acao == "jogar":
                                self.estado = "MENU_JOGAR"
                            elif btn.id_acao == "opcoes":
                                self.estado = "MENU_OPCOES"
                            elif btn.id_acao == "como_jogar":
                                self.estado = "MENU_COMO_JOGAR"
                            elif btn.id_acao == "sair":
                                return False

                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_1, pygame.K_KP1):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_JOGAR"
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_OPCOES"
                    elif evento.key in (pygame.K_3, pygame.K_KP3):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_COMO_JOGAR"
                    elif evento.key in (pygame.K_4, pygame.K_KP4, pygame.K_ESCAPE):
                        self.tocar_som(self.som_botao)
                        return False

            # --- MENU JOGAR ---
            elif self.estado == "MENU_JOGAR":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for btn in self.botoes_menu_jogar:
                        if btn.foi_clicado(pos_mouse):
                            self.tocar_som(self.som_botao)
                            if btn.id_acao == "1_jogador":
                                self.iniciar_partida(1)
                            elif btn.id_acao == "2_jogadores":
                                self.iniciar_partida(2)
                            elif btn.id_acao == "voltar":
                                self.estado = "MENU_PRINCIPAL"

                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_1, pygame.K_KP1):
                        self.tocar_som(self.som_botao)
                        self.iniciar_partida(1)
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        self.tocar_som(self.som_botao)
                        self.iniciar_partida(2)
                    elif evento.key == pygame.K_ESCAPE:
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"

            # --- MENU OPÇÕES ---
            elif self.estado == "MENU_OPCOES":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    # Checar abas
                    for btn in self.botoes_abas_opcoes:
                        if btn.foi_clicado(pos_mouse):
                            self.tocar_som(self.som_botao)
                            self.elemento_opcao = btn.id_acao

                    # Checar botões de cores
                    for btn_cor in self.botoes_cores:
                        if btn_cor["rect"].collidepoint(pos_mouse):
                            self.tocar_som(self.som_botao)
                            self.definir_cor_elemento(btn_cor["cor"])

                    # Checar botões e barra de volume
                    if self.btn_vol_menos.foi_clicado(pos_mouse):
                        self.aplicar_volume(self.volume - 0.05)
                        self.tocar_som(self.som_botao)
                    elif self.btn_vol_mais.foi_clicado(pos_mouse):
                        self.aplicar_volume(self.volume + 0.05)
                        self.tocar_som(self.som_botao)
                    elif self.rect_barra_volume.collidepoint(pos_mouse):
                        self.arrastando_volume = True
                        novo_vol = (pos_mouse[0] - self.rect_barra_volume.x) / self.rect_barra_volume.width
                        self.aplicar_volume(novo_vol)
                        self.tocar_som(self.som_botao)

                    # Checar botão voltar
                    if self.btn_voltar_opcoes.foi_clicado(pos_mouse):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"

                elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                    self.arrastando_volume = False

                elif evento.type == pygame.MOUSEMOTION and self.arrastando_volume:
                    novo_vol = (pos_mouse[0] - self.rect_barra_volume.x) / self.rect_barra_volume.width
                    self.aplicar_volume(novo_vol)

                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_1, pygame.K_KP1):
                        self.tocar_som(self.som_botao)
                        self.elemento_opcao = "barras"
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        self.tocar_som(self.som_botao)
                        self.elemento_opcao = "bola"
                    elif evento.key in (pygame.K_3, pygame.K_KP3):
                        self.tocar_som(self.som_botao)
                        self.elemento_opcao = "rede"
                    elif evento.key in (pygame.K_LEFT, pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.aplicar_volume(self.volume - 0.05)
                        self.tocar_som(self.som_botao)
                    elif evento.key in (pygame.K_RIGHT, pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.aplicar_volume(self.volume + 0.05)
                        self.tocar_som(self.som_botao)
                    elif evento.key == pygame.K_ESCAPE:
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"

            # --- MENU COMO JOGAR ---
            elif self.estado == "MENU_COMO_JOGAR":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.btn_voltar_como_jogar.foi_clicado(pos_mouse):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"

            # --- JOGANDO ---
            elif self.estado == "JOGANDO":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.tocar_som(self.som_botao)
                        self.parar_musica()
                        self.tocar_musica_menu()
                        self.estado = "MENU_PRINCIPAL"
                    elif evento.key == pygame.K_r:
                        self.tocar_som(self.som_botao)
                        self.iniciar_partida(self.modo_jogo)

        return True

    # ==========================================
    # LÓGICA DO JOGO (ATUALIZAÇÃO)
    # ==========================================
    def atualizar(self):
        if self.estado != "JOGANDO":
            self.partida_fundo.atualizar()
            return

        teclas = pygame.key.get_pressed()

        # Jogador 1 (Humano - W / S)
        if teclas[pygame.K_w] and self.palete_esq.top > 0:
            self.palete_esq.y -= VEL_PALETE
        if teclas[pygame.K_s] and self.palete_esq.bottom < ALTURA:
            self.palete_esq.y += VEL_PALETE

        # Lado Direito: Jogador 2 humano ou IA
        if self.modo_jogo == 2:
            if teclas[pygame.K_UP] and self.palete_dir.top > 0:
                self.palete_dir.y -= VEL_PALETE
            if teclas[pygame.K_DOWN] and self.palete_dir.bottom < ALTURA:
                self.palete_dir.y += VEL_PALETE
        else:
            # Modo 1 Jogador: IA defende com velocidade limitada
            self.atualizar_ia()

        # Lógica da Contagem Regressiva de 3 segundos (Início de partida)
        if self.em_contagem:
            decorrido_ms = pygame.time.get_ticks() - self.tempo_inicio_contagem
            segundos_passados = decorrido_ms / 1000.0
            if segundos_passados < 3.0:
                self.segundos_restantes = 3 - int(segundos_passados)
                return  # A bola NÃO se move durante a contagem
            else:
                self.em_contagem = False
                self.reiniciar_bola()
                self.tocar_musica_partida()

        # Lógica da Contagem Regressiva de 2 segundos (Após cada ponto marcado)
        if self.em_contagem_ponto:
            decorrido_ms = pygame.time.get_ticks() - self.tempo_inicio_ponto
            segundos_passados = decorrido_ms / 1000.0
            if segundos_passados < 2.0:
                self.segundos_restantes_ponto = 2 - int(segundos_passados)
                return  # A bola NÃO se move durante a contagem
            else:
                self.em_contagem_ponto = False
                self.reiniciar_bola()

        # Registrar rastro de movimento retrô da bola
        self.rastro_bola_jogo.append(self.bola.center)
        if len(self.rastro_bola_jogo) > 6:
            self.rastro_bola_jogo.pop(0)

        # Atualizar partículas de impacto
        self.particulas = [p for p in self.particulas if p.atualizar()]

        # Atualizar tremor de tela (Screen Shake)
        if self.tempo_tremida > 0:
            self.tempo_tremida -= 1
            self.shake_x = random.randint(-self.intensidade_tremida, self.intensidade_tremida)
            self.shake_y = random.randint(-self.intensidade_tremida, self.intensidade_tremida)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Movimento da bola
        self.bola.x += int(self.vel_bola_x)
        self.bola.y += int(self.vel_bola_y)

        # Colisão com o teto e chão
        if self.bola.top <= 0:
            self.bola.top = 0
            self.vel_bola_y *= -1
            self.criar_impacto(self.bola.centerx, self.bola.top, 0, 1, self.cor_bola, qtd=10, shake_intensidade=3, shake_duracao=5)
        elif self.bola.bottom >= ALTURA:
            self.bola.bottom = ALTURA
            self.vel_bola_y *= -1
            self.criar_impacto(self.bola.centerx, self.bola.bottom, 0, -1, self.cor_bola, qtd=10, shake_intensidade=3, shake_duracao=5)

        # Colisão com palete esquerda (ambas usam cor_barras)
        if self.bola.colliderect(self.palete_esq) and self.vel_bola_x < 0:
            self.bola.left = self.palete_esq.right
            self.vel_bola_x = -self.vel_bola_x * 1.05
            offset = (self.bola.centery - self.palete_esq.centery) / (ALTURA_PALETE / 2)
            self.vel_bola_y = offset * abs(self.vel_bola_x)
            self.sortear_estrategia_ia()
            self.criar_impacto(self.palete_esq.right, self.bola.centery, 1, 0, self.cor_barras, qtd=14, shake_intensidade=4, shake_duracao=6)

        # Colisão com palete direita
        if self.bola.colliderect(self.palete_dir) and self.vel_bola_x > 0:
            self.bola.right = self.palete_dir.left
            self.vel_bola_x = -self.vel_bola_x * 1.05
            offset = (self.bola.centery - self.palete_dir.centery) / (ALTURA_PALETE / 2)
            self.vel_bola_y = offset * abs(self.vel_bola_x)
            self.criar_impacto(self.palete_dir.left, self.bola.centery, -1, 0, self.cor_barras, qtd=14, shake_intensidade=4, shake_duracao=6)

        # Limitar velocidade máxima para estabilidade física
        vel_maxima = 14
        self.vel_bola_x = max(-vel_maxima, min(vel_maxima, self.vel_bola_x))
        self.vel_bola_y = max(-vel_maxima, min(vel_maxima, self.vel_bola_y))

        # Pontuação: aciona contagem regressiva de 2 segundos para o próximo saque
        if self.bola.left <= 0:
            self.pontos_dir += 1
            self.iniciar_contagem_ponto()
        elif self.bola.right >= LARGURA:
            self.pontos_esq += 1
            self.iniciar_contagem_ponto()

    # ==========================================
    # RENDERIZAÇÃO
    # ==========================================
    def desenhar(self):
        self.tela.fill(PRETO)

        # Partida animada retrô rolando no fundo de todos os menus
        if self.estado != "JOGANDO":
            self.partida_fundo.desenhar(self.tela, self.cor_barras, self.cor_bola, self.cor_rede, self.fonte_placar)

        if self.estado == "SPLASH":
            self.desenhar_splash()
        elif self.estado == "MENU_PRINCIPAL":
            self.desenhar_menu_principal()
        elif self.estado == "MENU_JOGAR":
            self.desenhar_menu_jogar()
        elif self.estado == "MENU_OPCOES":
            self.desenhar_menu_opcoes()
        elif self.estado == "MENU_COMO_JOGAR":
            self.desenhar_como_jogar()
        elif self.estado == "JOGANDO":
            self.desenhar_jogo()

        pygame.display.flip()

    def desenhar_splash(self):
        """Tela inicial com 'Pong Clone' em destaque e aviso de apertar tecla."""
        rect_card = pygame.Rect(LARGURA // 2 - 270, ALTURA // 2 - 110, 540, 220)
        pygame.draw.rect(self.tela, (12, 12, 18), rect_card, border_radius=12)
        pygame.draw.rect(self.tela, BRANCO, rect_card, width=2, border_radius=12)

        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        rect_titulo = titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 45))
        self.tela.blit(titulo, rect_titulo)

        piscar = (pygame.time.get_ticks() // 500) % 2 == 0
        if piscar:
            texto = self.fonte_subtitulo.render("Aperte qualquer tecla para iniciar", True, AMARELO)
            rect_texto = texto.get_rect(center=(LARGURA // 2, ALTURA // 2 + 35))
            self.tela.blit(texto, rect_texto)

        dica = self.fonte_texto.render("Pressione qualquer tecla ou clique para continuar", True, CINZA_TEXTO)
        self.tela.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA - 40)))

    def desenhar_menu_principal(self):
        """Menu principal com título 'Pong Clone' persistente e opções 1 a 4."""
        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        rect_titulo = titulo.get_rect(center=(LARGURA // 2, 100))
        self.tela.blit(titulo, rect_titulo)

        sub = self.fonte_texto.render("SELECIONE UMA OPÇÃO:", True, CINZA_TEXTO)
        self.tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 160)))

        for btn in self.botoes_menu_principal:
            btn.desenhar(self.tela, self.fonte_botao)

        dica = self.fonte_texto.render("Dica: Use o mouse ou os números [1, 2, 3, 4] no teclado", True, CINZA_TEXTO)
        self.tela.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA - 40)))

    def desenhar_menu_jogar(self):
        """Submenu de seleção de modo de jogo."""
        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 90)))

        sub = self.fonte_subtitulo.render("MODO DE JOGO", True, AMARELO)
        self.tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 165)))

        for btn in self.botoes_menu_jogar:
            btn.desenhar(self.tela, self.fonte_botao)

        if self.mensagem_aviso and (pygame.time.get_ticks() - self.tempo_aviso < 3500):
            aviso = self.fonte_texto.render(self.mensagem_aviso, True, AMARELO)
            rect_aviso = aviso.get_rect(center=(LARGURA // 2, 470))
            pygame.draw.rect(self.tela, (40, 35, 10), rect_aviso.inflate(24, 14), border_radius=6)
            pygame.draw.rect(self.tela, AMARELO, rect_aviso.inflate(24, 14), width=1, border_radius=6)
            self.tela.blit(aviso, rect_aviso)

    def desenhar_menu_opcoes(self):
        """Menu de customização de cores e controle de volume."""
        titulo = self.fonte_subtitulo.render("OPÇÕES E PERSONALIZAÇÃO", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 35)))

        desc = self.fonte_texto.render("Escolha o elemento e selecione uma cor pré-definida:", True, CINZA_TEXTO)
        self.tela.blit(desc, desc.get_rect(center=(LARGURA // 2, 68)))

        # Abas dos elementos
        for btn in self.botoes_abas_opcoes:
            btn.desenhar(self.tela, self.fonte_aba)

        # Botões de cores pré-setadas
        pos_mouse = pygame.mouse.get_pos()
        cor_atual = self.cor_atual_elemento()

        for btn_cor in self.botoes_cores:
            rect = btn_cor["rect"]
            hover = rect.collidepoint(pos_mouse)
            selecionada = (btn_cor["cor"] == cor_atual)

            # Fundo do botão da cor
            bg_cor = CINZA_CARD if hover or selecionada else (18, 18, 22)
            borda_cor = AMARELO if selecionada else (BRANCO if hover else CINZA_BORDA)
            pygame.draw.rect(self.tela, bg_cor, rect, border_radius=6)
            pygame.draw.rect(self.tela, borda_cor, rect, width=2 if selecionada else 1, border_radius=6)

            # Amostra da cor (quadradinho preenchido)
            swatch_rect = pygame.Rect(rect.x + 8, rect.y + 6, 20, 20)
            pygame.draw.rect(self.tela, btn_cor["cor"], swatch_rect, border_radius=4)
            pygame.draw.rect(self.tela, BRANCO if btn_cor["cor"] == PRETO else CINZA_BORDA, swatch_rect, width=1, border_radius=4)

            # Nome da cor
            txt_surface = self.fonte_texto.render(btn_cor["nome"], True, AMARELO if selecionada else BRANCO)
            self.tela.blit(txt_surface, (rect.x + 36, rect.y + 6))

        # --- Mini Prévia em tempo real ---
        rect_preview = pygame.Rect(210, 258, 380, 120)
        pygame.draw.rect(self.tela, (10, 10, 15), rect_preview, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_preview, width=2, border_radius=8)

        lbl_preview = self.fonte_texto.render("Prévia em Tempo Real", True, CINZA_TEXTO)
        self.tela.blit(lbl_preview, (rect_preview.centerx - lbl_preview.get_width() // 2, rect_preview.y + 5))

        # Linha pontilhada no preview (cor da rede)
        for y in range(rect_preview.y + 26, rect_preview.bottom - 6, 14):
            pygame.draw.rect(self.tela, self.cor_rede, (rect_preview.centerx - 1, y, 3, 7))

        # Paletes do preview (cor das barras)
        pygame.draw.rect(self.tela, self.cor_barras, (rect_preview.x + 18, rect_preview.centery - 24, 7, 48), border_radius=2)
        pygame.draw.rect(self.tela, self.cor_barras, (rect_preview.right - 25, rect_preview.centery - 24, 7, 48), border_radius=2)

        # Bolinha do preview (cor da bola)
        pygame.draw.rect(self.tela, self.cor_bola, (rect_preview.centerx - 5, rect_preview.centery - 5, 10, 10))

        # --- Seção de Controle de Volume ---
        pct_volume = int(round(self.volume * 100))
        lbl_vol = self.fonte_texto.render(f"VOLUME DO JOGO: {pct_volume}%", True, AMARELO)
        self.tela.blit(lbl_vol, (LARGURA // 2 - lbl_vol.get_width() // 2, 396))

        # Botão [-]
        self.btn_vol_menos.desenhar(self.tela, self.fonte_botao)

        # Barra de volume
        pygame.draw.rect(self.tela, (14, 14, 18), self.rect_barra_volume, border_radius=6)
        largura_preenchida = int(self.rect_barra_volume.width * self.volume)
        if largura_preenchida > 0:
            rect_preenchido = pygame.Rect(self.rect_barra_volume.x, self.rect_barra_volume.y, largura_preenchida, self.rect_barra_volume.height)
            pygame.draw.rect(self.tela, AMARELO, rect_preenchido, border_radius=6)
        pygame.draw.rect(self.tela, CINZA_BORDA, self.rect_barra_volume, width=2, border_radius=6)

        # Indicador / Knob do volume
        knob_x = self.rect_barra_volume.x + largura_preenchida
        knob_rect = pygame.Rect(knob_x - 4, self.rect_barra_volume.y - 3, 8, self.rect_barra_volume.height + 6)
        pygame.draw.rect(self.tela, BRANCO, knob_rect, border_radius=3)

        # Botão [+]
        self.btn_vol_mais.desenhar(self.tela, self.fonte_botao)

        # Dica de volume
        dica_vol = self.fonte_texto.render("Ajuste com [-] / [+] ou Setas Esquerda/Direita", True, CINZA_TEXTO)
        self.tela.blit(dica_vol, (LARGURA // 2 - dica_vol.get_width() // 2, 468))

        # Botão Voltar
        self.btn_voltar_opcoes.desenhar(self.tela, self.fonte_botao)

    def desenhar_como_jogar(self):
        """Tela de instruções e regras do Pong formatada perfeitamente no enquadramento."""
        titulo = self.fonte_subtitulo.render("COMO JOGAR & REGRAS", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 40)))

        # Card de Controles
        rect_card1 = pygame.Rect(60, 75, 680, 180)
        pygame.draw.rect(self.tela, CINZA_CARD, rect_card1, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_card1, width=1, border_radius=8)

        tit1 = self.fonte_botao.render("CONTROLES", True, AMARELO)
        self.tela.blit(tit1, (rect_card1.x + 22, rect_card1.y + 12))

        linhas_controles = [
            "• Modo 1 Jogador   : Você (W / S) contra a IA balanceada",
            "• Modo 2 Jogadores : Jogador 1 (W / S) vs Jogador 2 (Setas)",
            "• Tecla [ R ]      : Reiniciar a partida imediatamente",
            "• Tecla [ ESC ]    : Retornar ao menu principal",
        ]
        y_c1 = rect_card1.y + 46
        for linha in linhas_controles:
            txt = self.fonte_texto.render(linha, True, BRANCO)
            self.tela.blit(txt, (rect_card1.x + 22, y_c1))
            y_c1 += 30

        # Card de Regras
        rect_card2 = pygame.Rect(60, 270, 680, 235)
        pygame.draw.rect(self.tela, CINZA_CARD, rect_card2, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_card2, width=1, border_radius=8)

        tit2 = self.fonte_botao.render("REGRAS DO PONG", True, AMARELO)
        self.tela.blit(tit2, (rect_card2.x + 22, rect_card2.y + 12))

        linhas_regras = [
            "1. Controle sua palete e não deixe a bola passar da defesa.",
            "2. Cada bola que ultrapassar o rival rende 1 ponto.",
            "3. A cada ponto marcado, há 2s de pausa para a próxima bola.",
            "4. A velocidade da bola aumenta a cada rebatida na palete.",
            "5. O ângulo do rebote varia com o local de impacto na palete.",
            "6. A CPU possui velocidade justa: vença com reflexo e ângulo!",
        ]
        y_c2 = rect_card2.y + 44
        for linha in linhas_regras:
            txt = self.fonte_texto.render(linha, True, BRANCO)
            self.tela.blit(txt, (rect_card2.x + 22, y_c2))
            y_c2 += 29

        # Botão Voltar
        self.btn_voltar_como_jogar.desenhar(self.tela, self.fonte_botao)

    def desenhar_jogo(self):
        """Renderiza a quadra de jogo com cores customizadas, partículas e leve tremida de tela."""
        self.superficie_jogo.fill(PRETO)

        # Rede pontilhada central (com a cor customizada da rede)
        passo = 15
        for y in range(0, ALTURA, passo * 2):
            pygame.draw.rect(self.superficie_jogo, self.cor_rede, (LARGURA // 2 - 2, y, 4, passo))

        # Paletes (ambas compartilham a mesma cor customizada)
        pygame.draw.rect(self.superficie_jogo, self.cor_barras, self.palete_esq)
        pygame.draw.rect(self.superficie_jogo, self.cor_barras, self.palete_dir)

        # Partículas de impacto no ar
        for p in self.particulas:
            p.desenhar(self.superficie_jogo)

        # Rastro retrô da bola (fantasma / efeito fósforo CRT)
        qtd = len(self.rastro_bola_jogo)
        for i, pos in enumerate(self.rastro_bola_jogo):
            fator = (i + 1) / (qtd + 1)
            tam = max(4, int(TAMANHO_BOLA * (0.35 + 0.65 * fator)))
            cor_fantasma = (
                int(self.cor_bola[0] * fator * 0.75),
                int(self.cor_bola[1] * fator * 0.75),
                int(self.cor_bola[2] * fator * 0.75)
            )
            rect_fantasma = pygame.Rect(0, 0, tam, tam)
            rect_fantasma.center = pos
            pygame.draw.rect(self.superficie_jogo, cor_fantasma, rect_fantasma)

        # Bolinha quadrada clássica retrô
        pygame.draw.rect(self.superficie_jogo, self.cor_bola, self.bola)

        # Placar numérico
        texto_esq = self.fonte_placar.render(str(self.pontos_esq), True, BRANCO)
        texto_dir = self.fonte_placar.render(str(self.pontos_dir), True, BRANCO)
        self.superficie_jogo.blit(texto_esq, (LARGURA // 4 - texto_esq.get_width() // 2, 25))
        self.superficie_jogo.blit(texto_dir, (3 * LARGURA // 4 - texto_dir.get_width() // 2, 25))

        # Rótulos dos jogadores no placar
        nome_esq = "JOGADOR 1" if self.modo_jogo == 2 else "VOCÊ"
        nome_dir = "JOGADOR 2" if self.modo_jogo == 2 else "CPU (IA)"
        lbl_esq = self.fonte_texto.render(nome_esq, True, CINZA_TEXTO)
        lbl_dir = self.fonte_texto.render(nome_dir, True, CINZA_TEXTO)
        self.superficie_jogo.blit(lbl_esq, (LARGURA // 4 - lbl_esq.get_width() // 2, 75))
        self.superficie_jogo.blit(lbl_dir, (3 * LARGURA // 4 - lbl_dir.get_width() // 2, 75))

        # Contador de 3 segundos na tela antes de iniciar a partida
        if self.em_contagem:
            rect_box = pygame.Rect(LARGURA // 2 - 120, ALTURA // 2 - 90, 240, 180)
            pygame.draw.rect(self.superficie_jogo, (18, 18, 24), rect_box, border_radius=12)
            pygame.draw.rect(self.superficie_jogo, AMARELO, rect_box, width=3, border_radius=12)

            txt_cont = self.fonte_contador.render(str(self.segundos_restantes), True, AMARELO)
            rect_cont = txt_cont.get_rect(center=(LARGURA // 2, ALTURA // 2 - 15))
            self.superficie_jogo.blit(txt_cont, rect_cont)

            txt_prep = self.fonte_texto.render("PREPAREM-SE!", True, BRANCO)
            rect_prep = txt_prep.get_rect(center=(LARGURA // 2, ALTURA // 2 + 55))
            self.superficie_jogo.blit(txt_prep, rect_prep)

        # Contador de 2 segundos após marcação de ponto
        elif self.em_contagem_ponto:
            rect_box = pygame.Rect(LARGURA // 2 - 130, ALTURA // 2 - 90, 260, 180)
            pygame.draw.rect(self.superficie_jogo, (18, 18, 24), rect_box, border_radius=12)
            pygame.draw.rect(self.superficie_jogo, VERDE_DESTAQUE, rect_box, width=3, border_radius=12)

            txt_ponto = self.fonte_subtitulo.render("PONTO!", True, VERDE_DESTAQUE)
            rect_ponto = txt_ponto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
            self.superficie_jogo.blit(txt_ponto, rect_ponto)

            txt_cont = self.fonte_contador.render(str(self.segundos_restantes_ponto), True, AMARELO)
            rect_cont = txt_cont.get_rect(center=(LARGURA // 2, ALTURA // 2 + 5))
            self.superficie_jogo.blit(txt_cont, rect_cont)

            txt_prox = self.fonte_texto.render("Próxima bola em...", True, BRANCO)
            rect_prox = txt_prox.get_rect(center=(LARGURA // 2, ALTURA // 2 + 60))
            self.superficie_jogo.blit(txt_prox, rect_prox)

        # Scanlines CRT retrô sobre o jogo
        self.superficie_jogo.blit(self.partida_fundo.surf_scanlines, (0, 0))

        # Instruções no rodapé adaptadas ao modo
        if self.modo_jogo == 1:
            texto_rodape = "Você: W/S | Oponente: CPU (IA) | R: Reiniciar | ESC: Menu Principal"
        else:
            texto_rodape = "P1: W/S | P2: Setas | R: Reiniciar | ESC: Menu Principal"

        instrucoes = self.fonte_texto.render(texto_rodape, True, CINZA_TEXTO)
        self.superficie_jogo.blit(instrucoes, (LARGURA // 2 - instrucoes.get_width() // 2, ALTURA - 25))

        # Aplica a tremida na tela principal (Screen Shake)
        self.tela.blit(self.superficie_jogo, (self.shake_x, self.shake_y))

    # ==========================================
    # LOOP PRINCIPAL
    # ==========================================
    def executar(self):
        rodando = True
        while rodando:
            rodando = self.processar_eventos()
            self.atualizar()
            self.desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    jogo = PongGame()
    jogo.executar()
