import pygame
import sys
import random

# Constantes de configuração
LARGURA = 800
ALTURA = 600
TITULO = "Pong"
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)

# Dimensões dos elementos
LARGURA_PALETE = 15
ALTURA_PALETE = 90
VEL_PALETE = 6

TAMANHO_BOLA = 15
VEL_INICIAL_BOLA = 5


class PongGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("consolas", 48)
        self.fonte_instrucoes = pygame.font.SysFont("consolas", 18)

        # Paletes
        self.palete_esq = pygame.Rect(30, (ALTURA - ALTURA_PALETE) // 2, LARGURA_PALETE, ALTURA_PALETE)
        self.palete_dir = pygame.Rect(LARGURA - 30 - LARGURA_PALETE, (ALTURA - ALTURA_PALETE) // 2, LARGURA_PALETE, ALTURA_PALETE)

        # Bola
        self.bola = pygame.Rect((LARGURA - TAMANHO_BOLA) // 2, (ALTURA - TAMANHO_BOLA) // 2, TAMANHO_BOLA, TAMANHO_BOLA)
        self.vel_bola_x = 0
        self.vel_bola_y = 0

        # Pontuação
        self.pontos_esq = 0
        self.pontos_dir = 0

        self.reiniciar_bola()

    def reiniciar_bola(self):
        self.bola.center = (LARGURA // 2, ALTURA // 2)
        direcao_x = random.choice([-1, 1])
        direcao_y = random.choice([-0.7, -0.4, 0.4, 0.7])
        self.vel_bola_x = direcao_x * VEL_INICIAL_BOLA
        self.vel_bola_y = direcao_y * VEL_INICIAL_BOLA

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                if evento.key == pygame.K_r:
                    self.pontos_esq = 0
                    self.pontos_dir = 0
                    self.reiniciar_bola()
        return True

    def atualizar(self):
        teclas = pygame.key.get_pressed()

        # Movimento do Jogador 1 (W / S)
        if teclas[pygame.K_w] and self.palete_esq.top > 0:
            self.palete_esq.y -= VEL_PALETE
        if teclas[pygame.K_s] and self.palete_esq.bottom < ALTURA:
            self.palete_esq.y += VEL_PALETE

        # Movimento do Jogador 2 (Setas Cima / Baixo)
        if teclas[pygame.K_UP] and self.palete_dir.top > 0:
            self.palete_dir.y -= VEL_PALETE
        if teclas[pygame.K_DOWN] and self.palete_dir.bottom < ALTURA:
            self.palete_dir.y += VEL_PALETE

        # Movimento da Bola
        self.bola.x += int(self.vel_bola_x)
        self.bola.y += int(self.vel_bola_y)

        # Colisão com o teto e chão
        if self.bola.top <= 0:
            self.bola.top = 0
            self.vel_bola_y *= -1
        elif self.bola.bottom >= ALTURA:
            self.bola.bottom = ALTURA
            self.vel_bola_y *= -1

        # Colisão com palete esquerda
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

        # Limitar velocidade máxima para não atravessar paredes
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

    def desenhar(self):
        self.tela.fill(PRETO)

        # Linha pontilhada central
        passo = 15
        for y in range(0, ALTURA, passo * 2):
            pygame.draw.rect(self.tela, CINZA, (LARGURA // 2 - 2, y, 4, passo))

        # Paletes e Bola
        pygame.draw.rect(self.tela, BRANCO, self.palete_esq)
        pygame.draw.rect(self.tela, BRANCO, self.palete_dir)
        pygame.draw.ellipse(self.tela, BRANCO, self.bola)

        # Placar
        texto_esq = self.fonte.render(str(self.pontos_esq), True, BRANCO)
        texto_dir = self.fonte.render(str(self.pontos_dir), True, BRANCO)
        self.tela.blit(texto_esq, (LARGURA // 4 - texto_esq.get_width() // 2, 30))
        self.tela.blit(texto_dir, (3 * LARGURA // 4 - texto_dir.get_width() // 2, 30))

        # Instruções no rodapé
        instrucoes = self.fonte_instrucoes.render("P1: W/S | P2: Setas | R: Reiniciar | ESC: Sair", True, CINZA)
        self.tela.blit(instrucoes, (LARGURA // 2 - instrucoes.get_width() // 2, ALTURA - 30))

        pygame.display.flip()

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
