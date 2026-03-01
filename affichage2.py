from xml.dom.minidom import Text

import pygame
from math import *
from dico import *
from random import *
from time import *
from threading import *

class Jeu_Affichage:
    def __init__(self):
        pygame.init()
        self.pygame_initialized = False
        self.clock = pygame.time.Clock()
        self.elemines = []
        self.Clickable = {}
        self.cache_images = {}
        self.Text = {}
        self.state = "start"

        self.Parametre = {
            "TAILLE_STATUS": 100,
            "MARGE_BASSE_ENTRE_PERSO": 8.6,
            "GAME_COLOR": (155,155,155),
            "BORDER_RADIUS": 15,
            "TweenSizePerFrame": .01,
            "MaxSizeTween": 1.1,
            "ELEMINE_COLOR": (0,0,0),
            "ELEMINE_OPACITE": 200,
            "TweenMoveLerp": .1,
            "LARGEUR": 140,
            "HAUTEUR": 130,
            "NB_PAR_LIGNE": 8,
            "ESPACEMENT": 10,
            "MARGE_BASSE": 46,
            "MAX_FPS": 60,
            "DELAY_STATE": .11,
            "IN_TRANSITION": False,
            "Size_BOUTTON": (150, 50),
            "Size_Bottom": 200,
            "Button" : ["deviner", "BOT DEVINE", "1vs1JOUEUR", "1vs1BOT"],
            "Adjectif" : {
                        "Trait Physique": ["cheveux", "yeux", "accessoire", "barbe", "couleur de peau", "sourcil", "expression"],
                        "Accessoire": ["chapeau", "lunette", "collier", "boucle d'oreille", "casque", "masque", "serre-tete", "cravate"],
                        "Autres" : ["fond bleu", "fond nature", "fond rouge", "fond jaune", "fond vert", "fond violet", "fond rose"],
        }
        }

        self.Lancer()

    def charger_image(self, Data:dict):
        Position = Data.get("Position") and Data["Position"] or (self.xfull/2,self.yfull/2)
        perso = Data["Nom"]
        boost = Data.get("Scale") and Data["Scale"] or 1
        Size = Data.get("Size") and Data["Size"] or (self.Parametre["LARGEUR"], self.Parametre["HAUTEUR"])
        Offset = Data.get("Offset") and  Data["Offset"] or (Position[0] + (randint(1,2) == 1 and self.xfull or -self.xfull), Position[1])
        goaloffset = Data.get("GoalOffset") and Data["GoalOffset"] or (0,0)
        MaxSizeTween = Data.get("MaxSizeTween") and Data["MaxSizeTween"] or self.Parametre["MaxSizeTween"]
        SpeedTween = Data.get("SpeedTween") and Data["SpeedTween"] or self.Parametre["TweenSizePerFrame"]
        IsButton = Data.get("IsButton") and Data["IsButton"] or False
        Text:str = Data.get("Text") and Data["Text"] or None
        Color = Data.get("Color") and Data["Color"] or False
        PngName = Data.get("Cover") and Data["Cover"] or perso

        if perso not in self.cache_images:
            try:
                chemin = f"img/{PngName}.jpg"
                img = pygame.image.load(chemin).convert_alpha()
            except:
                try:
                    chemin = f"assets/{PngName}.png"
                    img = pygame.image.load(chemin).convert_alpha()
                except:
                    img = pygame.Surface(Size)
                    img.fill(self.Parametre["GAME_COLOR"]) 
            self.cache_images[perso] = {"img" : img,"boost": 1, "offset" : Offset, "goaloffset": goaloffset, "MaxSizeTween": MaxSizeTween, "SpeedTween": SpeedTween, "IsButton": IsButton, "Color": Color}
            if self.cache_images[perso].get("Color"):
                self.Ajouter_Filtre(self.cache_images[perso]["img"], self.cache_images[perso]["Color"], 150)
            if Text:
                nom = self.Create_Texte({"Nom": "Normal", "Text": Text, "Size": 36 - len(Text)})
                img.blit(nom, ((img.get_width() - nom.get_width()) // 2, (img.get_height() - nom.get_height()) // 2)) 

        base = self.cache_images[perso]
        return pygame.transform.scale(base["img"], (Size[0] * boost, Size[1] * boost))

    def initialiser_fenetre(self):
        if not self.pygame_initialized:
            pygame.font.init()
            nb_total = len(PERSONNAGES)
            lignes = ceil(nb_total / self.Parametre["NB_PAR_LIGNE"])
            largeur = self.Parametre["NB_PAR_LIGNE"] * (self.Parametre["LARGEUR"] + self.Parametre["ESPACEMENT"]) + self.Parametre["ESPACEMENT"]
            hauteur = lignes * (self.Parametre["HAUTEUR"] + self.Parametre["MARGE_BASSE"]) + self.Parametre["ESPACEMENT"] + self.Parametre["TAILLE_STATUS"] + self.Parametre["Size_Bottom"]
            self.screen = pygame.display.set_mode((largeur, hauteur))
            self.xfull,self.yfull = pygame.display.get_window_size()
            pygame.display.set_caption("Jeu du qui-est-ce ?")
            icon = self.charger_image({"Nom": "logo", "Size": (64, 64)})
            pygame.display.set_icon(icon)
            self.pygame_initialized = True            
        self.screen.fill(self.Parametre["GAME_COLOR"])

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
        filter = self.surface_arrondi(filter, self.Parametre["BORDER_RADIUS"]) 
        surface.blit(filter, (0, 0))

    def lerp(self, a: float, b: float, t: float) -> float:
        return (1 - t) * a + t * b
    
    def lerp_tuple(self, data:dict) -> tuple:
        tuple = data["tuple"]
        tupleend = data["tupleend"]
        t = data.get("t") and data["t"] or self.Parametre["TweenMoveLerp"]

        return (self.lerp(tuple[0], tupleend[0], t), self.lerp(tuple[1], tupleend[1], t))

    def Get_Boost(self,perso:str) -> int:
        Boost = 1
        if perso in self.cache_images:
            self.cache_images[perso]["boost"] = self.clamp(
            self.cache_images[perso]["boost"] + (self.Closest_Clickable(pygame.mouse.get_pos()) == perso and self.cache_images[perso]["SpeedTween"] or -self.cache_images[perso]["SpeedTween"]),
            1,
            self.cache_images[perso]["MaxSizeTween"]
        )
            Boost = self.cache_images[perso]["boost"]
        return Boost
    
    def Get_Offset(self,data:dict) -> tuple:
        perso = data["perso"]
        t = data.get("t") and data["t"] or self.Parametre["TweenMoveLerp"]

        Offset = (0,0)

        if perso in self.cache_images:
            self.cache_images[perso]["offset"] = self.lerp_tuple({
                "tuple": self.cache_images[perso]["offset"],
                "tupleend": self.cache_images[perso]["goaloffset"],
                "t": t
            })
            Offset = self.cache_images[perso]["offset"]
        return Offset

    def Add_Boutton(self, Data:dict):
        Nom = Data["Nom"]
        Scale = Data["Scale"]
        Position = Data.get("Position") and Data["Position"] or (self.xfull/2,self.yfull/2)
        notClickable = Data.get("notClickable") and Data["notClickable"] or False
        SpeedTween = Data.get("SpeedTween") and Data["SpeedTween"] or self.Parametre["TweenSizePerFrame"]

        Boost = self.Get_Boost(Nom)

        Data["Scale"] = Scale + Boost

        img = self.charger_image(Data)
        l,h = img.get_size()
        lw,hw = Position
        offsetx,offsety = self.Get_Offset({"perso": Nom, "t": SpeedTween})
        final_pos = ((lw - l/2) + offsetx, (hw - h/2) + offsety)
        self.screen.blit(img, final_pos)

        if not notClickable:
            self.Add_Collidable(img, Nom, final_pos)
        return img
    
    def Add_Collidable(self, Surface:pygame.Surface, Nom, Position):
        pos_x,pos_y = Position
        size_x,size_y = Surface.get_size()
        rect = pygame.Rect(pos_x, pos_y, size_x, size_y)
        self.screen.blit(Surface, rect)
        self.Clickable[Nom] = rect

    def Remove_Collidable(self, Nom):
        del self.Clickable[Nom]

    def afficher(self):
        """
        Affiche le plateau de jeu à l'écran sans bloquer le programme
        """
        x = 0
        for perso in PERSONNAGES:
                Boost = self.Get_Boost(perso)

                Size_Finale = (self.Parametre["LARGEUR"] * Boost, (self.Parametre["HAUTEUR"] + self.Parametre["MARGE_BASSE"] - self.Parametre["MARGE_BASSE_ENTRE_PERSO"]) * Boost)

                surf = pygame.Surface(Size_Finale)
                surf.fill((255, 255, 255))

                img = self.charger_image({"Nom": perso, "Scale": Boost})
                surf.blit(img, (0, 0))

                nom = self.Create_Texte({"Nom": "Bold_Italic", "Text": perso, "Bold": True, "Italic": True})

                surf.blit(nom, ((Size_Finale[0] - nom.get_width()) // 2, (self.Parametre["HAUTEUR"] * Boost) + 5))
                surf = self.surface_arrondi(surf, self.Parametre["BORDER_RADIUS"])

                surf = pygame.transform.scale(surf, Size_Finale)

                if perso in self.elemines:
                    self.Ajouter_Filtre(surf, self.Parametre["ELEMINE_COLOR"], self.Parametre["ELEMINE_OPACITE"]) 

                col = x % self.Parametre["NB_PAR_LIGNE"]
                row = x // self.Parametre["NB_PAR_LIGNE"]
                pos_x = self.Parametre["ESPACEMENT"] + col * (self.Parametre["LARGEUR"] + self.Parametre["ESPACEMENT"]) - ((self.Parametre["LARGEUR"]*Boost - self.Parametre["LARGEUR"]) / 2)
                pos_y = self.Parametre["ESPACEMENT"] + row * (self.Parametre["HAUTEUR"] + self.Parametre["MARGE_BASSE"] + self.Parametre["MARGE_BASSE_ENTRE_PERSO"]) 

                self.screen.blit(surf, (pos_x, pos_y))

                self.Add_Collidable(surf, perso, (pos_x, pos_y))

                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),            
                    (pos_x, pos_y, Size_Finale[0], Size_Finale[1]),
                    width=2,              
                    border_radius=self.Parametre["BORDER_RADIUS"]     
                )

                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),            
                    (pos_x, pos_y + img.get_height(), img.get_width(), 2),
                    width=2,              
                )
                pygame.draw.line(
                                self.screen,
                                (0, 0, 0),            
                                (pos_x, pos_y + img.get_height()),
                                (pos_x + img.get_width() - 2, pos_y + img.get_height()),
                                3,              
                                )
                x += 1

    def NewState(self,Next):
        self.Parametre["IN_TRANSITION"] = True
        sleep(self.Parametre["DELAY_STATE"])
        self.state = Next

    def ChangeState(self):
            Boutton = self.Closest_Clickable(pygame.mouse.get_pos())
            if Boutton and self.state == "start":
                for AllButton in self.cache_images:
                    if self.cache_images[AllButton]["IsButton"]:
                        self.Remove_Collidable(AllButton)
                        self.cache_images[AllButton]["goaloffset"] = (randint(1,2) == 1 and self.xfull or -self.xfull, 0)

                Thread(target=lambda: self.NewState(Boutton)).start()

    def CreateColumn_Button(self, Data:dict):
        list = Data["list"]
        column = (Data.get("column") and Data["column"] or 1) - 1
        color = Data.get("color") and Data["color"] or False

        Action_Param = {
                "X": -self.xfull/2 + self.Parametre["Size_BOUTTON"][0] / 2 , 
                "Y": self.yfull*.265,
                "Add_Y": self.Parametre["Size_BOUTTON"][1] + 10,
                "Max_Button_Per_Column": 4,
                "Column_Distance":(self.xfull / len(self.Parametre["Adjectif"]) ) * column,
                "Ecart_Left": self.Parametre["Size_BOUTTON"][0] / 4,
                "Pourcent_Beetween_Button" : 1.2
            }
        
        x = Action_Param["X"]
        y = Action_Param["Y"]
        i = 0
    
        for AllButton in list:
            if i%Action_Param["Max_Button_Per_Column"] == 0 and i != 0:
                x = Action_Param["X"] + self.Parametre["Size_BOUTTON"][0] * Action_Param["Pourcent_Beetween_Button"]
                y = Action_Param["Y"]

            self.Add_Boutton({
                "Nom": AllButton, 
                "Cover" : "adjectif",
                "Scale": 0.01, 
                "Size": self.Parametre["Size_BOUTTON"],
                "SpeedTween" : .1,
                "GoalOffset": (x+Action_Param["Column_Distance"] + Action_Param["Ecart_Left"], y),
                "IsButton": True,
                "MaxSizeTween": 1.15,
                "Text": AllButton,
                "Color" : color,
                })
            
            y += Action_Param["Add_Y"]
            i += 1

    def Afficher_Action(self):
        self.CreateColumn_Button({"list": self.Parametre["Adjectif"]["Trait Physique"], "column": 1, "color": (255, 0, 0)})
        self.CreateColumn_Button({"list": self.Parametre["Adjectif"]["Accessoire"], "column": 2, "color": (0, 255, 0)})
        self.CreateColumn_Button({"list": self.Parametre["Adjectif"]["Autres"], "column": 3, "color": (0, 0, 255)})
        
    def Afficher_State(self):
         if self.state == "start":
                pos = 300
                for AllButton in self.Parametre["Button"]:
                    self.Add_Boutton({
                        "Nom": AllButton, 
                        "Scale": 1.5, 
                        "Size": self.Parametre["Size_BOUTTON"],
                        "MaxSizeTween": 2,
                        "SpeedTween" : .21,
                        "GoalOffset": (0, pos),
                        "IsButton": True
                        })
                    pos -= 200
                
         elif self.state == "deviner": 
               self.afficher()
               self.Afficher_Action()
    
    def Events(self):
        res = True
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    res = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.ChangeState()
        return res
        
    def Transition(self):            
        if self.Parametre["IN_TRANSITION"]:
            transition = self.Add_Boutton({
                "Nom": "transition", 
                "Scale": 1, 
                "Size": (self.xfull, self.yfull), 
                "Offset": (-self.xfull*2, 0), 
                "GoalOffset": (self.xfull*2, 0), 
                "notClickable": True,
                "SpeedTween" : .15
                })
            
    def Transition_Out(self):
       if self.Parametre["IN_TRANSITION"] and "transition" in self.cache_images and self.cache_images["transition"]["offset"][0] >= self.xfull:
            self.cache_images["transition"]["offset"] = (-self.xfull*2, 0)
            self.Parametre["IN_TRANSITION"] = False
    
    def Background(self):
        transition = self.Add_Boutton({
                "Nom": "background", 
                "Scale": 1, 
                "Size": (self.xfull, self.yfull), 
                "Offset": (0,0), 
                "GoalOffset": (0,0), 
                "notClickable": True,
                "SpeedTween" : -1
                })

    def Lancer(self):
        running = True
        while running:
            self.initialiser_fenetre()
            self.Background()
            self.Transition()
            self.Afficher_State()
            running = self.Events()
            self.Transition_Out()
            pygame.display.flip()
            self.clock.tick(self.Parametre["MAX_FPS"])

    def Create_Texte(self, Data:dict):
        Nom = Data["Nom"]
        Size = Data.get("Size") and Data["Size"] or 30
        Color = Data.get("Color") and Data["Color"] or (10, 10, 10)
        Italic = Data.get("Italic") and Data["Italic"] or False
        Bold = Data.get("Bold") and Data["Bold"] or False
        if not self.Text.get(Nom):
            self.Text[Nom] = pygame.font.SysFont(None, Size)
            self.Text[Nom].italic = Italic
            self.Text[Nom].bold = Bold

        return self.Text[Nom].render(Data["Text"], True, Color)
    
    def Closest_Clickable(self, MousePos:tuple) -> str:
        for perso, rect in self.Clickable.items():
            if rect.collidepoint(MousePos):
                return perso

    def Choisir_Personnage(self, bot:bool) -> str:
        if bot:
            print("Bot")
        else:
            print("zizi")
        
if __name__ == "__main__":
    jeu = Jeu_Affichage()