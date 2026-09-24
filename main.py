import pygame
import sys
import random

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


class PongGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()

        # Fontes do sistema
        self.fonte_titulo = pygame.font.SysFont("consolas", 56, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("consolas", 28, bold=True)
        self.fonte_botao = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_texto = pygame.font.SysFont("consolas", 17)
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

        # Controle da contagem regressiva de 3 segundos
        self.em_contagem = False
        self.tempo_inicio_contagem = 0
        self.segundos_restantes = 3

        # Inicializar botões de menus
        self.criar_botoes()

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

        # Botões de Abas no Menu de Opções
        largura_aba = 180
        altura_aba = 40
        espaco_aba = 20
        x_aba_base = (LARGURA - (3 * largura_aba + 2 * espaco_aba)) // 2
        self.botoes_abas_opcoes = [
            Botao((x_aba_base, 110, largura_aba, altura_aba), "1 - Barras", "barras"),
            Botao((x_aba_base + largura_aba + espaco_aba, 110, largura_aba, altura_aba), "2 - Bolinha", "bola"),
            Botao((x_aba_base + 2 * (largura_aba + espaco_aba), 110, largura_aba, altura_aba), "3 - Rede Central", "rede"),
        ]

        # Botões das Cores Pré-setadas (3 colunas x 3 linhas)
        self.botoes_cores = []
        colunas = 3
        largura_cor = 180
        altura_cor = 36
        espaco_x = 20
        espaco_y = 10
        x_base_cor = (LARGURA - (colunas * largura_cor + (colunas - 1) * espaco_x)) // 2
        y_base_cor = 175

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

        # Botão Voltar para Opções e Como Jogar
        self.btn_voltar_opcoes = Botao(((LARGURA - 200) // 2, 530, 200, 42), "ESC - Voltar", "voltar")
        self.btn_voltar_como_jogar = Botao(((LARGURA - 200) // 2, 530, 200, 42), "ESC - Voltar", "voltar")

    def reiniciar_bola(self):
        """Reinicia a bola no centro da quadra com direção aleatória."""
        self.bola.center = (LARGURA // 2, ALTURA // 2)
        direcao_x = random.choice([-1, 1])
        direcao_y = random.choice([-0.7, -0.4, 0.4, 0.7])
        self.vel_bola_x = direcao_x * VEL_INICIAL_BOLA
        self.vel_bola_y = direcao_y * VEL_INICIAL_BOLA

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
        self.estado = "JOGANDO"

    def iniciar_partida_2p(self):
        self.iniciar_partida(2)

    def atualizar_ia(self):
        """Controla a palete direita com limites de velocidade e comportamento humanoide."""
        # Se a bola está se movendo em direção à IA
        if self.vel_bola_x > 0:
            alvo_y = self.bola.centery
            diferenca = alvo_y - self.palete_dir.centery

            # Zona morta de 10 pixels para evitar jitter
            if abs(diferenca) > 10:
                if diferenca > 0:
                    movimento = min(VEL_IA, diferenca)
                    self.palete_dir.y += int(movimento)
                else:
                    movimento = max(-VEL_IA, diferenca)
                    self.palete_dir.y += int(movimento)
        else:
            # Quando a bola está indo embora, a IA reposiciona-se suavemente para o centro da quadra
            centro_quadra = ALTURA // 2
            diferenca = centro_quadra - self.palete_dir.centery
            if abs(diferenca) > 15:
                vel_retorno = 2.5
                if diferenca > 0:
                    self.palete_dir.y += int(min(vel_retorno, diferenca))
                else:
                    self.palete_dir.y += int(max(-vel_retorno, diferenca))

        # Manter a palete dentro da tela
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
            self.btn_voltar_opcoes.checar_hover(pos_mouse)
        elif self.estado == "MENU_COMO_JOGAR":
            self.btn_voltar_como_jogar.checar_hover(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            # --- TELA INICIAL (SPLASH) ---
            if self.estado == "SPLASH":
                if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                    self.estado = "MENU_PRINCIPAL"

            # --- MENU PRINCIPAL ---
            elif self.estado == "MENU_PRINCIPAL":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for btn in self.botoes_menu_principal:
                        if btn.foi_clicado(pos_mouse):
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
                        self.estado = "MENU_JOGAR"
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        self.estado = "MENU_OPCOES"
                    elif evento.key in (pygame.K_3, pygame.K_KP3):
                        self.estado = "MENU_COMO_JOGAR"
                    elif evento.key in (pygame.K_4, pygame.K_KP4, pygame.K_ESCAPE):
                        return False

            # --- MENU JOGAR ---
            elif self.estado == "MENU_JOGAR":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for btn in self.botoes_menu_jogar:
                        if btn.foi_clicado(pos_mouse):
                            if btn.id_acao == "1_jogador":
                                self.iniciar_partida(1)
                            elif btn.id_acao == "2_jogadores":
                                self.iniciar_partida(2)
                            elif btn.id_acao == "voltar":
                                self.estado = "MENU_PRINCIPAL"

                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_1, pygame.K_KP1):
                        self.iniciar_partida(1)
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        self.iniciar_partida(2)
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU_PRINCIPAL"

            # --- MENU OPÇÕES ---
            elif self.estado == "MENU_OPCOES":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    # Checar abas
                    for btn in self.botoes_abas_opcoes:
                        if btn.foi_clicado(pos_mouse):
                            self.elemento_opcao = btn.id_acao

                    # Checar botões de cores
                    for btn_cor in self.botoes_cores:
                        if btn_cor["rect"].collidepoint(pos_mouse):
                            self.definir_cor_elemento(btn_cor["cor"])

                    # Checar botão voltar
                    if self.btn_voltar_opcoes.foi_clicado(pos_mouse):
                        self.estado = "MENU_PRINCIPAL"

                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_1, pygame.K_KP1):
                        self.elemento_opcao = "barras"
                    elif evento.key in (pygame.K_2, pygame.K_KP2):
                        self.elemento_opcao = "bola"
                    elif evento.key in (pygame.K_3, pygame.K_KP3):
                        self.elemento_opcao = "rede"
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU_PRINCIPAL"

            # --- MENU COMO JOGAR ---
            elif self.estado == "MENU_COMO_JOGAR":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.btn_voltar_como_jogar.foi_clicado(pos_mouse):
                        self.estado = "MENU_PRINCIPAL"

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU_PRINCIPAL"

            # --- JOGANDO ---
            elif self.estado == "JOGANDO":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.estado = "MENU_PRINCIPAL"
                    elif evento.key == pygame.K_r:
                        self.iniciar_partida(self.modo_jogo)

        return True

    # ==========================================
    # LÓGICA DO JOGO (ATUALIZAÇÃO)
    # ==========================================
    def atualizar(self):
        if self.estado != "JOGANDO":
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

        # Lógica da Contagem Regressiva de 3 segundos
        if self.em_contagem:
            decorrido_ms = pygame.time.get_ticks() - self.tempo_inicio_contagem
            segundos_passados = decorrido_ms / 1000.0
            if segundos_passados < 3.0:
                self.segundos_restantes = 3 - int(segundos_passados)
                return  # A bola NÃO se move durante a contagem
            else:
                self.em_contagem = False
                self.reiniciar_bola()

        # Movimento da bola
        self.bola.x += int(self.vel_bola_x)
        self.bola.y += int(self.vel_bola_y)

        # Colisão com o teto e chão
        if self.bola.top <= 0:
            self.bola.top = 0
            self.vel_bola_y *= -1
        elif self.bola.bottom >= ALTURA:
            self.bola.bottom = ALTURA
            self.vel_bola_y *= -1

        # Colisão com palete esquerda (ambas usam cor_barras)
        if self.bola.colliderect(self.palete_esq) and self.vel_bola_x < 0:
            self.bola.left = self.palete_esq.right
            self.vel_bola_x = -self.vel_bola_x * 1.05
            offset = (self.bola.centery - self.palete_esq.centery) / (ALTURA_PALETE / 2)
            self.vel_bola_y = offset * abs(self.vel_bola_x)

        # Colisão com palete direita
        if self.bola.colliderect(self.palete_dir) and self.vel_bola_x > 0:
            self.bola.right = self.palete_dir.left
            self.vel_bola_x = -self.vel_bola_x * 1.05
            offset = (self.bola.centery - self.palete_dir.centery) / (ALTURA_PALETE / 2)
            self.vel_bola_y = offset * abs(self.vel_bola_x)

        # Limitar velocidade máxima para estabilidade física
        vel_maxima = 14
        self.vel_bola_x = max(-vel_maxima, min(vel_maxima, self.vel_bola_x))
        self.vel_bola_y = max(-vel_maxima, min(vel_maxima, self.vel_bola_y))

        # Pontuação
        if self.bola.left <= 0:
            self.pontos_dir += 1
            self.reiniciar_bola()
        elif self.bola.right >= LARGURA:
            self.pontos_esq += 1
            self.reiniciar_bola()

    # ==========================================
    # RENDERIZAÇÃO
    # ==========================================
    def desenhar(self):
        self.tela.fill(PRETO)

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
        # Título em destaque
        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        rect_titulo = titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 60))
        self.tela.blit(titulo, rect_titulo)

        # Efeito de piscar sutil
        piscar = (pygame.time.get_ticks() // 500) % 2 == 0
        if piscar:
            texto = self.fonte_subtitulo.render("Aperte qualquer tecla para iniciar", True, AMARELO)
            rect_texto = texto.get_rect(center=(LARGURA // 2, ALTURA // 2 + 50))
            self.tela.blit(texto, rect_texto)

        dica = self.fonte_texto.render("Pressione qualquer tecla ou clique para continuar", True, CINZA_TEXTO)
        self.tela.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA - 40)))

    def desenhar_menu_principal(self):
        """Menu principal com título 'Pong Clone' persistente e opções 1 a 4."""
        # Título fixo em destaque
        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        rect_titulo = titulo.get_rect(center=(LARGURA // 2, 100))
        self.tela.blit(titulo, rect_titulo)

        sub = self.fonte_texto.render("SELECIONE UMA OPÇÃO:", True, CINZA_TEXTO)
        self.tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 160)))

        # Botões
        for btn in self.botoes_menu_principal:
            btn.desenhar(self.tela, self.fonte_botao)

        # Rodapé
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

        # Mensagem informativa caso o jogador selecione '1 Jogador'
        if self.mensagem_aviso and (pygame.time.get_ticks() - self.tempo_aviso < 3500):
            aviso = self.fonte_texto.render(self.mensagem_aviso, True, AMARELO)
            rect_aviso = aviso.get_rect(center=(LARGURA // 2, 470))
            pygame.draw.rect(self.tela, (40, 35, 10), rect_aviso.inflate(24, 14), border_radius=6)
            pygame.draw.rect(self.tela, AMARELO, rect_aviso.inflate(24, 14), width=1, border_radius=6)
            self.tela.blit(aviso, rect_aviso)

    def desenhar_menu_opcoes(self):
        """Menu de customização de cores das barras, bolinha e rede central."""
        titulo = self.fonte_subtitulo.render("PERSONALIZAÇÃO DE CORES", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 50)))

        desc = self.fonte_texto.render("Escolha o item e selecione uma cor pré-definida:", True, CINZA_TEXTO)
        self.tela.blit(desc, desc.get_rect(center=(LARGURA // 2, 85)))

        # Abas dos elementos
        for btn in self.botoes_abas_opcoes:
            btn.desenhar(self.tela, self.fonte_botao)

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
            swatch_rect = pygame.Rect(rect.x + 8, rect.y + 7, 22, 22)
            pygame.draw.rect(self.tela, btn_cor["cor"], swatch_rect, border_radius=4)
            pygame.draw.rect(self.tela, BRANCO if btn_cor["cor"] == PRETO else CINZA_BORDA, swatch_rect, width=1, border_radius=4)

            # Nome da cor
            txt_surface = self.fonte_texto.render(btn_cor["nome"], True, AMARELO if selecionada else BRANCO)
            self.tela.blit(txt_surface, (rect.x + 38, rect.y + 8))

        # --- Mini Prévia em tempo real ---
        rect_preview = pygame.Rect(200, 315, 400, 180)
        pygame.draw.rect(self.tela, (10, 10, 15), rect_preview, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_preview, width=2, border_radius=8)

        lbl_preview = self.fonte_texto.render("Prévia em Tempo Real", True, CINZA_TEXTO)
        self.tela.blit(lbl_preview, (rect_preview.centerx - lbl_preview.get_width() // 2, rect_preview.y + 8))

        # Linha pontilhada no preview (cor da rede)
        for y in range(rect_preview.y + 35, rect_preview.bottom - 10, 16):
            pygame.draw.rect(self.tela, self.cor_rede, (rect_preview.centerx - 1, y, 3, 8))

        # Paletes do preview (cor das barras)
        pygame.draw.rect(self.tela, self.cor_barras, (rect_preview.x + 20, rect_preview.centery - 28, 8, 56), border_radius=2)
        pygame.draw.rect(self.tela, self.cor_barras, (rect_preview.right - 28, rect_preview.centery - 28, 8, 56), border_radius=2)

        # Bolinha do preview (cor da bola)
        pygame.draw.ellipse(self.tela, self.cor_bola, (rect_preview.centerx - 6, rect_preview.centery - 6, 12, 12))

        # Botão Voltar
        self.btn_voltar_opcoes.desenhar(self.tela, self.fonte_botao)

    def desenhar_como_jogar(self):
        """Tela de instruções e regras do Pong."""
        titulo = self.fonte_subtitulo.render("COMO JOGAR & REGRAS", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 45)))

        # Card de Controles
        rect_card1 = pygame.Rect(70, 80, 660, 185)
        pygame.draw.rect(self.tela, CINZA_CARD, rect_card1, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_card1, width=1, border_radius=8)

        tit1 = self.fonte_botao.render("CONTROLES", True, AMARELO)
        self.tela.blit(tit1, (rect_card1.x + 20, rect_card1.y + 12))

        linhas_controles = [
            "• Modo 1 Jogador       : Você (W / S) contra a CPU (IA com velocidade limitada)",
            "• Modo 2 Jogadores     : Jogador 1 (W / S) vs Jogador 2 (Setas Cima / Baixo)",
            "• Tecla [ R ]          : Reiniciar partida e contagem de 3 segundos",
            "• Tecla [ ESC ]        : Voltar ao Menu Principal",
        ]
        y_c1 = rect_card1.y + 48
        for linha in linhas_controles:
            txt = self.fonte_texto.render(linha, True, BRANCO)
            self.tela.blit(txt, (rect_card1.x + 20, y_c1))
            y_c1 += 32

        # Card de Regras
        rect_card2 = pygame.Rect(70, 280, 660, 230)
        pygame.draw.rect(self.tela, CINZA_CARD, rect_card2, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_card2, width=1, border_radius=8)

        tit2 = self.fonte_botao.render("REGRAS DO PONG", True, AMARELO)
        self.tela.blit(tit2, (rect_card2.x + 20, rect_card2.y + 12))

        linhas_regras = [
            "1. Cada jogador controla uma palete nas laterais da tela.",
            "2. O objetivo é rebater a bola e não deixá-la passar pela sua linha.",
            "3. Se a bola passar da defesa adversária, você ganha 1 ponto!",
            "4. A bola ganha velocidade a cada rebatida bem-sucedida.",
            "5. O ângulo de retorno da bola depende do ponto de impacto na palete.",
            "6. A IA possui limite de velocidade, permitindo que você a vença com jogadas rápidas!",
        ]
        y_c2 = rect_card2.y + 48
        for linha in linhas_regras:
            txt = self.fonte_texto.render(linha, True, BRANCO)
            self.tela.blit(txt, (rect_card2.x + 20, y_c2))
            y_c2 += 28

        # Botão Voltar
        self.btn_voltar_como_jogar.desenhar(self.tela, self.fonte_botao)

    def desenhar_jogo(self):
        """Renderiza a quadra de jogo com cores customizadas e contador."""
        # Rede pontilhada central (com a cor customizada da rede)
        passo = 15
        for y in range(0, ALTURA, passo * 2):
            pygame.draw.rect(self.tela, self.cor_rede, (LARGURA // 2 - 2, y, 4, passo))

        # Paletes (ambas compartilham a mesma cor customizada)
        pygame.draw.rect(self.tela, self.cor_barras, self.palete_esq)
        pygame.draw.rect(self.tela, self.cor_barras, self.palete_dir)

        # Bolinha (com a cor customizada da bola)
        pygame.draw.ellipse(self.tela, self.cor_bola, self.bola)

        # Placar numérico
        texto_esq = self.fonte_placar.render(str(self.pontos_esq), True, BRANCO)
        texto_dir = self.fonte_placar.render(str(self.pontos_dir), True, BRANCO)
        self.tela.blit(texto_esq, (LARGURA // 4 - texto_esq.get_width() // 2, 25))
        self.tela.blit(texto_dir, (3 * LARGURA // 4 - texto_dir.get_width() // 2, 25))

        # Rótulos dos jogadores no placar
        nome_esq = "JOGADOR 1" if self.modo_jogo == 2 else "VOCÊ"
        nome_dir = "JOGADOR 2" if self.modo_jogo == 2 else "CPU (IA)"
        lbl_esq = self.fonte_texto.render(nome_esq, True, CINZA_TEXTO)
        lbl_dir = self.fonte_texto.render(nome_dir, True, CINZA_TEXTO)
        self.tela.blit(lbl_esq, (LARGURA // 4 - lbl_esq.get_width() // 2, 75))
        self.tela.blit(lbl_dir, (3 * LARGURA // 4 - lbl_dir.get_width() // 2, 75))

        # Contador de 3 segundos na tela antes de iniciar
        if self.em_contagem:
            # Caixa estilizada com número da contagem
            rect_box = pygame.Rect(LARGURA // 2 - 120, ALTURA // 2 - 90, 240, 180)
            pygame.draw.rect(self.tela, (18, 18, 24), rect_box, border_radius=12)
            pygame.draw.rect(self.tela, AMARELO, rect_box, width=3, border_radius=12)

            txt_cont = self.fonte_contador.render(str(self.segundos_restantes), True, AMARELO)
            rect_cont = txt_cont.get_rect(center=(LARGURA // 2, ALTURA // 2 - 15))
            self.tela.blit(txt_cont, rect_cont)

            txt_prep = self.fonte_texto.render("PREPAREM-SE!", True, BRANCO)
            rect_prep = txt_prep.get_rect(center=(LARGURA // 2, ALTURA // 2 + 55))
            self.tela.blit(txt_prep, rect_prep)

        # Instruções no rodapé adaptadas ao modo
        if self.modo_jogo == 1:
            texto_rodape = "Você: W/S | Oponente: CPU (IA) | R: Reiniciar | ESC: Menu Principal"
        else:
            texto_rodape = "P1: W/S | P2: Setas | R: Reiniciar | ESC: Menu Principal"

        instrucoes = self.fonte_texto.render(texto_rodape, True, CINZA_TEXTO)
        self.tela.blit(instrucoes, (LARGURA // 2 - instrucoes.get_width() // 2, ALTURA - 25))

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
