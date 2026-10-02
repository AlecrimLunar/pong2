import pygame
import sys
import random
import os
import json
import datetime

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
VERMELHO_CORACAO = (235, 55, 75)
DOURADO = (255, 215, 0)

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
VEL_IA_BASE = 4.2

TAMANHO_BOLA = 15
VEL_INICIAL_BOLA = 5

# Arquivo de persistência de recordes arcade
ARQUIVO_RECORDES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")
CARACTERES_ARCADE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"


def carregar_recordes():
    """Carrega a tabela de recordes persistente do arquivo JSON."""
    if os.path.exists(ARQUIVO_RECORDES):
        try:
            with open(ARQUIVO_RECORDES, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
        except Exception as e:
            print(f"Aviso ao carregar recordes: {e}")
    # Recordes padrão de arcade clássico
    return [
        {"nome": "ACE", "adversario": 10, "combo_max": 5, "data": "2026-10-01"},
        {"nome": "VET", "adversario": 7,  "combo_max": 4, "data": "2026-10-01"},
        {"nome": "BOT", "adversario": 5,  "combo_max": 3, "data": "2026-10-01"},
        {"nome": "CPU", "adversario": 3,  "combo_max": 2, "data": "2026-10-01"},
        {"nome": "P1_", "adversario": 1,  "combo_max": 1, "data": "2026-10-01"},
    ]


def salvar_recordes(recordes):
    """Salva a tabela de recordes em disco de forma persistente."""
    try:
        with open(ARQUIVO_RECORDES, "w", encoding="utf-8") as f:
            json.dump(recordes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar recordes: {e}")


def registrar_novo_recorde(nome, adversario, combo_max):
    """Insere um novo recorde na tabela ordenada e salva no arquivo."""
    recordes = carregar_recordes()
    novo = {
        "nome": str(nome)[:3].upper(),
        "adversario": int(adversario),
        "combo_max": int(combo_max),
        "data": str(datetime.date.today())
    }
    recordes.append(novo)
    # Ordenar por adversário decrescente, e por combo decrescente
    recordes.sort(key=lambda r: (r.get("adversario", 0), r.get("combo_max", 0)), reverse=True)
    recordes = recordes[:10]  # Manter top 10
    salvar_recordes(recordes)
    return recordes


def desenhar_coracao(tela, x, y, tamanho=18, cor=VERMELHO_CORACAO, preenchido=True):
    """Desenha um coração retrô estilizado na tela."""
    surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    r = tamanho // 4
    c_esq = (r, r)
    c_dir = (tamanho - r, r)
    if preenchido:
        pygame.draw.circle(surf, cor, c_esq, r)
        pygame.draw.circle(surf, cor, c_dir, r)
        pontos = [(0, r), (tamanho, r), (tamanho // 2, tamanho)]
        pygame.draw.polygon(surf, cor, pontos)
    else:
        cor_borda = (80, 80, 95)
        pygame.draw.circle(surf, cor_borda, c_esq, r, width=2)
        pygame.draw.circle(surf, cor_borda, c_dir, r, width=2)
        pontos = [(0, r), (tamanho, r), (tamanho // 2, tamanho)]
        pygame.draw.polygon(surf, cor_borda, pontos, width=2)
    tela.blit(surf, (x, y))


class OndaImpacto:
    """Efeito de poucas ondas retrô se espalhando como uma gota d'água ao marcar ponto."""
    def __init__(self, x, y, cor):
        self.x = float(x)
        self.y = float(y)
        self.cor = cor
        # Poucas ondas (3 anéis concêntricos)
        self.ondas = [
            {"raio": 4.0, "delay": 0, "ativo": True},
            {"raio": 4.0, "delay": 7, "ativo": False},
            {"raio": 4.0, "delay": 14, "ativo": False},
        ]
        self.frame = 0
        self.duracao_max = 42
        self.raio_max = 140.0

    def atualizar(self):
        self.frame += 1
        for o in self.ondas:
            if not o["ativo"] and self.frame >= o["delay"]:
                o["ativo"] = True
            if o["ativo"]:
                o["raio"] += 3.4
        return self.frame < self.duracao_max

    def desenhar(self, tela):
        for o in self.ondas:
            if o["ativo"]:
                fator = min(1.0, o["raio"] / self.raio_max)
                alpha = int(220 * (1.0 - fator))
                if alpha <= 0:
                    continue
                raio = int(o["raio"])
                diametro = raio * 2 + 6
                surf = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
                cor_rgba = (*self.cor[:3], alpha)
                espessura = 2 if fator > 0.5 else 3
                pygame.draw.circle(surf, cor_rgba, (raio + 3, raio + 3), raio, width=espessura)
                tela.blit(surf, (int(self.x - raio - 3), int(self.y - raio - 3)))


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
        self.particulas = [p for p in self.particulas if p.atualizar()]

        if self.delay_ponto > 0:
            self.delay_ponto -= 1
            if self.delay_ponto == 0:
                self.reiniciar_bola()
            return

        self.rastro.append(self.bola.center)
        if len(self.rastro) > self.max_rastro:
            self.rastro.pop(0)

        if self.vel_x < 0:
            alvo = self.bola.centery
            diff = alvo - self.palete_esq.centery
            if abs(diff) > 8:
                self.palete_esq.y += int(min(self.vel_ia, diff) if diff > 0 else max(-self.vel_ia, diff))
        else:
            diff_centro = (self.altura // 2) - self.palete_esq.centery
            if abs(diff_centro) > 12:
                self.palete_esq.y += int(min(2.0, diff_centro) if diff_centro > 0 else max(-2.0, diff_centro))

        if self.vel_x > 0:
            alvo = self.bola.centery
            diff = alvo - self.palete_dir.centery
            if abs(diff) > 8:
                self.palete_dir.y += int(min(self.vel_ia, diff) if diff > 0 else max(-self.vel_ia, diff))
        else:
            diff_centro = (self.altura // 2) - self.palete_dir.centery
            if abs(diff_centro) > 12:
                self.palete_dir.y += int(min(2.0, diff_centro) if diff_centro > 0 else max(-2.0, diff_centro))

        self.palete_esq.top = max(0, min(self.altura - self.palete_esq.height, self.palete_esq.top))
        self.palete_dir.top = max(0, min(self.altura - self.palete_dir.height, self.palete_dir.top))

        self.bola.x += int(self.vel_x)
        self.bola.y += int(self.vel_y)

        if self.bola.top <= 0:
            self.bola.top = 0
            self.vel_y *= -1
            self.criar_impacto(self.bola.centerx, self.bola.top, 0, 1, (200, 200, 200), qtd=6)
        elif self.bola.bottom >= self.altura:
            self.bola.bottom = self.altura
            self.vel_y *= -1
            self.criar_impacto(self.bola.centerx, self.bola.bottom, 0, -1, (200, 200, 200), qtd=6)

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

        self.vel_x = max(-9, min(9, self.vel_x))
        self.vel_y = max(-9, min(9, self.vel_y))

        if self.bola.left <= 0:
            self.pontos_dir += 1
            self.delay_ponto = 20
        elif self.bola.right >= self.largura:
            self.pontos_esq += 1
            self.delay_ponto = 20

    def desenhar(self, tela, cor_barras, cor_bola, cor_rede, fonte_placar):
        passo = 15
        for y in range(0, self.altura, passo * 2):
            pygame.draw.rect(tela, cor_rede, (self.largura // 2 - 2, y, 4, passo))

        placar_cor = (max(20, cor_barras[0] // 2), max(20, cor_barras[1] // 2), max(20, cor_barras[2] // 2))
        txt_esq = fonte_placar.render(str(self.pontos_esq), True, placar_cor)
        txt_dir = fonte_placar.render(str(self.pontos_dir), True, placar_cor)
        tela.blit(txt_esq, (self.largura // 4 - txt_esq.get_width() // 2, 25))
        tela.blit(txt_dir, (3 * self.largura // 4 - txt_dir.get_width() // 2, 25))

        pygame.draw.rect(tela, cor_barras, self.palete_esq)
        pygame.draw.rect(tela, cor_barras, self.palete_dir)

        for p in self.particulas:
            p.desenhar(tela)

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

        pygame.draw.rect(tela, cor_bola, self.bola)
        tela.blit(self.surf_overlay, (0, 0))
        tela.blit(self.surf_scanlines, (0, 0))


def carregar_sistema_fontes():
    """Inicializa o sistema de renderização de fontes com suporte a fallback (pygame.font -> pygame.freetype -> DummyFont)."""
    global pygame
    try:
        if hasattr(pygame, "font") and pygame.font:
            pygame.font.init()
            if pygame.font.get_init():
                def criar_fonte_font(nome, tamanho, bold=False):
                    try:
                        return pygame.font.SysFont(nome, tamanho, bold=bold)
                    except Exception:
                        return pygame.font.Font(None, tamanho)
                return criar_fonte_font
    except Exception as e:
        print(f"[Aviso] pygame.font indisponível ({e}). Tentando fallback para pygame.freetype...")

    try:
        import pygame.freetype
        pygame.freetype.init()

        class FreetypeWrapper:
            def __init__(self, ft_font):
                self._font = ft_font

            def render(self, text, antialias, color, background=None):
                surf, _ = self._font.render(str(text), color, bgcolor=background)
                return surf

            def size(self, text):
                rect = self._font.get_rect(str(text))
                return (rect.width, rect.height)

        def criar_fonte_freetype(nome, tamanho, bold=False):
            try:
                ft = pygame.freetype.SysFont(nome, tamanho, bold=bold)
            except Exception:
                ft = pygame.freetype.Font(None, tamanho)
            return FreetypeWrapper(ft)

        print("[Info] pygame.freetype ativado com sucesso como mecanismo de fontes!")
        return criar_fonte_freetype
    except Exception as e:
        print(f"[Aviso] pygame.freetype também indisponível: {e}")

    class DummyFont:
        def __init__(self, tamanho=20):
            self.tamanho = tamanho

        def render(self, text, antialias, color, background=None):
            largura = max(len(str(text)) * int(self.tamanho * 0.6), 10)
            altura = max(int(self.tamanho * 1.2), 10)
            surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
            return surf

        def size(self, text):
            return (len(str(text)) * int(self.tamanho * 0.6), int(self.tamanho * 1.2))

    return lambda nome, tamanho, bold=False: DummyFont(tamanho)


class PongGame:
    def __init__(self):
        pygame.init()
        criar_fonte = carregar_sistema_fontes()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()

        # Fontes do sistema
        self.fonte_titulo = criar_fonte("consolas", 56, bold=True)
        self.fonte_subtitulo = criar_fonte("consolas", 28, bold=True)
        self.fonte_botao = criar_fonte("consolas", 22, bold=True)
        self.fonte_aba = criar_fonte("consolas", 20, bold=True)
        self.fonte_texto = criar_fonte("consolas", 16)
        self.fonte_texto_bold = criar_fonte("consolas", 16, bold=True)
        self.fonte_contador = criar_fonte("consolas", 84, bold=True)
        self.fonte_placar = criar_fonte("consolas", 48, bold=True)

        # Estados: SPLASH, MENU_PRINCIPAL, MENU_JOGAR, MENU_RECORDES, MENU_OPCOES, MENU_COMO_JOGAR, JOGANDO, REGISTRO_RECORDE
        self.estado = "SPLASH"

        # Cores Customizáveis (Branco por padrão)
        self.cor_barras = (255, 255, 255)
        self.cor_bola = (255, 255, 255)
        self.cor_rede = (255, 255, 255)

        self.elemento_opcao = "barras"
        self.mensagem_aviso = ""
        self.tempo_aviso = 0

        # Elementos de jogo
        self.palete_esq = pygame.Rect(30, (ALTURA - ALTURA_PALETE) // 2, LARGURA_PALETE, ALTURA_PALETE)
        self.palete_dir = pygame.Rect(LARGURA - 30 - LARGURA_PALETE, (ALTURA - ALTURA_PALETE) // 2, LARGURA_PALETE, ALTURA_PALETE)
        self.bola = pygame.Rect((LARGURA - TAMANHO_BOLA) // 2, (ALTURA - TAMANHO_BOLA) // 2, TAMANHO_BOLA, TAMANHO_BOLA)
        self.vel_bola_x = 0
        self.vel_bola_y = 0
        self.pontos_esq = 0
        self.pontos_dir = 0

        # Modo de jogo: 1 (1 Jogador vs IA Roguelite Arcade), 2 (2 Jogadores clássico)
        self.modo_jogo = 1

        # Mecânicas do Modo 1 Jogador (Vidas, Adversários e Combo)
        self.vida_jogador = 3
        self.adversario_atual = 1
        self.vida_cpu_maxima = 3
        self.vida_cpu = 3
        self.vel_ia_atual = VEL_IA_BASE
        self.combo_atual = 0
        self.tempo_combo_restante = 0.0
        self.tempo_combo_janela = 20.0
        self.max_combo_partida = 0
        self.mensagem_transicao_adv = ""
        self.tempo_transicao_adv = 0

        # Efeitos visuais (Partículas, Tremor, Ondas aquáticas)
        self.partida_fundo = PartidaFundo()
        self.rastro_bola_jogo = []
        self.particulas = []
        self.ondas_impacto = []
        self.tempo_tremida = 0
        self.intensidade_tremida = 0
        self.shake_x = 0
        self.shake_y = 0
        self.superficie_jogo = pygame.Surface((LARGURA, ALTURA))

        # Imprevisibilidade da IA
        self.ia_offset_alvo = 0
        self.sortear_estrategia_ia()

        # Contagens regressivas
        self.em_contagem = False
        self.tempo_inicio_contagem = 0
        self.segundos_restantes = 3

        self.em_contagem_ponto = False
        self.tempo_inicio_ponto = 0
        self.segundos_restantes_ponto = 2
        self.ultimo_marcador = "esq"

        # Sistema de Áudio e Controle de Volume
        self.volume = 0.7
        self.arrastando_volume = False
        self.carregar_sons()
        self.tocar_musica_menu()

        # Tabela de Recordes e Registro Arcade
        self.recordes = carregar_recordes()
        self.iniciais_arcade = ["A", "A", "A"]
        self.slot_letra_ativo = 0

        # Inicializar botões
        self.criar_botoes()

    # ==========================================
    # SISTEMA DE ÁUDIO
    # ==========================================
    def carregar_sons(self):
        """Carrega todos os efeitos sonoros e músicas da pasta Sons/."""
        self.audio_disponivel = False
        self.som_botao = None
        self.som_impacto = None
        self.som_contagem_3s = None
        self.som_yourself_point = None
        self.som_enemy_point = None
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
        self.som_yourself_point = carregar_efeito("yourself_point.mp3")
        self.som_enemy_point = carregar_efeito("enemy_point.mp3")

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
                if self.som_yourself_point:
                    self.som_yourself_point.set_volume(self.volume)
                if self.som_enemy_point:
                    self.som_enemy_point.set_volume(self.volume)
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
        # Botões do Menu Principal (5 opções agora, incluindo Recordes)
        largura_btn = 300
        altura_btn = 46
        x_btn = (LARGURA - largura_btn) // 2
        self.botoes_menu_principal = [
            Botao((x_btn, 190, largura_btn, altura_btn), "1 - Jogar", "jogar"),
            Botao((x_btn, 248, largura_btn, altura_btn), "2 - Recordes", "recordes"),
            Botao((x_btn, 306, largura_btn, altura_btn), "3 - Opções", "opcoes"),
            Botao((x_btn, 364, largura_btn, altura_btn), "4 - Como Jogar", "como_jogar"),
            Botao((x_btn, 422, largura_btn, altura_btn), "5 - Sair", "sair"),
        ]

        # Botões do Menu Jogar
        self.botoes_menu_jogar = [
            Botao((x_btn, 230, largura_btn, altura_btn), "1 - 1 Jogador", "1_jogador"),
            Botao((x_btn, 300, largura_btn, altura_btn), "2 - 2 Jogadores", "2_jogadores"),
            Botao((x_btn, 385, largura_btn, altura_btn), "ESC - Voltar", "voltar"),
        ]

        # Botão Voltar da Tabela de Recordes
        self.btn_voltar_recordes = Botao(((LARGURA - 200) // 2, 520, 200, 42), "ESC - Voltar", "voltar")

        # Botões de Abas no Menu de Opções
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

        # Botão de confirmação de recorde arcade
        self.btn_confirmar_recorde = Botao(((LARGURA - 280) // 2, 435, 280, 44), "CONFIRMAR REGISTRO", "confirmar_recorde")

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
        self.ondas_impacto.clear()
        self.sortear_estrategia_ia()

        # Configurações da campanha Roguelite Arcade para Modo 1 Jogador
        if modo == 1:
            self.vida_jogador = 3
            self.adversario_atual = 1
            self.vida_cpu_maxima = 3
            self.vida_cpu = 3
            self.vel_ia_atual = VEL_IA_BASE
            self.combo_atual = 0
            self.tempo_combo_restante = 0.0
            self.tempo_combo_janela = 20.0
            self.max_combo_partida = 0
            self.mensagem_transicao_adv = ""
            self.tempo_transicao_adv = 0

        self.estado = "JOGANDO"

        # Áudio: interrompe a música do menu e aciona a contagem regressiva de 3 segundos
        self.parar_musica()
        self.tocar_som(self.som_contagem_3s)

    def iniciar_contagem_ponto(self, lado_marcador="esq"):
        """Inicia a pausa e contagem regressiva de 2 segundos após um ponto marcado, aplica dano/combo e toca som."""
        self.em_contagem_ponto = True
        self.tempo_inicio_ponto = pygame.time.get_ticks()
        self.segundos_restantes_ponto = 2
        self.ultimo_marcador = lado_marcador

        # Posição da onda de impacto no ponto
        x_impacto = self.bola.centerx
        y_impacto = self.bola.centery
        self.bola.center = (LARGURA // 2, ALTURA // 2)
        self.vel_bola_x = 0
        self.vel_bola_y = 0
        self.rastro_bola_jogo.clear()
        self.particulas.clear()

        # Mecânicas do Modo 1 Jogador (Vidas, Danos, Combos e Próximo Adversário)
        if self.modo_jogo == 1:
            if lado_marcador == "esq":
                # JOGADOR PONTUOU NA CPU
                self.tocar_som(self.som_yourself_point)
                self.ondas_impacto.append(OndaImpacto(x_impacto, y_impacto, VERDE_DESTAQUE))

                # Avançar combo do jogador
                if self.combo_atual == 0:
                    self.combo_atual = 1
                else:
                    self.combo_atual = min(5, self.combo_atual + 1)

                self.max_combo_partida = max(self.max_combo_partida, self.combo_atual)

                # Janela de tempo: 20s no combo 1 até 6s no combo 5
                # Combo 1: 20s, Combo 2: 16.5s, Combo 3: 13s, Combo 4: 9.5s, Combo 5: 6s
                self.tempo_combo_janela = max(6.0, 20.0 - (self.combo_atual - 1) * 3.5)
                self.tempo_combo_restante = self.tempo_combo_janela

                # Dano na CPU: 2 no combo 5, 1 nos demais
                dano = 2 if self.combo_atual >= 5 else 1
                self.vida_cpu = max(0, self.vida_cpu - dano)

                # Verificar se a CPU foi derrotada
                if self.vida_cpu <= 0:
                    self.adversario_atual += 1
                    self.vida_jogador = 3  # Recupera todos os corações perdidos
                    self.vida_cpu_maxima = 3 + (self.adversario_atual - 1)  # Mais 1 coração de vida
                    self.vida_cpu = self.vida_cpu_maxima
                    # Aumento gradual e suave de velocidade da CPU (curva menor)
                    self.vel_ia_atual = min(6.5, VEL_IA_BASE + (self.adversario_atual - 1) * 0.08)
                    self.mensagem_transicao_adv = f"ADVERSÁRIO #{self.adversario_atual - 1} DERROTADO!"
                    self.tempo_transicao_adv = pygame.time.get_ticks()

                    # Transição para o próximo adversário: contagem de 3 segundos (não a de 2s)
                    self.em_contagem_ponto = False
                    self.em_contagem = True
                    self.tempo_inicio_contagem = pygame.time.get_ticks()
                    self.segundos_restantes = 3
                    self.palete_esq.centery = ALTURA // 2
                    self.palete_dir.centery = ALTURA // 2

                    # Interrompe música da partida e toca o som da contagem regressiva de 3s
                    self.parar_musica()
                    self.tocar_som(self.som_contagem_3s)
                    return

            else:
                # CPU PONTUOU NO JOGADOR
                self.tocar_som(self.som_enemy_point)
                self.ondas_impacto.append(OndaImpacto(x_impacto, y_impacto, (240, 60, 60)))

                # Jogador perde 1 coração
                self.vida_jogador = max(0, self.vida_jogador - 1)

                # Combo é quebrado imediatamente quando a CPU pontua
                self.combo_atual = 0
                self.tempo_combo_restante = 0.0

                # Verificar Game Over do jogador
                if self.vida_jogador <= 0:
                    self.preparar_registro_recorde()
                    return

        else:
            # Modo 2 Jogadores: som clássico de yourself_point para ambos
            self.tocar_som(self.som_yourself_point)
            cor_onda = AMARELO if lado_marcador == "esq" else (100, 180, 255)
            self.ondas_impacto.append(OndaImpacto(x_impacto, y_impacto, cor_onda))

    def preparar_registro_recorde(self):
        """Prepara o estado de registro de recorde de 3 letras ao perder no modo 1 jogador."""
        self.estado = "REGISTRO_RECORDE"
        self.iniciais_arcade = ["A", "A", "A"]
        self.slot_letra_ativo = 0
        self.parar_musica()
        self.tocar_musica_menu()

    def atualizar_ia(self):
        """Controla a palete direita com limites de velocidade proporcionais ao adversário atual."""
        vel_atual = self.vel_ia_atual if self.modo_jogo == 1 else 4.5

        if self.vel_bola_x > 0:
            ponto_alvo_palete = self.palete_dir.centery + self.ia_offset_alvo
            diferenca = self.bola.centery - ponto_alvo_palete

            if abs(diferenca) > 8:
                if diferenca > 0:
                    movimento = min(vel_atual, diferenca)
                    self.palete_dir.y += int(movimento)
                else:
                    movimento = max(-vel_atual, diferenca)
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
        elif self.estado == "MENU_RECORDES":
            self.btn_voltar_recordes.checar_hover(pos_mouse)
        elif self.estado == "REGISTRO_RECORDE":
            self.btn_confirmar_recorde.checar_hover(pos_mouse)
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

            # --- MENU PRINCIPAL (5 OPÇÕES) ---
            elif self.estado == "MENU_PRINCIPAL":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for btn in self.botoes_menu_principal:
                        if btn.foi_clicado(pos_mouse):
                            self.tocar_som(self.som_botao)
                            if btn.id_acao == "jogar":
                                self.estado = "MENU_JOGAR"
                            elif btn.id_acao == "recordes":
                                self.recordes = carregar_recordes()
                                self.estado = "MENU_RECORDES"
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
                        self.recordes = carregar_recordes()
                        self.estado = "MENU_RECORDES"
                    elif evento.key in (pygame.K_3, pygame.K_KP3):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_OPCOES"
                    elif evento.key in (pygame.K_4, pygame.K_KP4):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_COMO_JOGAR"
                    elif evento.key in (pygame.K_5, pygame.K_KP5, pygame.K_ESCAPE):
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

            # --- MENU RECORDES (TABELA DE RANQUE) ---
            elif self.estado == "MENU_RECORDES":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.btn_voltar_recordes.foi_clicado(pos_mouse):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"
                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.tocar_som(self.som_botao)
                        self.estado = "MENU_PRINCIPAL"

            # --- REGISTRO DE RECORDE ARCADE (3 LETRAS) ---
            elif self.estado == "REGISTRO_RECORDE":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.btn_confirmar_recorde.foi_clicado(pos_mouse):
                        self.tocar_som(self.som_botao)
                        nome = "".join(self.iniciais_arcade)
                        self.recordes = registrar_novo_recorde(nome, self.adversario_atual, self.max_combo_partida)
                        self.estado = "MENU_RECORDES"

                elif evento.type == pygame.KEYDOWN:
                    caractere_atual = self.iniciais_arcade[self.slot_letra_ativo]
                    idx_atual = CARACTERES_ARCADE.find(caractere_atual)
                    if idx_atual == -1:
                        idx_atual = 0

                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.tocar_som(self.som_botao)
                        novo_idx = (idx_atual + 1) % len(CARACTERES_ARCADE)
                        self.iniciais_arcade[self.slot_letra_ativo] = CARACTERES_ARCADE[novo_idx]

                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.tocar_som(self.som_botao)
                        novo_idx = (idx_atual - 1) % len(CARACTERES_ARCADE)
                        self.iniciais_arcade[self.slot_letra_ativo] = CARACTERES_ARCADE[novo_idx]

                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        self.tocar_som(self.som_botao)
                        if self.slot_letra_ativo < 2:
                            self.slot_letra_ativo += 1

                    elif evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_BACKSPACE):
                        self.tocar_som(self.som_botao)
                        if self.slot_letra_ativo > 0:
                            self.slot_letra_ativo -= 1

                    elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        self.tocar_som(self.som_botao)
                        if self.slot_letra_ativo < 2:
                            self.slot_letra_ativo += 1
                        else:
                            nome = "".join(self.iniciais_arcade)
                            self.recordes = registrar_novo_recorde(nome, self.adversario_atual, self.max_combo_partida)
                            self.estado = "MENU_RECORDES"

            # --- MENU OPÇÕES ---
            elif self.estado == "MENU_OPCOES":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for btn in self.botoes_abas_opcoes:
                        if btn.foi_clicado(pos_mouse):
                            self.tocar_som(self.som_botao)
                            self.elemento_opcao = btn.id_acao

                    for btn_cor in self.botoes_cores:
                        if btn_cor["rect"].collidepoint(pos_mouse):
                            self.tocar_som(self.som_botao)
                            self.definir_cor_elemento(btn_cor["cor"])

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
            self.atualizar_ia()

        # Lógica da Contagem Regressiva de 3 segundos (Início de partida ou Novo Adversário)
        if self.em_contagem:
            decorrido_ms = pygame.time.get_ticks() - self.tempo_inicio_contagem
            segundos_passados = decorrido_ms / 1000.0
            if segundos_passados < 3.0:
                self.segundos_restantes = 3 - int(segundos_passados)
                # Atualizar ondas de impacto e partículas mesmo durante a contagem
                self.ondas_impacto = [o for o in self.ondas_impacto if o.atualizar()]
                self.particulas = [p for p in self.particulas if p.atualizar()]
                return
            else:
                self.em_contagem = False
                self.mensagem_transicao_adv = ""
                self.reiniciar_bola()
                self.tocar_musica_partida()

        # Lógica da Contagem Regressiva de 2 segundos (Após cada ponto marcado)
        if self.em_contagem_ponto:
            decorrido_ms = pygame.time.get_ticks() - self.tempo_inicio_ponto
            segundos_passados = decorrido_ms / 1000.0
            if segundos_passados < 2.0:
                self.segundos_restantes_ponto = 2 - int(segundos_passados)
                # Atualizar ondas de impacto mesmo na pausa
                self.ondas_impacto = [o for o in self.ondas_impacto if o.atualizar()]
                self.particulas = [p for p in self.particulas if p.atualizar()]
                return
            else:
                self.em_contagem_ponto = False
                self.reiniciar_bola()

        # Atualização do temporizador de COMBO (apenas com a bola em jogo)
        if self.modo_jogo == 1 and self.combo_atual > 0:
            self.tempo_combo_restante -= 1.0 / FPS
            if self.tempo_combo_restante <= 0:
                self.combo_atual = 0
                self.tempo_combo_restante = 0.0

        # Atualizar ondas de impacto aquáticas e partículas
        self.ondas_impacto = [o for o in self.ondas_impacto if o.atualizar()]
        self.particulas = [p for p in self.particulas if p.atualizar()]

        # Registrar rastro de movimento retrô da bola
        self.rastro_bola_jogo.append(self.bola.center)
        if len(self.rastro_bola_jogo) > 6:
            self.rastro_bola_jogo.pop(0)

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

        # Colisão com palete esquerda (Jogador)
        if self.bola.colliderect(self.palete_esq) and self.vel_bola_x < 0:
            self.bola.left = self.palete_esq.right
            self.vel_bola_x = -self.vel_bola_x * 1.05

            # Bônus de velocidade do COMBO do JOGADOR
            if self.modo_jogo == 1 and self.combo_atual > 1:
                # Combo 2 dá +0.7, Combo 3 +1.4, Combo 4 +2.1, Combo 5 (cap) +2.8
                bonus_combo = (min(5, self.combo_atual) - 1) * 0.70
                self.vel_bola_x += bonus_combo

            offset = (self.bola.centery - self.palete_esq.centery) / (ALTURA_PALETE / 2)
            self.vel_bola_y = offset * abs(self.vel_bola_x)
            self.sortear_estrategia_ia()
            self.criar_impacto(self.palete_esq.right, self.bola.centery, 1, 0, self.cor_barras, qtd=14, shake_intensidade=4, shake_duracao=6)

        # Colisão com palete direita (CPU ou Jogador 2)
        if self.bola.colliderect(self.palete_dir) and self.vel_bola_x > 0:
            self.bola.right = self.palete_dir.left

            # Força de rebatimento gradual e equilibrada da CPU
            if self.modo_jogo == 1:
                mult_cpu = 1.035 + min(0.06, (self.adversario_atual - 1) * 0.005)
                self.vel_bola_x = -self.vel_bola_x * mult_cpu
            else:
                self.vel_bola_x = -self.vel_bola_x * 1.05

            offset = (self.bola.centery - self.palete_dir.centery) / (ALTURA_PALETE / 2)
            self.vel_bola_y = offset * abs(self.vel_bola_x)
            self.criar_impacto(self.palete_dir.left, self.bola.centery, -1, 0, self.cor_barras, qtd=14, shake_intensidade=4, shake_duracao=6)

        # Limitar velocidade máxima física com cap
        vel_maxima = 16.5
        self.vel_bola_x = max(-vel_maxima, min(vel_maxima, self.vel_bola_x))
        self.vel_bola_y = max(-vel_maxima, min(vel_maxima, self.vel_bola_y))

        # Pontuação
        if self.bola.left <= 0:
            self.pontos_dir += 1
            self.iniciar_contagem_ponto(lado_marcador="dir")
        elif self.bola.right >= LARGURA:
            self.pontos_esq += 1
            self.iniciar_contagem_ponto(lado_marcador="esq")

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
        elif self.estado == "MENU_RECORDES":
            self.desenhar_menu_recordes()
        elif self.estado == "REGISTRO_RECORDE":
            self.desenhar_registro_recorde()
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
        """Menu principal com título 'Pong Clone' e 5 opções (Jogar, Recordes, Opções, Como Jogar, Sair)."""
        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        rect_titulo = titulo.get_rect(center=(LARGURA // 2, 85))
        self.tela.blit(titulo, rect_titulo)

        sub = self.fonte_texto.render("SELECIONE UMA OPÇÃO:", True, CINZA_TEXTO)
        self.tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 145)))

        for btn in self.botoes_menu_principal:
            btn.desenhar(self.tela, self.fonte_botao)

        dica = self.fonte_texto.render("Dica: Use o mouse ou os números [1, 2, 3, 4, 5] no teclado", True, CINZA_TEXTO)
        self.tela.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA - 35)))

    def desenhar_menu_jogar(self):
        """Submenu de seleção de modo de jogo."""
        titulo = self.fonte_titulo.render("PONG CLONE", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 90)))

        sub = self.fonte_subtitulo.render("MODO DE JOGO", True, AMARELO)
        self.tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 165)))

        for btn in self.botoes_menu_jogar:
            btn.desenhar(self.tela, self.fonte_botao)

    def desenhar_menu_recordes(self):
        """Tela de exibição da tabela de recordes (Hall da Fama Arcade)."""
        titulo = self.fonte_subtitulo.render("TABELA DE RECORDES - ARCADE", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 45)))

        desc = self.fonte_texto.render("Maiores adversários alcançados no modo 1 Jogador:", True, CINZA_TEXTO)
        self.tela.blit(desc, desc.get_rect(center=(LARGURA // 2, 78)))

        # Moldura da Tabela
        rect_tabela = pygame.Rect(90, 105, 620, 395)
        pygame.draw.rect(self.tela, CINZA_CARD, rect_tabela, border_radius=10)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_tabela, width=2, border_radius=10)

        # Cabeçalho da Tabela
        pygame.draw.rect(self.tela, (24, 24, 32), (rect_tabela.x, rect_tabela.y, rect_tabela.width, 36), border_top_left_radius=10, border_top_right_radius=10)
        col_pos = rect_tabela.x + 35
        col_nome = rect_tabela.x + 140
        col_adv = rect_tabela.x + 295
        col_combo = rect_tabela.x + 480

        h_pos = self.fonte_botao.render("POS", True, AMARELO)
        h_nome = self.fonte_botao.render("NOME", True, AMARELO)
        h_adv = self.fonte_botao.render("ADVERSÁRIO", True, AMARELO)
        h_combo = self.fonte_botao.render("MAX COMBO", True, AMARELO)

        self.tela.blit(h_pos, (col_pos, rect_tabela.y + 6))
        self.tela.blit(h_nome, (col_nome, rect_tabela.y + 6))
        self.tela.blit(h_adv, (col_adv, rect_tabela.y + 6))
        self.tela.blit(h_combo, (col_combo, rect_tabela.y + 6))

        # Linhas dos Recordes
        recordes = self.recordes[:8]
        y_linha = rect_tabela.y + 48

        for idx, rec in enumerate(recordes):
            if idx == 0:
                cor_pos = DOURADO
            elif idx == 1:
                cor_pos = (210, 215, 225)
            elif idx == 2:
                cor_pos = (205, 127, 50)
            else:
                cor_pos = BRANCO

            txt_p = self.fonte_texto.render(f"{idx + 1}º", True, cor_pos)
            txt_n = self.fonte_botao.render(rec.get("nome", "---"), True, cor_pos)
            txt_a = self.fonte_texto.render(f"Adversário #{rec.get('adversario', 1)}", True, BRANCO)
            txt_c = self.fonte_texto.render(f"x{rec.get('combo_max', 1)}", True, AMARELO)

            self.tela.blit(txt_p, (col_pos + 6, y_linha + 3))
            self.tela.blit(txt_n, (col_nome, y_linha))
            self.tela.blit(txt_a, (col_adv + 8, y_linha + 3))
            self.tela.blit(txt_c, (col_combo + 25, y_linha + 3))

            pygame.draw.line(self.tela, (45, 45, 55), (rect_tabela.x + 20, y_linha + 36), (rect_tabela.right - 20, y_linha + 36), 1)
            y_linha += 42

        self.btn_voltar_recordes.desenhar(self.tela, self.fonte_botao)

    def desenhar_registro_recorde(self):
        """Tela de registro de recorde estilo arcade com 3 letras após o Game Over."""
        rect_card = pygame.Rect(LARGURA // 2 - 260, ALTURA // 2 - 215, 520, 430)
        pygame.draw.rect(self.tela, (14, 14, 20), rect_card, border_radius=12)
        pygame.draw.rect(self.tela, (230, 60, 60), rect_card, width=3, border_radius=12)

        tit = self.fonte_titulo.render("GAME OVER", True, (240, 60, 60))
        self.tela.blit(tit, tit.get_rect(center=(LARGURA // 2, rect_card.y + 45)))

        sub1 = self.fonte_subtitulo.render(f"VOCÊ CHEGOU AO ADVERSÁRIO #{self.adversario_atual}", True, AMARELO)
        self.tela.blit(sub1, sub1.get_rect(center=(LARGURA // 2, rect_card.y + 100)))

        sub2 = self.fonte_texto.render(f"Combo Máximo da Partida: x{self.max_combo_partida}", True, CINZA_TEXTO)
        self.tela.blit(sub2, sub2.get_rect(center=(LARGURA // 2, rect_card.y + 135)))

        lbl_ins = self.fonte_botao.render("INSIRA SUAS INICIAIS", True, BRANCO)
        self.tela.blit(lbl_ins, lbl_ins.get_rect(center=(LARGURA // 2, rect_card.y + 180)))

        # 3 Slots de Letras estilo arcade
        largura_slot = 68
        altura_slot = 68
        espaco_slot = 24
        x_base_slots = (LARGURA - (3 * largura_slot + 2 * espaco_slot)) // 2
        y_slots = rect_card.y + 220

        for i in range(3):
            x_slot = x_base_slots + i * (largura_slot + espaco_slot)
            rect_slot = pygame.Rect(x_slot, y_slots, largura_slot, altura_slot)
            ativo = (i == self.slot_letra_ativo)

            bg_slot = (32, 32, 44) if ativo else (18, 18, 24)
            borda_slot = AMARELO if ativo else CINZA_BORDA

            pygame.draw.rect(self.tela, bg_slot, rect_slot, border_radius=8)
            pygame.draw.rect(self.tela, borda_slot, rect_slot, width=3 if ativo else 1, border_radius=8)

            txt_l = self.fonte_subtitulo.render(self.iniciais_arcade[i], True, AMARELO if ativo else BRANCO)
            self.tela.blit(txt_l, txt_l.get_rect(center=rect_slot.center))

            if ativo:
                seta_cima = self.fonte_texto.render("▲", True, AMARELO)
                self.tela.blit(seta_cima, seta_cima.get_rect(center=(rect_slot.centerx, rect_slot.y - 14)))
                seta_baixo = self.fonte_texto.render("▼", True, AMARELO)
                self.tela.blit(seta_baixo, seta_baixo.get_rect(center=(rect_slot.centerx, rect_slot.bottom + 14)))

        dica = self.fonte_texto.render("Use [CIMA/BAIXO/W/S] | [ENTER/ESPAÇO] para confirmar", True, CINZA_TEXTO)
        self.tela.blit(dica, dica.get_rect(center=(LARGURA // 2, rect_card.y + 325)))

        self.btn_confirmar_recorde.desenhar(self.tela, self.fonte_botao)

    def desenhar_menu_opcoes(self):
        """Menu de customização de cores e controle de volume."""
        titulo = self.fonte_subtitulo.render("OPÇÕES E PERSONALIZAÇÃO", True, BRANCO)
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 35)))

        desc = self.fonte_texto.render("Escolha o elemento e selecione uma cor pré-definida:", True, CINZA_TEXTO)
        self.tela.blit(desc, desc.get_rect(center=(LARGURA // 2, 68)))

        for btn in self.botoes_abas_opcoes:
            btn.desenhar(self.tela, self.fonte_aba)

        pos_mouse = pygame.mouse.get_pos()
        cor_atual = self.cor_atual_elemento()

        for btn_cor in self.botoes_cores:
            rect = btn_cor["rect"]
            hover = rect.collidepoint(pos_mouse)
            selecionada = (btn_cor["cor"] == cor_atual)

            bg_cor = CINZA_CARD if hover or selecionada else (18, 18, 22)
            borda_cor = AMARELO if selecionada else (BRANCO if hover else CINZA_BORDA)
            pygame.draw.rect(self.tela, bg_cor, rect, border_radius=6)
            pygame.draw.rect(self.tela, borda_cor, rect, width=2 if selecionada else 1, border_radius=6)

            swatch_rect = pygame.Rect(rect.x + 8, rect.y + 6, 20, 20)
            pygame.draw.rect(self.tela, btn_cor["cor"], swatch_rect, border_radius=4)
            pygame.draw.rect(self.tela, BRANCO if btn_cor["cor"] == PRETO else CINZA_BORDA, swatch_rect, width=1, border_radius=4)

            txt_surface = self.fonte_texto.render(btn_cor["nome"], True, AMARELO if selecionada else BRANCO)
            self.tela.blit(txt_surface, (rect.x + 36, rect.y + 6))

        # Mini Prévia em tempo real
        rect_preview = pygame.Rect(210, 258, 380, 120)
        pygame.draw.rect(self.tela, (10, 10, 15), rect_preview, border_radius=8)
        pygame.draw.rect(self.tela, CINZA_BORDA, rect_preview, width=2, border_radius=8)

        lbl_preview = self.fonte_texto.render("Prévia em Tempo Real", True, CINZA_TEXTO)
        self.tela.blit(lbl_preview, (rect_preview.centerx - lbl_preview.get_width() // 2, rect_preview.y + 5))

        for y in range(rect_preview.y + 26, rect_preview.bottom - 6, 14):
            pygame.draw.rect(self.tela, self.cor_rede, (rect_preview.centerx - 1, y, 3, 7))

        pygame.draw.rect(self.tela, self.cor_barras, (rect_preview.x + 18, rect_preview.centery - 24, 7, 48), border_radius=2)
        pygame.draw.rect(self.tela, self.cor_barras, (rect_preview.right - 25, rect_preview.centery - 24, 7, 48), border_radius=2)
        pygame.draw.rect(self.tela, self.cor_bola, (rect_preview.centerx - 5, rect_preview.centery - 5, 10, 10))

        # Seção de Controle de Volume
        pct_volume = int(round(self.volume * 100))
        lbl_vol = self.fonte_texto.render(f"VOLUME DO JOGO: {pct_volume}%", True, AMARELO)
        self.tela.blit(lbl_vol, (LARGURA // 2 - lbl_vol.get_width() // 2, 396))

        self.btn_vol_menos.desenhar(self.tela, self.fonte_botao)

        pygame.draw.rect(self.tela, (14, 14, 18), self.rect_barra_volume, border_radius=6)
        largura_preenchida = int(self.rect_barra_volume.width * self.volume)
        if largura_preenchida > 0:
            rect_preenchido = pygame.Rect(self.rect_barra_volume.x, self.rect_barra_volume.y, largura_preenchida, self.rect_barra_volume.height)
            pygame.draw.rect(self.tela, AMARELO, rect_preenchido, border_radius=6)
        pygame.draw.rect(self.tela, CINZA_BORDA, self.rect_barra_volume, width=2, border_radius=6)

        knob_x = self.rect_barra_volume.x + largura_preenchida
        knob_rect = pygame.Rect(knob_x - 4, self.rect_barra_volume.y - 3, 8, self.rect_barra_volume.height + 6)
        pygame.draw.rect(self.tela, BRANCO, knob_rect, border_radius=3)

        self.btn_vol_mais.desenhar(self.tela, self.fonte_botao)

        dica_vol = self.fonte_texto.render("Ajuste com [-] / [+] ou Setas Esquerda/Direita", True, CINZA_TEXTO)
        self.tela.blit(dica_vol, (LARGURA // 2 - dica_vol.get_width() // 2, 468))

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
            "• Modo 1 Jogador   : Você (W / S) contra os Adversários da CPU",
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

        tit2 = self.fonte_botao.render("REGRAS & CAMPANHA ARCADE", True, AMARELO)
        self.tela.blit(tit2, (rect_card2.x + 22, rect_card2.y + 12))

        linhas_regras = [
            "1. No modo 1P: 3 vidas (corações). Ponto sofrido custa 1 vida.",
            "2. Derrote a CPU para avançar: cada adversário é mais rápido e forte!",
            "3. Vencer recupera seus corações. Adversários ganham mais vidas.",
            "4. COMBO: Faça pontos rápidos para acelerar a bola e causar 2x dano!",
            "5. Ao perder, registre seu nome de 3 letras na Tabela de Recordes.",
            "6. A CPU rebate com ângulos dinâmicos e velocidade justa.",
        ]
        y_c2 = rect_card2.y + 44
        for linha in linhas_regras:
            txt = self.fonte_texto.render(linha, True, BRANCO)
            self.tela.blit(txt, (rect_card2.x + 22, y_c2))
            y_c2 += 29

        self.btn_voltar_como_jogar.desenhar(self.tela, self.fonte_botao)

    def desenhar_jogo(self):
        """Renderiza a quadra de jogo com camadas ordenadas: rede ao fundo, HUD na camada intermediária e paletes/bolinha em primeiro plano."""
        self.superficie_jogo.fill(PRETO)

        # -------------------------------------------------------------
        # CAMADA 1 (FUNDO ABSOLUTO / ÚLTIMA CAMADA): Rede Central Pontilhada
        # -------------------------------------------------------------
        passo = 15
        for y in range(0, ALTURA, passo * 2):
            pygame.draw.rect(self.superficie_jogo, self.cor_rede, (LARGURA // 2 - 2, y, 4, passo))

        # Ondas aquáticas de impacto retrô ao fazer ponto (no fundo)
        for o in self.ondas_impacto:
            o.desenhar(self.superficie_jogo)

        # -------------------------------------------------------------
        # CAMADA 2 (CAMADA DA HUD): Abaixo dos paletes e da bolinha
        # -------------------------------------------------------------
        if self.modo_jogo == 1:
            # Distintivo do Adversário Atual no topo
            rect_adv = pygame.Rect(LARGURA // 2 - 100, 16, 200, 32)
            pygame.draw.rect(self.superficie_jogo, CINZA_CARD, rect_adv, border_radius=6)
            pygame.draw.rect(self.superficie_jogo, AMARELO, rect_adv, width=2, border_radius=6)
            txt_adv = self.fonte_texto_bold.render(f"ADVERSÁRIO #{self.adversario_atual}", True, AMARELO)
            self.superficie_jogo.blit(txt_adv, txt_adv.get_rect(center=rect_adv.center))

            # --- LADO ESQUERDO: VOCÊ ---
            lbl_esq = self.fonte_texto.render("VOCÊ", True, BRANCO)
            self.superficie_jogo.blit(lbl_esq, (60, 20))

            # Corações do Jogador (sempre 3 corações máximos)
            for i in range(3):
                desenhar_coracao(self.superficie_jogo, 60 + i * 26, 44, tamanho=20, cor=VERMELHO_CORACAO, preenchido=(i < self.vida_jogador))

            # --- LADO DIREITO: CPU (ADVERSÁRIO) ---
            lbl_dir = self.fonte_texto.render(f"CPU (ADV #{self.adversario_atual})", True, BRANCO)
            self.superficie_jogo.blit(lbl_dir, (LARGURA - 60 - lbl_dir.get_width(), 20))

            # Corações da CPU (Regra 7):
            # Se vida máxima <= 5: desenha os corações individuais
            # Se vida máxima > 5: desenha 1 coração com "x{self.vida_cpu}"
            if self.vida_cpu_maxima <= 5:
                largura_total_coracoes = self.vida_cpu_maxima * 26
                x_base_cpu = LARGURA - 60 - largura_total_coracoes
                for i in range(self.vida_cpu_maxima):
                    desenhar_coracao(self.superficie_jogo, x_base_cpu + i * 26, 44, tamanho=20, cor=VERMELHO_CORACAO, preenchido=(i < self.vida_cpu))
            else:
                txt_qtd = self.fonte_subtitulo.render(f"x{self.vida_cpu}", True, AMARELO)
                x_coracao = LARGURA - 70 - txt_qtd.get_width() - 26
                desenhar_coracao(self.superficie_jogo, x_coracao, 42, tamanho=22, cor=VERMELHO_CORACAO, preenchido=True)
                self.superficie_jogo.blit(txt_qtd, (x_coracao + 28, 40))

            # --- PAINEL DO COMBO DO JOGADOR ---
            if self.combo_atual > 0:
                rect_combo = pygame.Rect(30, 78, 220, 42)
                cor_borda_combo = (245, 60, 60) if self.combo_atual >= 5 else AMARELO
                pygame.draw.rect(self.superficie_jogo, (16, 16, 22), rect_combo, border_radius=6)
                pygame.draw.rect(self.superficie_jogo, cor_borda_combo, rect_combo, width=2, border_radius=6)

                txt_combo = f"COMBO x{self.combo_atual} [DANO 2x!]" if self.combo_atual >= 5 else f"COMBO x{self.combo_atual}"
                surf_c = self.fonte_texto_bold.render(txt_combo, True, cor_borda_combo)
                self.superficie_jogo.blit(surf_c, (rect_combo.x + 8, rect_combo.y + 4))

                pct_tempo = max(0.0, min(1.0, self.tempo_combo_restante / self.tempo_combo_janela))
                rect_barra = pygame.Rect(rect_combo.x + 8, rect_combo.y + 24, 140, 10)
                pygame.draw.rect(self.superficie_jogo, (35, 35, 45), rect_barra, border_radius=3)
                if pct_tempo > 0:
                    pygame.draw.rect(self.superficie_jogo, cor_borda_combo, (rect_barra.x, rect_barra.y, int(rect_barra.width * pct_tempo), rect_barra.height), border_radius=3)
                txt_t = self.fonte_texto.render(f"{self.tempo_combo_restante:.1f}s", True, BRANCO)
                self.superficie_jogo.blit(txt_t, (rect_combo.x + 155, rect_combo.y + 21))

        else:
            # Placar clássico no Modo 2 Jogadores
            texto_esq = self.fonte_placar.render(str(self.pontos_esq), True, BRANCO)
            texto_dir = self.fonte_placar.render(str(self.pontos_dir), True, BRANCO)
            self.superficie_jogo.blit(texto_esq, (LARGURA // 4 - texto_esq.get_width() // 2, 25))
            self.superficie_jogo.blit(texto_dir, (3 * LARGURA // 4 - texto_dir.get_width() // 2, 25))
            lbl_esq = self.fonte_texto.render("JOGADOR 1", True, CINZA_TEXTO)
            lbl_dir = self.fonte_texto.render("JOGADOR 2", True, CINZA_TEXTO)
            self.superficie_jogo.blit(lbl_esq, (LARGURA // 4 - lbl_esq.get_width() // 2, 75))
            self.superficie_jogo.blit(lbl_dir, (3 * LARGURA // 4 - lbl_dir.get_width() // 2, 75))

        # Instruções no rodapé adaptadas ao modo (na camada HUD)
        if self.modo_jogo == 1:
            texto_rodape = "Você: W/S | Oponente: CPU (IA) | R: Reiniciar | ESC: Menu Principal"
        else:
            texto_rodape = "P1: W/S | P2: Setas | R: Reiniciar | ESC: Menu Principal"

        instrucoes = self.fonte_texto.render(texto_rodape, True, CINZA_TEXTO)
        self.superficie_jogo.blit(instrucoes, (LARGURA // 2 - instrucoes.get_width() // 2, ALTURA - 25))

        # -------------------------------------------------------------
        # CAMADA 3 (CAMADA PRINCIPAL DE JOGO): Paletes e Bolinha por CIMA da HUD
        # -------------------------------------------------------------
        # Rastro retrô da bola
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

        # Paletes (renderizadas sobre a HUD para máxima visibilidade)
        pygame.draw.rect(self.superficie_jogo, self.cor_barras, self.palete_esq)
        pygame.draw.rect(self.superficie_jogo, self.cor_barras, self.palete_dir)

        # Bolinha (renderizada sobre a HUD para que nunca se esconda)
        pygame.draw.rect(self.superficie_jogo, self.cor_bola, self.bola)

        # Partículas de impacto no ar (sobretudo paletes e bola)
        for p in self.particulas:
            p.desenhar(self.superficie_jogo)

        # -------------------------------------------------------------
        # CAMADA 4 (BOXES DE CONTAGEM REGRESSIVA): Renderizadas POR CIMA da bolinha
        # -------------------------------------------------------------
        # Contador de 3 segundos (Início de partida ou Transição para Novo Adversário)
        if self.em_contagem:
            rect_box = pygame.Rect(LARGURA // 2 - 160, ALTURA // 2 - 100, 320, 200)
            cor_borda = VERDE_DESTAQUE if (self.modo_jogo == 1 and self.mensagem_transicao_adv) else AMARELO
            pygame.draw.rect(self.superficie_jogo, (18, 18, 24), rect_box, border_radius=12)
            pygame.draw.rect(self.superficie_jogo, cor_borda, rect_box, width=3, border_radius=12)

            if self.modo_jogo == 1 and self.mensagem_transicao_adv:
                txt_titulo = self.fonte_texto_bold.render(self.mensagem_transicao_adv, True, VERDE_DESTAQUE)
                rect_titulo = txt_titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 55))
                self.superficie_jogo.blit(txt_titulo, rect_titulo)

                txt_cont = self.fonte_contador.render(str(self.segundos_restantes), True, AMARELO)
                rect_cont = txt_cont.get_rect(center=(LARGURA // 2, ALTURA // 2 + 5))
                self.superficie_jogo.blit(txt_cont, rect_cont)

                txt_prox = self.fonte_texto_bold.render(f"Próximo: Adversário #{self.adversario_atual}", True, AMARELO)
                rect_prox = txt_prox.get_rect(center=(LARGURA // 2, ALTURA // 2 + 65))
                self.superficie_jogo.blit(txt_prox, rect_prox)
            else:
                txt_prep = self.fonte_subtitulo.render("PREPAREM-SE!", True, AMARELO)
                rect_prep = txt_prep.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
                self.superficie_jogo.blit(txt_prep, rect_prep)

                txt_cont = self.fonte_contador.render(str(self.segundos_restantes), True, AMARELO)
                rect_cont = txt_cont.get_rect(center=(LARGURA // 2, ALTURA // 2 + 8))
                self.superficie_jogo.blit(txt_cont, rect_cont)

                txt_sub = self.fonte_texto.render("A partida vai começar!", True, BRANCO)
                rect_sub = txt_sub.get_rect(center=(LARGURA // 2, ALTURA // 2 + 65))
                self.superficie_jogo.blit(txt_sub, rect_sub)

        # Contador de 2 segundos após ponto normal
        elif self.em_contagem_ponto:
            rect_box = pygame.Rect(LARGURA // 2 - 150, ALTURA // 2 - 95, 300, 190)

            if self.modo_jogo == 1:
                if self.ultimo_marcador == "esq":
                    cor_borda = VERDE_DESTAQUE
                    txt_titulo = "SEU PONTO!"
                else:
                    cor_borda = (235, 75, 75)
                    txt_titulo = "PONTO DA CPU!"
            else:
                cor_borda = AMARELO
                txt_titulo = "PONTO: JOGADOR 1" if self.ultimo_marcador == "esq" else "PONTO: JOGADOR 2"

            pygame.draw.rect(self.superficie_jogo, (18, 18, 24), rect_box, border_radius=12)
            pygame.draw.rect(self.superficie_jogo, cor_borda, rect_box, width=3, border_radius=12)

            txt_ponto = self.fonte_subtitulo.render(txt_titulo, True, cor_borda)
            rect_ponto = txt_ponto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
            self.superficie_jogo.blit(txt_ponto, rect_ponto)

            txt_cont = self.fonte_contador.render(str(self.segundos_restantes_ponto), True, AMARELO)
            rect_cont = txt_cont.get_rect(center=(LARGURA // 2, ALTURA // 2 + 5))
            self.superficie_jogo.blit(txt_cont, rect_cont)

            txt_prox = self.fonte_texto.render("Próxima bola em...", True, BRANCO)
            rect_prox = txt_prox.get_rect(center=(LARGURA // 2, ALTURA // 2 + 62))
            self.superficie_jogo.blit(txt_prox, rect_prox)

        # -------------------------------------------------------------
        # CAMADA 5: Efeito de Scanlines CRT e Tremor de Tela
        # -------------------------------------------------------------
        self.superficie_jogo.blit(self.partida_fundo.surf_scanlines, (0, 0))

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
