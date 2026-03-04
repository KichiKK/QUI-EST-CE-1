from xml.dom.minidom import Text

from h11 import Data
import pygame
from math import *
from dico import *
from random import *
from time import *
from threading import Thread

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
        self.state_action = [dico_attribut]
        self.Players = {"Player1": {}, "Player2": {}}
        self.IsPlaying = "Player1"
        self.Adjectif_Used = []
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
            "Button" : ["deviner", "BOT DEVINE", "1vs1JOUEUR", "1vs1BOT"],
            "Color_List": [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128)],
            "MessageScale" : 7,
            "OutlineSize" : 3,
            "MessageClick": {
                "oui": ["Bien joué!", "Félicitations!", "Excellent!", "Continue!"], 
                "non": ["Raté!", "Essaie encore!", "Pas tout à fait!", "Presque!"]},
        }

        self.Lancer()

    def get_frame(self, img:pygame.Surface, framez, nb_colonnes, nb_lignes):
        frame = int(framez)
        w = img.get_width() // nb_colonnes
        h = img.get_height() // nb_lignes
        
        col = frame % nb_colonnes
        row = frame // nb_colonnes
        
        return img.subsurface((col * w, row * h, w, h))
    
    def charger_image(self, Data:dict):
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
        TextSize = Data.get("TextSize") and Data["TextSize"] or 40
        TextColor = Data.get("TextColor") and Data["TextColor"] or False
        
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
                    nom = self.Create_Texte({"Nom": perso + "_outline", "Text": str.upper(Text), "Size": TextSize+ OutlineSize/2 - len(Text), "Color": (0,0,0)})
                    img.blit(nom, (((img.get_width() - nom.get_width()) // 2 )+ OutlineSize, (img.get_height() - nom.get_height()) // 2))  

                nom = self.Create_Texte({"Nom": perso, "Text": str.upper(Text), "Size": TextSize - len(Text), "Color": TextColor})
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
            self.cache_images[perso]["boost"] + (self.Closest_Clickable_Func(pygame.mouse.get_pos()) == perso and self.cache_images[perso]["SpeedTween"] or -self.cache_images[perso]["SpeedTween"]),
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
        if self.Clickable.get(Nom):
            del self.Clickable[Nom]

    def afficher(self):
        """
        Affiche le plateau de jeu à l'écran sans bloquer le programme
        """
        x = 0
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
        self.Remove_All_Button()

    def Remove_Button(self, Button):
        self.Remove_Collidable(Button)
        self.cache_images[Button]["goaloffset"] = (randint(1,2) == 1 and self.xfull or -self.xfull, 0)
        self.cache_images[Button]["Deleted"] = True
        
    def Remove_All_Button(self):
        for Button in self.cache_images:
            if self.cache_images[Button]["IsButton"]:
               self.Remove_Button(Button)
                
    def Click_Start(self, Boutton):
        self.Remove_All_Button()
        Thread(target=lambda: self.NewState(Boutton)).start()

    def IsIterable(self, obj):
        return isinstance(obj, list) or isinstance(obj, dict)

    def Have_Adjectif(self, Data):
        Adjectif = Data["Adjectif"]
        Target_Adject = Data["Target_Adject"]
        return str(Adjectif) == str(Target_Adject) or (self.IsIterable(Target_Adject) and Adjectif in Target_Adject)
    
    def get_adj(self, data:dict):
        res = data.get(self.state_action[1])
        if len(self.state_action) > 2:
            res = data.get(self.state_action[1]).get(self.state_action[2])
        return res
        
    def Remove_Adjectif(self, Adjectif):
        if str(self.state_action + [Adjectif]) not in self.Adjectif_Used:
            self.Adjectif_Used.append(str(self.state_action + [Adjectif]))
            self.Ajouter_Filtre(self.cache_images[Adjectif]["img"], self.Parametre["ELEMINE_COLOR"], self.Parametre["ELEMINE_OPACITE"])

            Main_Character_Have_Adjectif = False

            OtherPlayer = "Player1" if self.IsPlaying == "Player2" else "Player2"
            data = self.Players[OtherPlayer]["Character"].attributs
            adj = self.get_adj(data)
            if self.Have_Adjectif({"Adjectif": Adjectif, "Target_Adject": adj}):
                Main_Character_Have_Adjectif = True  
    
            for perso in PERSONNAGES:
                data = perso.attributs
                adj = self.get_adj(data)
                HaveAdj = self.Have_Adjectif({"Adjectif": Adjectif, "Target_Adject": adj})
                if Main_Character_Have_Adjectif and not HaveAdj and perso.nom not in self.elemines:
                    self.elemines.append(perso.nom)
                elif not Main_Character_Have_Adjectif and HaveAdj and perso.nom not in self.elemines:
                    self.elemines.append(perso.nom)

            self.Players[self.IsPlaying]["Score"] = self.Players[self.IsPlaying].get("Score", 0) + (Main_Character_Have_Adjectif and 1 or 0)
            self.Message_On_Screen(Text=choice(Main_Character_Have_Adjectif and self.Parametre["MessageClick"]["oui"] or self.Parametre["MessageClick"]["non"]), Color=Main_Character_Have_Adjectif and (0, 255, 0) or (255, 0, 0))

    def Get_Last_Adjectif(self):
        List_Actual = self.state_action[0]
        for key in self.state_action[1:]:
            List_Actual = List_Actual[key]
        return List_Actual

    def Adjectif_Click(self, Boutton):
            if isinstance(self.Get_Last_Adjectif(), dict) and (isinstance(self.Get_Last_Adjectif()[Boutton], dict) or isinstance(self.Get_Last_Adjectif()[Boutton], list)):
                self.Remove_All_Button()
                self.state_action.append(str(Boutton))
            else:
                self.Remove_Adjectif(str(Boutton))

    def Get_Last_State_Action(self):
         self.Remove_All_Button()
         self.state_action.pop()
    
    def Bouton_Retour(self):
        if len(self.state_action) > 1:
            self.Get_Last_State_Action()
        else:
            self.Reset_Jeu()

    def Clickable_Func(self):
            Boutton = self.Closest_Clickable_Func(pygame.mouse.get_pos())
            if self.Winner_Player:
                self.Reset_Jeu()
            elif Boutton and self.state == "start":
                 self.Click_Start(Boutton)
            elif Boutton and self.state == "deviner" and  self.cache_images[Boutton]["IsAdjectif"]:
                 self.Adjectif_Click(Boutton)
            elif Boutton and self.state == "deviner" and  Boutton == "Retour":
                 self.Bouton_Retour()
                 
    def Create_Column_Button(self, Data:dict):
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

        if str(self.state_action + [Button]) in self.Adjectif_Used and self.cache_images[Button]["frame"] == 1: 
             self.Ajouter_Filtre(self.cache_images[Button]["img"], self.Parametre["ELEMINE_COLOR"], self.Parametre["ELEMINE_OPACITE"])

        if Button == "Retour":
            self.cache_images[Button]["goaloffset"] = Final_Pos
        
        y += Action_Param["Add_Y"]
        i += 1

        return (x,y,i)
    
    def Create_Column(self, Data:dict):
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
        self.Remove_Button_Start_Collidable()
        Color_List = self.Parametre["Color_List"]
        if len(self.state_action) > 0:
            self.Create_Column({"list": self.Get_Last_Adjectif(), "column": 0, "color": Color_List[len(self.state_action) - 1]})
    
    def Set_Personnage(self, Player):
        if self.Players[Player] == {}:
                self.Players[Player]["Character"] = self.Choisir_Personnage(True)

    def deviner_state(self):
            self.Set_Personnage("Player2")
            self.afficher()
            self.Afficher_Action()

    def Winner(self):
        if len(self.elemines) >= len(PERSONNAGES) - 1:
            Text = self.IsPlaying+ "| Score : " + str(self.Players[self.IsPlaying]["Score"])
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
                    "TextSize": 150,
                    "TextColor": (255, 255, 255)
                    })
        
    def Remove_Button_Start_Collidable(self):
        for Button in self.Parametre["Button"]:
            self.Remove_Collidable(Button)
        
    def start_state(self):
        pos = 300
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
                
    def Afficher_State(self):
         if self.state == "start":
                self.start_state()
         elif self.state == "deviner": 
               self.deviner_state()

    def Reset_Jeu(self):
        self.running = False
        self.restart = True

    def Events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.Clickable_Func()

    def Transition(self):            
        if self.Parametre["IN_TRANSITION"]:
            transition = self.Add_Boutton({
                "Nom": "transition", 
                "Scale": 1, 
                "Size": (self.xfull, self.yfull), 
                "Offset": (-self.xfull*2, 0), 
                "goaloffset": (self.xfull*2, 0), 
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
                "goaloffset": (0,0), 
                "notClickable": True,
                "SpeedTween" : -1
                })

    def Lancer(self):
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

    def Create_Texte(self, Data:dict):
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
    
    def Closest_Clickable_Func(self, MousePos:tuple) -> str:
        for perso, rect in self.Clickable.items():
            if rect.collidepoint(MousePos):
                return perso

    def Affiche_Message(self):
         if self.Parametre.get("MessageData"):
            Scale  = self.Parametre["MessageData"]["Scale"]
            Text  = self.Parametre["MessageData"]["Text"]
            Duration_Message = self.Parametre["MessageData"]["Duration_Message"]
            DestroyFrame_Smoke = self.Parametre["MessageData"]["DestroyFrame_Smoke"]
            Speed = self.Parametre["MessageData"]["Speed"]
            Position = self.Parametre["MessageData"].get("Position") and self.Parametre["MessageData"]["Position"] or (0, 0)
            Color = self.Parametre["MessageData"].get("Color") and self.Parametre["MessageData"]["Color"] or False
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
                        "TextSize": 100,
                        "TextColor": Color,
                        "Outline" : True,
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

    def Message_On_Screen(self, Text:str, Duration:float=4,Scale:int=4, Color = (0,0,0)):
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
            "Color": Color
        }

    def Choisir_Personnage(self, bot:bool) -> str:
        res = None
        if bot:
            res = choice(list(PERSONNAGES))
        else:
            print("zizi")
        return res
        
if __name__ == "__main__": 
    jeu = Jeu_Affichage()