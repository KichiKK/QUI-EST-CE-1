import pygame
from math import ceil
from dico import *

 # Constantes
LARGEUR = 140
HAUTEUR = 130
NB_PAR_LIGNE = 8
ESPACEMENT = 10
MARGE_BASSE = 46
MAX_FPS = 60

class Jeu_Affichage:
    def __init__(self):
        pygame.init()
        self.pygame_initialized = False
        self.screen = None
        self.txt = None
        self.clock = pygame.time.Clock()
        self.enemies = []

        self.Lancer()

    def charger_image(self, perso):
        chemin = f"img/{perso}.jpg"
        try:
            img = pygame.image.load(chemin).convert()
            return pygame.transform.scale(img, (LARGEUR, HAUTEUR))
        except pygame.error:
            print(f"[Erreur] Image introuvable pour {perso} ({chemin})")
            img_vide = pygame.Surface((LARGEUR, HAUTEUR))
            img_vide.fill((200, 200, 200))
            return img_vide

    def initialiser_fenetre(self):
        if not self.pygame_initialized:
            pygame.font.init()
            nb_total = len(PERSONNAGES)
            lignes = ceil(nb_total / NB_PAR_LIGNE)
            largeur = NB_PAR_LIGNE * (LARGEUR + ESPACEMENT) + ESPACEMENT
            hauteur = lignes * (HAUTEUR + MARGE_BASSE) + ESPACEMENT
            self.screen = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
            pygame.display.set_caption("Jeu du qui-est-ce ?")
            self.txt = pygame.font.Font(None, 28)
            self.pygame_initialized = True

    def afficher(self, elimines):
        """
        Affiche le plateau de jeu à l'écran sans bloquer le programme
        """
        self.initialiser_fenetre()

        self.screen.fill((220, 220, 220))
        x = 0
        for perso in PERSONNAGES:
            if perso not in elimines:
                surf = pygame.Surface((LARGEUR, HAUTEUR + MARGE_BASSE))
                surf.fill((255, 255, 255))

                img = self.charger_image(perso)
                surf.blit(img, (0, 0))

                nom = self.txt.render(perso, True, (10, 10, 10))
                surf.blit(nom, ((LARGEUR - nom.get_width()) // 2, HAUTEUR + 5))

                col = x % NB_PAR_LIGNE
                row = x // NB_PAR_LIGNE
                pos_x = ESPACEMENT + col * (LARGEUR + ESPACEMENT)
                pos_y = ESPACEMENT + row * (HAUTEUR + MARGE_BASSE)
                self.screen.blit(surf, (pos_x, pos_y))
                x += 1

        pygame.display.flip()

    def Lancer(self):
        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.pos)

            self.afficher(self.enemies)
            self.clock.tick(MAX_FPS)

if __name__ == "__main__":
    jeu = Jeu_Affichage()