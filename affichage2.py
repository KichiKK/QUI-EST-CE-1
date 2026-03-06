import pygame
from math import *
from dico import *
from random import *
from time import *
from threading import Thread

class Jeu_Affichage:
    """
    Classe principale du "Qui-est-ce ?"
    """
    def __init__(self):
        """
        Le constructeur de la classe Jeu_Affichage et initialise le jeu
        """
        pygame.init()
        self.pygame_initialized = False
        self.clock = pygame.time.Clock()
        self.Clickable = {}
        self.cache_images = {}
        self.Text = {}
        self.state = "start"
        self.state_action = [dico_attribut]
        self.Players = {"Player1": {}, "Player2": {}}
        self.IsPlaying = "Player1"
        self.Winner_Player = None
        self.restart = False

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
            "Button" : ["deviner", "1vs1JOUEUR", "1vs1BOT", "rules_button"],
            "Color_List": [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128)],
            "MessageScale" : 7,
            "OutlineSize" : 3,
            "MessageClick": {
                "oui": ["Bien joué!", "Félicitations!", "Excellent!", "Continue!"], 
                "non": ["Raté!", "Essaie encore!", "Pas tout à fait!", "Presque!"]},
            "Anonyme" : False
        }

        self.Lancer()

    def get_frame(self, img, framez, nb_colonnes, nb_lignes):
        """
        Renvoie une partie précise d'une image donnée
        :param img: (pygame.Surface) Image source
        :param framez: (int) Numéro de la frame
        :param nb_colonnes: (int) Nombre de colonnes du sprite
        :param nb_lignes: (int) Nombre de lignes du sprite
        :return: (pygame.Surface) Frame extraite
        """
        assert isinstance(img, pygame.Surface), "img doit etre une Surface pygame"
        assert isinstance(nb_colonnes, int) and nb_colonnes > 0, "nb_colonnes doit etre un int > 0"
        assert isinstance(nb_lignes, int) and nb_lignes > 0, "nb_lignes doit etre un int > 0"
        assert isinstance(framez, (int, float)), "framez doit etre un int ou float"

        frame = int(framez)
        w = img.get_width() // nb_colonnes
        h = img.get_height() // nb_lignes
        
        col = frame % nb_colonnes
        row = frame // nb_colonnes
        
        return img.subsurface((col * w, row * h, w, h))
    
    def charger_image(self, Data):
        """
        Charge une image pour l'affichage
        :param Data: (dict) Un dictionnaire de configuration de l'image
        :return: (pygame.Surface) Une image prête à être affichée
        """
        assert isinstance(Data, dict), "Data doit etre un dict"
        Position = Data.get("Position") and Data["Position"] or (self.xfull/2,self.yfull/2)
        perso = Data["Nom"]
        boost = Data.get("Scale") and Data["Scale"] or 1
        Size = Data.get("Size") and Data["Size"] or (self.Parametre["LARGEUR"], self.Parametre["HAUTEUR"])
        Offset = Data.get("Offset") and  Data["Offset"] or (Position[0] + (randint(1,2) == 1 and self.xfull or -self.xfull), Position[1])
        goaloffset = Data.get("goaloffset") and Data["goaloffset"] or (0,0)
        MaxSizeTween = Data.get("MaxSizeTween") and Data["MaxSizeTween"] or self.Parametre["MaxSizeTween"]
        SpeedTween = Data.get("SpeedTween") and Data["SpeedTween"] or self.Parametre["TweenSizePerFrame"]
        IsButton = Data.get("IsButton") and Data["IsButton"] or False
        IsAdjectif = Data.get("IsAdjectif") and Data["IsAdjectif"] or False
        Text:str = Data.get("Text") and Data["Text"] or None
        Color = Data.get("Color") and Data["Color"] or False
        PngName = Data.get("Cover") and Data["Cover"] or perso
        IsFlipBook = Data.get("IsFlipBook") and Data["IsFlipBook"] or False
        DestroyFrame = Data.get("DestroyFrame") and Data["DestroyFrame"] or False
        LowerFrame = Data.get("LowerFrame") and Data["LowerFrame"] or 1
        TextSize = Text and (Data.get("TextSize") and Data["TextSize"] or 40)- len(Text)
        TextColor = Data.get("TextColor") and Data["TextColor"] or False

        if self.Parametre["Anonyme"]:
            for persoclass in PERSONNAGES:
                persoo = persoclass.nom
                if persoo == perso:
                    PngName = "person"

        if self.cache_images.get(perso) and self.cache_images[perso].get("Deleted") and self.cache_images[perso]["Deleted"]:
            del self.cache_images[perso]
             
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
            self.cache_images[perso] = {"DestroyFrame": DestroyFrame, "original": img,"IsFlipBook": IsFlipBook,"frame": 0, "img" : img,"boost": 1, "offset" : Offset, "goaloffset": goaloffset, "MaxSizeTween": MaxSizeTween, "SpeedTween": SpeedTween, "IsAdjectif": IsAdjectif, "IsButton": IsButton, "Color": Color}
            
            if self.cache_images[perso].get("Color"):
                self.Ajouter_Filtre(self.cache_images[perso]["img"], self.cache_images[perso]["Color"], 150)
            if Text:
                if Data.get("Outline") and Data["Outline"]:
                    OutlineSize = self.Parametre["OutlineSize"]
                    nom = self.Create_Texte({"Nom": perso + "_outline", "Text": str.upper(Text), "Size": TextSize+ OutlineSize/2, "Color": (0,0,0)})
                    img.blit(nom, (((img.get_width() - nom.get_width()) // 2 )+ OutlineSize, (img.get_height() - nom.get_height()) // 2))  

                nom = self.Create_Texte({"Nom": perso, "Text": str.upper(Text), "Size": TextSize, "Color": TextColor})
                img.blit(nom, ((img.get_width() - nom.get_width()) // 2, (img.get_height() - nom.get_height()) // 2)) 

        if self.cache_images[perso]["IsFlipBook"]:
            nb_col = self.cache_images[perso]["IsFlipBook"]["colonne"]
            nb_lig = self.cache_images[perso]["IsFlipBook"]["ligne"]
            frame = self.cache_images[perso]["frame"] % (nb_col * nb_lig)
            self.cache_images[perso]["img"] = self.get_frame(self.cache_images[perso]["original"], frame, nb_col, nb_lig)

        if self.cache_images[perso]["DestroyFrame"]:
            self.cache_images[perso]["DestroyFrame"] -= LowerFrame

        self.cache_images[perso]["frame"] += LowerFrame  

        return pygame.transform.scale(self.cache_images[perso]["img"], (Size[0] * boost, Size[1] * boost))

    def initialiser_fenetre(self):
        """
        Initialise la fenêtre pygame si elle n'est pas encore créée
        """
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
        """
        Renvoie l'image avec des bords arrondis
        :param surface: La surface à modifier
        :param radius: (int or float) Le rayon des coins arrondis
        :return: L'image modifiée avec coins arrondis
        """
        assert isinstance(surface, pygame.Surface), "surface doit etre une Surface pygame"
        assert isinstance(radius, (int, float)) and radius >= 0, "radius doit etre un int/float >= 0"
        border = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(border, (255,255,255), border.get_rect(), border_radius=radius)
        border.blit(surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        return border
    
    def clamp(self,n, min, max):
        """
        Permet de limiter une valeur entre un minimum et un maximum
        :param n: (int or float) Valeur à limiter
        :param min: (int or float) Valeur minimale
        :param max: (int or float) Valeur maximale
        :return: (int or float) Une valeur comprise entre le minimum et maximum
        """
        assert isinstance(n, (int, float)), "n doit etre un int/float"
        assert isinstance(min, (int, float)), "min doit etre un int/float"
        assert isinstance(max, (int, float)), "max doit etre un int/float"
        if n < min:
            return min
        elif n > max:
            return max
        else:   
            return n
        
    def Ajouter_Filtre(self, surface, color, opacite):
        """
        Ajoute un filtre sur une image
        :param surface: surface à modifier
        :param color: couleur du filtre
        :param opacite: niveau de transparence
        """
        assert isinstance(surface, pygame.Surface), "surface doit etre une Surface pygame"
        assert isinstance(color, (tuple, list)) and len(color) >= 3, "color doit etre un tuple/list de 3+ valeurs"
        assert isinstance(opacite, (int, float)) and 0 <= opacite <= 255, "opacite doit etre entre 0 et 255"
        filter = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        filter.fill((color[0], color[1], color[2], opacite))
        filter = self.surface_arrondi(filter, self.Parametre["BORDER_RADIUS"]) 
        surface.blit(filter, (0, 0))

    def lerp(self, a, b, t):
        """
        Renvoie une valeur compris entre deux nombres a et b
        :param a: (int or float) Première valeur
        :param b: (int or float) Seconde valeur
        :param t: (float) Portion de la distance entre a et b
        :return: (int ou float) Valeur comprise entre a et b
        """
        assert isinstance(a, (int, float)), "a doit etre un int/float"
        assert isinstance(b, (int, float)), "b doit etre un int/float"
        assert isinstance(t, (int, float)), "t doit etre un int/float"
        return (1 - t) * a + t * b
    
    def lerp_tuple(self, data):
        """
        Renvoie une position intermédiaire entre deux positions
        :param data: (dict) Un dictionnaire contenant les positions de départ et d'arrivée
        :return: (tuple) Une nouvelle position intermédiaire sous la forme d'un tuple
        """
        assert isinstance(data, dict), "data doit etre un dict"
        tuple = data["tuple"]
        tupleend = data["tupleend"]
        t = data.get("t") and data["t"] or self.Parametre["TweenMoveLerp"]

        return (self.lerp(tuple[0], tupleend[0], t), self.lerp(tuple[1], tupleend[1], t))

    def Get_Boost(self,perso):
        """
        Renvoie le facteur d'agrandissement d'un élement donné
        :param perso: (str) Le nom de l'élément
        :return: (int) La valeur du facteur d'agrandissement
        """
        assert isinstance(perso, str), "perso doit etre un str"
        Boost = 1
        if perso in self.cache_images:
            self.cache_images[perso]["boost"] = self.clamp(
            self.cache_images[perso]["boost"] + (self.Closest_Clickable_Func() == perso and self.cache_images[perso]["SpeedTween"] or -self.cache_images[perso]["SpeedTween"]),
            1,
            self.cache_images[perso]["MaxSizeTween"]
        )
            Boost = self.cache_images[perso]["boost"]
        return Boost
    
    def Get_Offset(self,data):
        """
        Calcule le décalage progressif d'un élément à l'écran
        :param data:(dict) Un dictionnaire contenant les informations de l'élément
        :return: (tuple) La position ajustée sous forme de tuple
        """
        assert isinstance(data, dict), "data doit etre un dict"
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

    def Add_Boutton(self, Data):
        """
        Crée et affiche un bouton à l'écran
        :param Data: (dict) dictionnaire contenant les informations du bouton
        :return: L'image du bouton affiché
        """
        assert isinstance(Data, dict), "Data doit etre un dict"
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
    
    def Add_Collidable(self, Surface, Nom, Position):
        """
        Ajoute une zone cliquable associée à une surface donnée
        :param Surface: La surface concernée
        :param Nom: (str) Le nom associé à la zone
        :param Position: (tuple) La position de la surface sous la forme d'un tuple de coordonnée x et y 
        """
        assert isinstance(Surface, pygame.Surface), "Surface doit etre une Surface pygame"
        assert isinstance(Nom, str), "Nom doit etre un str"
        assert isinstance(Position, tuple) and len(Position) == 2, "Position doit etre un tuple/list de 2 elements"
        pos_x,pos_y = Position
        size_x,size_y = Surface.get_size()
        rect = pygame.Rect(pos_x, pos_y, size_x, size_y)
        self.screen.blit(Surface, rect)
        self.Clickable[Nom] = rect

    def Remove_Collidable(self, Nom):
        """
        Supprime une zone cliquable
        :param Nom: (str) nom de la zone à supprimer
        """
        assert isinstance(Nom, str), "Nom doit etre un str"
        if self.Clickable.get(Nom):
            del self.Clickable[Nom]

    def afficher(self):
        """
        Affiche le plateau de jeu à l'écran sans bloquer le programme
        """
        x = 0
        Playing = self.IsPlaying
        if self.Players[Playing]["Bot"]:
            Playing = self.Get_Other_Player()
            
        elemines = self.Players[Playing].get("Elemines") and self.Players[Playing]["Elemines"]
        for persoclass in PERSONNAGES:
                perso = persoclass.nom
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

                if perso in elemines:
                    self.Ajouter_Filtre(surf, self.Parametre["ELEMINE_COLOR"], self.Parametre["ELEMINE_OPACITE"]) 

                Contour = (0, 0, 0)

                adj = self.get_adj(persoclass.attributs)
                Clickable =self.Closest_Clickable_Func()
                if Clickable and adj:
                    HaveAdj = self.Have_Adjectif({"Adjectif": Clickable, "Target_Adject": adj})
                    if HaveAdj:
                        Contour = (255,255,0)
                    
                    if self.Players[self.IsPlaying]["Character"] == "INPUT" and Clickable == perso:
                        Contour = (0,255,0)

                col = x % self.Parametre["NB_PAR_LIGNE"]
                row = x // self.Parametre["NB_PAR_LIGNE"]
                pos_x = self.Parametre["ESPACEMENT"] + col * (self.Parametre["LARGEUR"] + self.Parametre["ESPACEMENT"]) - ((self.Parametre["LARGEUR"]*Boost - self.Parametre["LARGEUR"]) / 2)
                pos_y = self.Parametre["ESPACEMENT"] + row * (self.Parametre["HAUTEUR"] + self.Parametre["MARGE_BASSE"] + self.Parametre["MARGE_BASSE_ENTRE_PERSO"]) 

                self.screen.blit(surf, (pos_x, pos_y))

                self.Add_Collidable(surf, perso, (pos_x, pos_y))

                pygame.draw.rect(
                    self.screen,
                    Contour,            
                    (pos_x, pos_y, Size_Finale[0], Size_Finale[1]),
                    width=2,              
                    border_radius=self.Parametre["BORDER_RADIUS"]     
                )

                pygame.draw.rect(
                    self.screen,
                    Contour,            
                    (pos_x, pos_y + img.get_height(), img.get_width(), 2),
                    width=2,              
                )
                pygame.draw.line(
                                self.screen,
                                Contour,            
                                (pos_x, pos_y + img.get_height()),
                                (pos_x + img.get_width() - 2, pos_y + img.get_height()),
                                3,              
                                )
                x += 1

    def NewState(self,Next):
        """
        Change l'état actuel du jeu
        :param Next: (str) Le nom du nouvel état du jeu
        """
        assert isinstance(Next, str), "Next doit etre un str"
        self.Parametre["IN_TRANSITION"] = True
        sleep(self.Parametre["DELAY_STATE"])
        self.state = Next
        self.Remove_All_Button()

    def Remove_Button(self, Button):
        """
        Supprime un bouton affiché à l'écran
        :param Button: (str) Nom du bouton à supprimer
        """
        assert isinstance(Button, str), "Button doit etre un str"
        self.Remove_Collidable(Button)
        self.cache_images[Button]["goaloffset"] = (randint(1,2) == 1 and self.xfull or -self.xfull, 0)
        self.cache_images[Button]["Deleted"] = True
        
    def Remove_All_Button(self):
        """
        Supprime tous les boutons actuellement présents à l'écran
        """
        for Button in self.cache_images:
            if self.cache_images[Button]["IsButton"]:
               self.Remove_Button(Button)
                
    def Click_Start(self, Boutton):
        """
        Lance le changement d'état après un clic sur un bouton du menu
        :param Boutton:(str) Le nom du bouton sélectionné
        """
        assert isinstance(Boutton, str), "Boutton doit etre un str"
        self.Remove_All_Button()
        Thread(target=lambda: self.NewState(Boutton)).start()

    def IsIterable(self, obj):
        """
        Prédicat renvoyant si l'objet est une liste ou un dictionnaire ou non
        :param obj: (any) L'objet à tester
        :return: (True or False) L'objet est une liste ou un dictionnaire, ou False sinon
        """
        assert obj is not None, "obj ne doit pas etre None"
        return isinstance(obj, list) or isinstance(obj, dict)

    def Have_Adjectif(self, Data):
        """
        Prédicat renvoyant si un adjectif correspond à la personne donnée
        :param Data: (dict) Dictionnaire contenant l'adjectif et la personne
        :return: True si l'adjectif correspond, False sinon
        """
        assert isinstance(Data, dict), "Data doit etre un dict"
        Adjectif = Data["Adjectif"]
        Target_Adject = Data["Target_Adject"]
        return str(Adjectif) == str(Target_Adject) or (self.IsIterable(Target_Adject) and Adjectif in Target_Adject)
    
    def get_adj(self, data):
        """
        Renvoie la liste des adjectifs correspondant à la catégorie parcourue
        :param data: (dict) Dictionnaire contenant les attributs d'un personnage
        :return: Une liste ou valeur correspondant à la catégorie sélectionnée
        """
        assert isinstance(data, dict), "data doit etre un dict"
        res = self.state_action[0].keys()
        if len(self.state_action) > 2:
            res = data.get(self.state_action[1]).get(self.state_action[2])
        elif len(self.state_action) > 1:
            res = data.get(self.state_action[1])
        return res
    
    def Random_Adjectif(self):
        """
        Sélectionne un adjectif aléatoirement dans le dictionnaire des attributs dico_attribut
        :return: Le chemin complet menant à cet adjectif
        """
        categorie = choice(list(dico_attribut.keys()))
        valeur = dico_attribut[categorie]

        Chemin = [dico_attribut]
        if isinstance(valeur, list):
            Chemin.extend([categorie, choice(valeur)])
        elif isinstance(valeur, dict):
            sous_cat = choice(list(valeur.keys()))
            Chemin.extend([categorie, sous_cat, choice(valeur[sous_cat])])
        return Chemin

    def Remove_Adjectif(self, Adjectif):
        """
        Compare l'adjectif choisi par le joueur afin d'éliminer les personnages qui ne correspondent pas
        :param Adjectif: (str) Adjectif sélectionné par le joueur
        """
        assert isinstance(Adjectif, str), "Adjectif doit etre un str"
        if str(self.state_action + [Adjectif]) not in self.Players[self.IsPlaying]["Adjectif_Used"]:
            elemines = self.Players[self.IsPlaying].get("Elemines") and self.Players[self.IsPlaying]["Elemines"]

            self.Players[self.IsPlaying]["Adjectif_Used"].append(str(self.state_action + [Adjectif]))

            Main_Character_Have_Adjectif = False

            data = self.Players[self.Get_Other_Player()]["Character"].attributs
            adj = self.get_adj(data)

            if self.Have_Adjectif({"Adjectif": Adjectif, "Target_Adject": adj}):
                Main_Character_Have_Adjectif = True  
    
            for perso in PERSONNAGES:
                adj = self.get_adj(perso.attributs)
                HaveAdj = self.Have_Adjectif({"Adjectif": Adjectif, "Target_Adject": adj})
                if Main_Character_Have_Adjectif and not HaveAdj and perso.nom not in elemines:
                    elemines.append(perso.nom)
                elif not Main_Character_Have_Adjectif and HaveAdj and perso.nom not in elemines:
                    elemines.append(perso.nom)

            self.Players[self.IsPlaying]["Score"] = self.Players[self.IsPlaying].get("Score", 0) + (Main_Character_Have_Adjectif and 1 or 0)
            
            self.BackToChoice()
            
            if len(elemines) < len(PERSONNAGES) - 1:
                self.Message_On_Screen(Text=choice(Main_Character_Have_Adjectif and self.Parametre["MessageClick"]["oui"] or self.Parametre["MessageClick"]["non"]), Color=Main_Character_Have_Adjectif and (0, 255, 0) or (255, 0, 0))
                self.Change_Player()

    def BackToChoice(self):
        """
        Retourne au choix de l'adjectif précédent et supprime les boutons affichés
        """
        self.state_action = [dico_attribut]
        self.Remove_All_Button()

    def Get_Other_Player(self):
        """
        Renvoie le nom de l'autre joueur
        :return: (str) Le nom de l'autre joueur
        """
        return self.IsPlaying == "Player2" and "Player1" or "Player2"
    
    def Change_Player(self):
        """
        Permet de passer au joueur suivant
        """
        if self.state != "deviner":
            self.Parametre["IN_TRANSITION"] = True
            self.IsPlaying = self.Get_Other_Player()
    
    def Get_Last_Adjectif(self):
        """
        Renvoie la catégorie ou la liste d'adjectifs correspondant à la position actuelle dans le dictionnaire d'attributs
        :return: Liste ou dictionnaire contenant les adjectifs disponibles
        """
        List_Actual = self.state_action[0]
        for key in self.state_action[1:]:
            List_Actual = List_Actual[key]
        return List_Actual

    def Adjectif_Click(self, Boutton):
        """
        Gère le clic sur un bouton correspondant à un adjectif ou une catégorie d'adjectifs
        :param Boutton: (str) Nom du bouton sélectionné
        """
        assert isinstance(Boutton, str), "Boutton doit etre un str"
        if isinstance(self.Get_Last_Adjectif(), dict) and (isinstance(self.Get_Last_Adjectif()[Boutton], dict) or isinstance(self.Get_Last_Adjectif()[Boutton], list)):
            self.Remove_All_Button()
            self.state_action.append(str(Boutton))
        else:
            self.Remove_Adjectif(str(Boutton))

    def Get_Last_State_Action(self):
         """
         Revient à l'étape précédente dans la navigation des catégories d'adjectifs
         """
         self.Remove_All_Button()
         self.state_action.pop()
    
    def Bouton_Retour(self):
        """
        Gère l'action du bouton retour afin de revenir à l'étape précédente ou de réinitialiser le jeu
        """
        if len(self.state_action) > 1:
            self.Get_Last_State_Action()
        else:
            self.Reset_Jeu()

    def Get_Character_With_Button(self,Boutton):
        """
        Renvoie le personnage correspondant au bouton sélectionné
        :param Boutton: (str) Nom du bouton sélectionné
        :return: Objet personnage correspondant ou None si aucun personnage ne correspond
        """
        assert isinstance(Boutton, str), "Boutton doit etre un str"
        for perso in PERSONNAGES:
            if perso.nom == Boutton:
                return perso

    def Clickable_Func(self):
        """
        Analyse le bouton actuellement sélectionné par le joueur et déclenche l'action correspondante
        """
        Boutton = self.Closest_Clickable_Func()
        if self.state == "rules_button" or (self.Winner_Player and self.cache_images.get("winner") and self.cache_images["winner"]["frame"] >= 120):
            self.Reset_Jeu()
        elif Boutton and self.state == "start":
                self.Click_Start(Boutton)
        elif Boutton and self.cache_images[Boutton]["IsAdjectif"]:
                self.Adjectif_Click(Boutton)
        elif Boutton and Boutton == "Retour":
                self.Bouton_Retour()
        elif Boutton and self.Get_Character_With_Button(Boutton):
            if self.Players.get(self.IsPlaying) and self.Players[self.IsPlaying].get("Character") and self.Players[self.IsPlaying]["Character"] == "INPUT":
                    self.Players[self.IsPlaying]["Character"] = self.Get_Character_With_Button(Boutton)
                
    def Remove_Filter(self,Button):
        """
        Supprime le filtre appliqué à une image et restaure son apparence originale
        :param Button: (str) Nom de l'image
        """
        assert isinstance(Button, str), "Button doit etre un str"
        self.cache_images[Button]["img"] = self.cache_images[Button]["original"].copy()

    def Create_Column_Button(self, Data):
        """
        Crée un bouton dans une colonne de sélection d'adjectifs
        :param Data: (dict) Dictionnaire contenant les paramètres du bouton
        :return: Nouvelle position et index utilisés pour placer le bouton suivant
        """
        assert isinstance(Data, dict), "Data doit etre un dict"
        Action_Param=Data["Action_Param"]
        Button = str(Data["Button"])
        color = Data.get("Color") and Data["Color"] or False
        IsAdjectif = Data.get("IsAdjectif") and Data["IsAdjectif"] or False

        x = Data["X"]
        y = Data["Y"]
        i = Data["i"]

        if i%Action_Param["Max_Button_Per_Column"] == 0 and i != 0:
                x +=  self.Parametre["Size_BOUTTON"][0] * Action_Param["Pourcent_Beetween_Button"]
                y = Action_Param["Y"]

        Final_Pos = (x+Action_Param["Column_Distance"] + Action_Param["Ecart_Left"], y)
        self.Add_Boutton({
            "Nom": Button, 
            "Cover" : "adjectif",
            "Scale": 0.01, 
            "Size": self.Parametre["Size_BOUTTON"],
            "SpeedTween" : .25,
            "goaloffset": Final_Pos,
            "IsButton": True,
            "MaxSizeTween": 1.15,
            "Text": Button,
            "Color" : color,
            "IsAdjectif": IsAdjectif,
            })

        self.Remove_Filter(Button)

        if str(self.state_action + [Button]) in self.Players[self.IsPlaying]["Adjectif_Used"]: 
             self.Ajouter_Filtre(self.cache_images[Button]["img"], self.Parametre["ELEMINE_COLOR"], self.Parametre["ELEMINE_OPACITE"])

        if Button == "Retour":
            self.cache_images[Button]["goaloffset"] = Final_Pos
        
        y += Action_Param["Add_Y"]
        i += 1

        return (x,y,i)
    
    def Create_Column(self, Data):
        """
        Crée une colonne de boutons correspondant aux adjectifs disponibles
        :param Data: (dict) Dictionnaire contenant la liste des adjectifs et les paramètres d'affichage
        """
        assert isinstance(Data, dict), "Data doit etre un dict"
        list = Data["list"]
        column = (Data.get("column") and Data["column"] or 1) - 1
        LenList = len(list) + 1

        Action_Param = {
                "X": -self.xfull/2 + self.Parametre["Size_BOUTTON"][0] / 2 , 
                "Y": self.yfull*.265,
                "Add_Y": self.Parametre["Size_BOUTTON"][1] + 10,
                "Max_Button_Per_Column": 4,
                "Column_Distance":(self.xfull / LenList ) * column,
                "Ecart_Left": self.Parametre["Size_BOUTTON"][0] / 4,
                "Pourcent_Beetween_Button" : 1.2
            }
        
        x = Action_Param["X"]
        y = Action_Param["Y"]
        i = 0
    
        x,y,i = self.Create_Column_Button({"Action_Param": Action_Param, "Color": (0,0,0), "i": i, "Button": "Retour", "X": x, "Y": y})

        for Button in list:
           x,y,i = self.Create_Column_Button({"Action_Param": Action_Param, "Button": Button, "Color": self.Parametre["Color_List"][len(self.state_action) - 1], "i": i, "X": x, "Y": y, "IsAdjectif": True})

    def Afficher_Action(self):
        """
        Affiche les boutons permettant au joueur de choisir un adjectif
        """
        self.Remove_Button_Start_Collidable()
        Color_List = self.Parametre["Color_List"]
        if len(self.state_action) > 0 and not self.Winner_Player:
            self.Create_Column({"list": self.Get_Last_Adjectif(), "column": 0, "color": Color_List[len(self.state_action) - 1]})
    
    def Setup_Player(self, Player,Bot = False):
        """
        Initialise les informations des joueurs
        :param Player: (str) Le nom du 1er joueur
        :param Bot: (bool) Indique si le 2nd joueur est joué automatiquement, par défaut à False
        """
        assert isinstance(Player, str), "Player doit etre un str"
        assert isinstance(Bot, bool), "Bot doit etre un bool"
        if self.Players[Player] == {}:
            self.Players[Player]["Character"] = Bot and choice(list(PERSONNAGES)) or "INPUT"
            self.Players[Player]["Elemines"] = []
            self.Players[Player]["Adjectif_Used"] = []
            self.Players[Player]["Bot"] = Bot

    def Playing_Bot(self):
        """
        Permet au bot de sélectionner automatiquement un adjectif et de jouer
        """
        if self.Players[self.IsPlaying]["Bot"]:
            Chemin = self.Random_Adjectif()
            Adjectif = Chemin.pop()
            self.state_action = Chemin
            self.Remove_Adjectif(Adjectif)
            
    def GameMode(self, bot):
        """
        Gère le déroulement du jeu selon le mode choisi
        :param bot: (bool) Indique si le second joueur est contrôlé par un bot ou non
        """
        assert isinstance(bot, bool), "bot doit etre un bool"
        if self.state != "deviner" and self.Players["Player1"]["Character"] == "INPUT":
            if not self.cache_images.get("Player 1: Choisissez votre personnage" + "_Message"):
                self.IsPlaying = "Player1"
                self.Message_On_Screen("Player 1: Choisissez votre personnage", Color=(0,0,255), Duration=20, TextSize=75, Outline = False)
        elif self.state != "deviner" and not bot and self.Players["Player2"]["Character"] == "INPUT":
            if not self.cache_images.get("Player 2: Choisissez votre personnage" + "_Message"):
                self.IsPlaying = "Player2"
                self.Message_On_Screen("Player 2: Choisissez votre personnage", Color=(0,0,255), Duration=20, TextSize=75, Outline = False)
        else:
            if self.state != "deviner" and len(self.Players["Player1"]["Elemines"]) == 0:
                self.IsPlaying = "Player1"
            self.Afficher_Action()

    def deviner_state(self):
        """
        Gère l'état du jeu dans lequel les joueurs doivent deviner le personnage adverse
        """
        bot = self.state != "1vs1JOUEUR" and True or False
        self.Setup_Player("Player1")
        self.Setup_Player("Player2", bot)
        self.Playing_Bot()
        self.afficher()
        self.GameMode(bot)

    def Winner(self):
        """
        Vérifie si un joueur a gagné la partie et affiche un message s'il a gagné
        """
        elemines = self.Players[self.IsPlaying].get("Elemines") and self.Players[self.IsPlaying]["Elemines"]
        if elemines and len(elemines) >= len(PERSONNAGES) - 1:
            Text = (self.Players[self.IsPlaying]["Bot"] and "Bot" or self.IsPlaying) + "| Score : " + str(int(1 / (self.Players[self.IsPlaying]["Score"] or 1) * 100))
            self.Winner_Player = Text
            self.Add_Boutton({
                    "Nom": "winner", 
                    "Scale": 1, 
                    "Size": (self.xfull, self.yfull*.55), 
                    "Offset": (-self.xfull*2, 0), 
                    "goaloffset": (0, 0), 
                    "notClickable": True,
                    "SpeedTween" : .15,
                    "Text": Text,
                    "Outline": True,
                    "TextSize": 140,
                    "TextColor": (255, 255, 255)
                })
        
    def Remove_Button_Start_Collidable(self):
        """
        Supprime les zones cliquables associées aux boutons du menu principal
        """
        for Button in self.Parametre["Button"]:
            self.Remove_Collidable(Button)
        
    def start_state(self):
        """
        Affiche les boutons du menu principal permettant de choisir le mode de jeu
        """
        pos =300
        for AllButton in self.Parametre["Button"]:
            self.Add_Boutton({
                "Nom": AllButton, 
                "Scale": 1.5, 
                "Size": self.Parametre["Size_BOUTTON"],
                "MaxSizeTween": 2,
                "SpeedTween" : .21,
                "goaloffset": (0, pos),
                "IsButton": True
                })
            pos -= 200

    def Afficher_Regle_Du_Jeu(self):
        """
        "Permet l'affichage des regles du jeu"
        """
        regle = self.Add_Boutton({
            "Nom": "rules", 
            "Scale": .2, 
            "Size": (self.xfull*.5, self.yfull*.8), 
            "Offset": (-self.xfull*2, 0), 
            "goaloffset": (0, 0), 
            "notClickable": True,
            "SpeedTween" : .08
            })

    def Afficher_State(self):
         """
         Affiche l'écran correspondant à l'état actuel du jeu
         """
         if self.state == "start":
            self.start_state()
         elif self.state == "rules_button":
            self.Afficher_Regle_Du_Jeu()
         else:
            self.deviner_state()

    def Reset_Jeu(self):
        """
        Arrête la partie actuelle et prépare le redémarrage du jeu
        """
        self.running = False
        self.restart = True

    def Events(self):
        """
        Analyse les événements pygame tels que les clics de souris ou la fermeture de la fenêtre
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.Clickable_Func()

    def Transition(self):   
        """
        Affiche une animation de transition entre deux états du jeu
        """          
        if self.Parametre["IN_TRANSITION"]:
            self.Add_Boutton({
                "Nom": "transition", 
                "Scale": 1, 
                "Size": (self.xfull, self.yfull), 
                "Offset": (-self.xfull*2, 0), 
                "goaloffset": (self.xfull*2, 0), 
                "notClickable": True,
                "SpeedTween" : .15
                })
            
    def Transition_Out(self):
        """
        Termine l'animation de transition et réactive le jeu normal
        """
        if self.Parametre["IN_TRANSITION"] and "transition" in self.cache_images and self.cache_images["transition"]["offset"][0] >= self.xfull:
            self.cache_images["transition"]["offset"] = (-self.xfull*2, 0)
            self.Parametre["IN_TRANSITION"] = False
    
    def Background(self):
        """
        Affiche un fond d'écran
        """
        backgroundtext = self.state == "1vs1JOUEUR" and str.lower(self.IsPlaying) or "background"
        self.Add_Boutton({
                "Nom": backgroundtext, 
                "Scale": 1, 
                "Size": (self.xfull, self.yfull), 
                "Offset": (0,0), 
                "goaloffset": (0,0), 
                "notClickable": True,
                "SpeedTween" : -1,
                })

    def Lancer(self):
        """
        Lance la boucle principale du jeu et met à jour l'affichage à chaque image
        """
        self.running = True
        while self.running:
            self.initialiser_fenetre()
            self.Background()
            self.Transition()
            self.Events()
            self.Afficher_State()
            self.Winner()
            self.Affiche_Message()
            self.Transition_Out()
            pygame.display.flip()
            self.clock.tick(self.Parametre["MAX_FPS"])
        if self.restart:
            Jeu_Affichage()

    def Create_Texte(self, Data):
        """
        Crée un texte destiné à être affiché à l'écran
        :param Data: (dict) Dictionnaire contenant les paramètres du texte
        :return: La surface contenant le texte généré
        """
        assert isinstance(Data, dict), "Data doit etre un dict"
        Nom = Data["Nom"]
        Size = int(Data.get("Size") and Data["Size"] or 30) 
        Color = Data.get("Color") and Data["Color"] or (10, 10, 10)
        Italic = Data.get("Italic") and Data["Italic"] or False
        Bold = Data.get("Bold") and Data["Bold"] or False
        if not self.Text.get(Nom):
            self.Text[Nom] = pygame.font.SysFont(None, Size)
            self.Text[Nom].italic = Italic
            self.Text[Nom].bold = Bold
        
        return self.Text[Nom].render(Data["Text"], True, Color)
    
    def Closest_Clickable_Func(self):
        """
        Renvoie le nom de l'élément cliquable actuellement situé sous la position de la souris
        :return: (str) Le nom de l'élément détecté sous le curseur de la souris
        """
        MousePos = pygame.mouse.get_pos()
        for perso, rect in self.Clickable.items():
            if rect.collidepoint(MousePos):
                return perso

    def Affiche_Message(self):
         '''
         Permet l'affichage de message temporaire en bas a droite
         '''
         if self.Parametre.get("MessageData"):
            Scale  = self.Parametre["MessageData"]["Scale"]
            Text  = self.Parametre["MessageData"]["Text"]
            Duration_Message = self.Parametre["MessageData"]["Duration_Message"]
            DestroyFrame_Smoke = self.Parametre["MessageData"]["DestroyFrame_Smoke"]
            Speed = self.Parametre["MessageData"]["Speed"]
            Position = self.Parametre["MessageData"].get("Position") and self.Parametre["MessageData"]["Position"] or (0, 0)
            Color = self.Parametre["MessageData"].get("Color") and self.Parametre["MessageData"]["Color"] or False
            TextSize = self.Parametre["MessageData"].get("TextSize") and self.Parametre["MessageData"]["TextSize"] or False
            Outline = self.Parametre["MessageData"].get("Outline") and self.Parametre["MessageData"]["Outline"] or False
            tweenspeed = .01

            if not self.cache_images.get(Text + "_Message") or self.cache_images[Text + "_Message"]["DestroyFrame"] > 0:

                if self.cache_images.get(Text + "_Message"):
                    if self.cache_images[Text + "_Message"]["DestroyFrame"]<= Duration_Message * .75:
                        self.cache_images[Text + "_Message"]["goaloffset"] = (self.xfull*2, Position[1])
                    else:
                        tweenspeed = 1
                        self.cache_images[Text + "_Message"]["goaloffset"] = Position
                
                self.Add_Boutton({
                        "Nom": Text + "_Message", 
                        "Scale": Scale, 
                        "Size": (25*Scale, 30*(Scale/2)), 
                        "Offset": Position, 
                        "goaloffset": Position, 
                        "notClickable": True,
                        "SpeedTween" : tweenspeed,
                        "Text": Text,
                        "TextSize": TextSize,
                        "TextColor": Color,
                        "Outline" : Outline,
                        "DestroyFrame": Duration_Message,
                        "Cover": "message", 
                        })
                   
            if not self.cache_images.get(Text + "_Smoke") or self.cache_images[Text + "_Smoke"]["DestroyFrame"] > 0:
                self.Add_Boutton({
                    "Nom": Text + "_Smoke", 
                    "Scale": Scale + 1.2, 
                    "Size": (25*Scale, 35*(Scale/2)), 
                    "Offset": Position, 
                    "goaloffset": Position, 
                    "notClickable": True,
                    "SpeedTween" : 1,
                    "Cover" : "smoke",
                    "IsFlipBook": {"colonne" : 4, "ligne": 4},
                    "DestroyFrame":DestroyFrame_Smoke,
                    "LowerFrame" : Speed
                    })

    def Message_On_Screen(self, Texttr, Duration=4,Scale=4, Color = (0,0,0), TextSize = 100, Outline = True):
        """
        Prépare l'affichage d'un message temporaire à l'écran
        :param Text: (str) Le texte à afficher
        :param Duration: (int or float) La durée d'affichage du texte en secondes
        :param Scale: (int) La taille du message
        :param Color: (tuple) La couleur du texte
        :param TextSize: (int) La taille de la police
        :param Outline: (bool) Indique si le texte possède un contour
        :cu: La durée, la taille du message et de la police doivent être positifs
        """
        assert isinstance(Text, str), "Text doit etre un str"
        assert isinstance(Duration, (int, float)) and Duration > 0, "Duration doit etre un int/float > 0"
        assert isinstance(Scale, (int, float)) and Scale > 0, "Scale doit etre un int/float > 0"
        assert isinstance(Color, tuple) and len(Color) >= 3, "Color doit etre un tuple de 3+ valeurs"
        assert isinstance(TextSize, (int, float)) and TextSize > 0, "TextSize doit etre un int/float > 0"
        assert isinstance(Outline, bool), "Outline doit etre un bool"
        DestroyFrame_Smoke = 4*4
        Speed = .5
        Duration_Message = Duration*60
        PourcentX, PourcentY = 0.25, 0.35
        Position = (self.xfull*PourcentX, self.yfull*PourcentY)
        if self.cache_images.get(Text + "_Message") and self.cache_images.get(Text + "_Smoke"):
                del self.cache_images[Text + "_Message"]
                del self.cache_images[Text + "_Smoke"]
        self.Parametre["MessageData"] = {
            "Scale": Scale,
            "Text": Text,
            "Duration_Message": Duration_Message,
            "DestroyFrame_Smoke": DestroyFrame_Smoke,
            "Speed": Speed,
            "Position": Position,
            "Color": Color,
            "TextSize":TextSize,
            "Outline" : Outline,
        }
    
if __name__ == "__main__": 
    jeu = Jeu_Affichage()