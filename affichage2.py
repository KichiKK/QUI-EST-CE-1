import pygame
from math import *
from dico import *

 # Constantes
LARGEUR = 140
HAUTEUR = 130
NB_PAR_LIGNE = 8
ESPACEMENT = 10
MARGE_BASSE = 46
MAX_FPS = 60
TAILLE_STATUS = 100
MARGE_BASSE_ENTRE_PERSO = 10
GAME_COLOR = (200,200,200)
BORDER_RADIUS = 15
TweenSizePerFrame = .01
MaxSizeTween = 1.1
ELEMINE_COLOR = (0,0,0)
ELEMINE_OPACITE = 200

class Jeu_Affichage:
    def __init__(self):
        pygame.init()
        self.pygame_initialized = False
        self.screen = None
        self.txt = None
        self.clock = pygame.time.Clock()
        self.enemies = []
        self.personnages_pos = {}
        self.cache_images = {}

        self.Lancer()

    def charger_image(self, perso, boost):
        if perso not in self.cache_images:
            try:
                chemin = f"img/{perso}.jpg"
                img = pygame.image.load(chemin).convert()
            except:
                print(f"[Erreur] Image introuvable pour {perso}")
                img = pygame.Surface((LARGEUR, HAUTEUR))
                img.fill(GAME_COLOR)
            self.cache_images[perso] = (img,1)
        base = self.cache_images[perso]
        return pygame.transform.scale(base[0], (int(LARGEUR * boost), int(HAUTEUR * boost)))

    def initialiser_fenetre(self):
        if not self.pygame_initialized:
            pygame.font.init()
            nb_total = len(PERSONNAGES)
            lignes = ceil(nb_total / NB_PAR_LIGNE)
            largeur = NB_PAR_LIGNE * (LARGEUR + ESPACEMENT) + ESPACEMENT
            hauteur = lignes * (HAUTEUR + MARGE_BASSE) + ESPACEMENT + TAILLE_STATUS
            self.screen = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
            pygame.display.set_caption("Jeu du qui-est-ce ?")
            self.txt = pygame.font.Font(None, 28)
            self.pygame_initialized = True

    def surface_arrondi(self, surface, radius):
        border = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(border, (255,255,255), border.get_rect(), border_radius=radius)
        border.blit(surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        return border
    
    def clamp(self,n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n
        
    def Ajouter_Filtre(self, surface:pygame.Surface, color, opacite):
        filter = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        filter.fill((color[0], color[1], color[2], opacite))
        filter = self.surface_arrondi(filter, BORDER_RADIUS)
        surface.blit(filter, (0, 0))

    def afficher(self, elimines):
        """
        Affiche le plateau de jeu à l'écran sans bloquer le programme
        """
        self.initialiser_fenetre()

        self.screen.fill((220, 220, 220))
        x = 0
        for perso in PERSONNAGES:
                Boost = 1
                if perso in self.cache_images:
                    self.cache_images[perso] = (self.cache_images[perso][0] ,self.clamp(self.cache_images[perso][1] + (self.Closest_Personnage(pygame.mouse.get_pos()) == perso and TweenSizePerFrame or -TweenSizePerFrame), 1, MaxSizeTween))
                    Boost = self.cache_images[perso][1]

                Size_Finale = (LARGEUR * Boost,(HAUTEUR + MARGE_BASSE - MARGE_BASSE_ENTRE_PERSO) * Boost)

                surf = pygame.Surface(Size_Finale)
                surf.fill((255, 255, 255))

                img = self.charger_image(perso, Boost)
                surf.blit(img, (0, 0))

                nom = self.txt.render(perso, True, (10, 10, 10))
                surf.blit(nom, ((Size_Finale[0] - nom.get_width()) // 2, (HAUTEUR * Boost) + 5))
                surf = self.surface_arrondi(surf,BORDER_RADIUS)

                surf = pygame.transform.scale(surf, Size_Finale)

                if perso in elimines:
                    self.Ajouter_Filtre(surf, ELEMINE_COLOR, ELEMINE_OPACITE)

                col = x % NB_PAR_LIGNE
                row = x // NB_PAR_LIGNE
                pos_x = ESPACEMENT + col * (LARGEUR + ESPACEMENT) - ((LARGEUR*Boost - LARGEUR)/2)
                pos_y = ESPACEMENT + row * (HAUTEUR + MARGE_BASSE + MARGE_BASSE_ENTRE_PERSO)

                self.personnages_pos[perso]= (pos_x + LARGEUR/2,pos_y + HAUTEUR/2)

                self.screen.blit(surf, (pos_x, pos_y))

                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),            
                    (pos_x, pos_y, Size_Finale[0], Size_Finale[1]),
                    width=2,              
                    border_radius=BORDER_RADIUS     
                )

                x += 1

        pygame.display.flip()

    def Lancer(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.Closest_Personnage(event.pos)

            self.afficher(self.enemies)
            self.clock.tick(MAX_FPS)

    def Closest_Personnage(self, MousePos:tuple) -> str:
        Closest = inf
        Char = None
        for key,pos in self.personnages_pos.items():
            calcx = pos[0] - MousePos[0]
            calcy = pos[1]- MousePos[1]
            d = abs(calcy) + abs(calcx)
            if d <= (HAUTEUR + LARGEUR)/2 and d < Closest:
                Closest = d
                Char = key
        return Char


    def Choisir_Personnage(self, bot:bool) -> str:
        if bot:
            print("Bot")
        else:
            print("zizi")
        

if __name__ == "__main__":
    jeu = Jeu_Affichage()