import gpxpy
import pandas
import pygame
import numpy as np

def distance(point1, point2):
    return ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**0.5

def temps_en_secondes(temps):
    temps = str(temps)
    if temps in ["nan", "Abandon", "Disqualifié"]:
        return -1
    temps = tuple(map(int, temps.split(':')))
    if len(temps) == 1: #ss
        return temps[0]
    elif len(temps) == 2: #mm:ss
        return 60*temps[0] + temps[1]
    elif len(temps) == 3: #hh:mm:ss
        return 3600*temps[0] + 60*temps[1] + temps[2]
    else:
        print(temps)
        return -1

def creer_texte(nom, taille, gras, italique, couleur):
    global dicoPolices
    if taille not in dicoPolices:
        dicoPolices[taille] = pygame.font.SysFont("Arial", taille, bold=gras, italic=italique)
    return dicoPolices[taille].render(nom, True, couleur)
dicoPolices = {}

def creer_image(texte, rayon, couleurFond):
    fond = pygame.Surface((2*rayon, 2*rayon), pygame.SRCALPHA)
    pygame.draw.circle(surface=fond, color=couleurFond, center=(rayon, rayon), radius=rayon)
    surfaceTexte = creer_texte(nom=texte, taille=round(1.5*rayon), gras=True, italique=False, couleur=(255,255,255))
    fond.blit(surfaceTexte, ((2*rayon-surfaceTexte.get_width())/2, (2*rayon-surfaceTexte.get_height())/2))
    return fond


class Athlete(object):
    def __init__(self, simulation, lVitesses, listeLPoints, rayon, couleur, nom, place):
        self.actif = True
        self.simulation = simulation

        self.lVitesses = lVitesses
        self.listeLPoints = listeLPoints
        self.rayon = rayon
        self.couleur = couleur
        self.nom = nom
        self.place = place
        self.image = creer_image(texte=str(self.place), rayon=self.rayon, couleurFond=self.couleur)
        self.wI, self.hI = self.image.get_size()

        self.yMin, self.yMax = 0.10, 0.50
        
        self.reset(reel=False)

    def reset(self, reel=True):
        self.actif = True

        self.iParcours = 0
        self.iProchainPoint = 1
        self.x, self.y = self.listeLPoints[self.iParcours][0]
        self.dist = 0

        if reel:
            self.changer_texte()

    def avancer_n_metres(self, deltaDist):
        changementParcours = False
        while self.actif and distance((self.x, self.y), self.listeLPoints[self.iParcours][self.iProchainPoint]) <= deltaDist:
            deltaDist -= distance((self.x, self.y), self.listeLPoints[self.iParcours][self.iProchainPoint])
            self.x, self.y = self.listeLPoints[self.iParcours][self.iProchainPoint]
            self.iProchainPoint += 1
            if self.iProchainPoint >= len(self.listeLPoints[self.iParcours]):
                changementParcours = True
                self.iParcours += 1
                self.iProchainPoint = 1
                if self.iParcours >= len(self.listeLPoints):
                    self.actif = False
                self.changer_texte()
        return changementParcours

    def bouger(self):
        if not self.actif :
            return
        deltaDist = self.lVitesses[self.iParcours]
        self.dist += deltaDist
        changementParcours = self.avancer_n_metres(deltaDist=deltaDist)
        
        if self.actif :
            x2, y2 = self.listeLPoints[self.iParcours][self.iProchainPoint]
            dist = distance((self.x, self.y), (x2, y2))
            self.x += deltaDist * (x2-self.x) / dist
            self.y += deltaDist * (y2-self.y) / dist

        return changementParcours

    def afficher(self):
        if self.texte is not None:
            fenetre.blit(self.texte, self.positionTexte)
        if self.actif :
            self.simulation.fondParcours.blit(self.image, (self.x-self.wI/2, self.y-self.hI/2))

    def changer_texte(self):
        if self.nom not in self.simulation.dicoNoms:
            self.texte = None
            return
        self.placeActu = 1+self.simulation.lAthletes.index(self)
        self.texte = creer_texte(nom=f"{self.nom} : {self.placeActu} => {"Départ" if not self.simulation.depart else "Arrivée" if not self.actif else self.simulation.lParcours[self.iParcours]}", taille=20, gras=True, italique=False, couleur=self.couleur)
        self.yMilieuTexte = (self.yMin + ((self.simulation.lAthletesNoms).index(self)+0.5)*(self.yMax-self.yMin) / (len(self.simulation.dicoNoms)-1)) * hF if len(self.simulation.dicoNoms) != 1 else (self.yMin+(self.yMax-self.yMin)/2)*hF        
        self.positionTexte = ((0.5*wF-self.texte.get_width())/2, self.yMilieuTexte-self.texte.get_height()/2)
        self.image = creer_image(texte=str(self.placeActu), rayon=self.rayon, couleurFond=self.couleur)
        










class Simulation(object):
    def __init__(self):
        self.quitterSimulation = False
        self.depart = False

        self.lFichiersResultats = ["S_Cadets.xls", "S_Cadettes.xls", "S_Juniors.xls", "S_Juniores.xls"]
        self.lNomsCourses = ["Cadets Hommes (S)", "Cadettes Filles (S)", "Juniors Hommes (S)", "Juniores Filles (S)"]
        self.iCourse = 3
        self.lDicoNoms = [{"ROCHETTE TOM":1, "PERRIN MAXENCE":2, "CROIZIER MARCEAU":2, "CARRIER GASPARD":2, "ROCHET TOM":1, "GARIVIER RAPHAËL":0},
                         {},
                         {"BERTEAU MAEL":0},
                         {"JAQUEROD LILOU":1, "MUGNIER DIANE":1, "CRON—BELGRAND ZOE":0, "HALAJDA JULIETTE":1, "LIATARD ELEA":1}]
        self.dicoNoms = self.lDicoNoms[self.iCourse]
        self.dicoRayons = {0:20, 1:16, 2:13, 3:5}

        self.fpsMin, self.fpsMax, self.fps = 1, 200, 30

        self.xFondParcours, self.yFondParcours = 0.025*wF, 0.275*hF
        self.wParcours, self.hParcours = 0.95*wF, 0.7*hF
        self.fondParcours = pygame.Surface((self.wParcours, self.hParcours), pygame.SRCALPHA)

        self.fondEcran0 = pygame.image.load("carte_2.png")
        self.wFE0, self.hFE0 = self.fondEcran0.get_size()
        self.xFE, self.yFE, self.echelleFE = 0, 0, 1
        self.changer_fond_ecran()

        self.charger_gpx()
        self.charger_resultats()

        self.titre = creer_texte(nom=f"Animation Sélectif Triathlon Condrieu 2026 : {self.lNomsCourses[self.iCourse]}", taille=30, gras=True, italique=False, couleur=(0,0,150))
        self.positionTitre = ((wF-self.titre.get_width())/2, 0.01*hF)
        self.changer_texte_fps()

        self.creer_athletes()

    def charger_gpx(self):
        with open("triathlon_S_3.gpx", "r", encoding="utf-8") as fichier:
            triathlon = gpxpy.parse(fichier)

        self.lParcours, self.listeLPoints, self.lDist = [], [], []
        longMin, longMax, latMin, latMax = float("inf"), -float("inf"), float('inf'), -float("inf")
        for parcours in triathlon.tracks:
            self.lParcours.append(parcours.name)
            lPoints = []
            dist = 0 # en m
            pointAvant = None
            for segment in parcours.segments:
                for point in segment.points:
                    lPoints.append((point.longitude, point.latitude))
                    if pointAvant is not None:
                        dist += point.distance_2d(pointAvant)
                    pointAvant = point
            self.lDist.append(dist)
            lPoints = np.array(lPoints, dtype=np.float64)
            self.listeLPoints.append(lPoints)
            longMin = min(longMin, np.min(lPoints[:, 0]))
            longMax = max(longMax, np.max(lPoints[:, 0]))
            latMin = min(latMin, np.min(lPoints[:, 1]))
            latMax = max(latMax, np.max(lPoints[:, 1]))

        echelle = min(self.wParcours/(longMax-longMin), self.hParcours/(latMax-latMin))
        x0, y0 = (self.wParcours - echelle*(longMax-longMin))/2, (self.hParcours - echelle*(latMax-latMin))/2
        for lPoints in self.listeLPoints:
            lPoints[:, 0] = x0 + (lPoints[:, 0] - longMin) * echelle
            lPoints[:, 1] = self.hParcours - (y0 + (lPoints[:, 1] - latMin) * echelle)
            dist = sum(distance(lPoints[i], lPoints[i-1]) for i in range(1, len(lPoints)))

        self.lCouleursParcours = []
        for i, parcours in enumerate(self.lParcours):
            c = i/len(self.lParcours)
            self.lCouleursParcours.append((255*(1-c), 255*c, (255*2*c)%255, 80))

    def charger_resultats(self):
        fichier = pandas.read_html(self.lFichiersResultats[self.iCourse])
        tableau = fichier[0]
        #columns : ['Pl.', 'Dos', 'Unnamed: 2', 'Nom', 'Club', 'Sx', 'Cat', 'Par cat.', 'NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2', 'CAP', 'Temps', 'Ecart', 'Moy']
        tableau["Nom"] = tableau["Nom"].str.replace('\xa0', ' ')
        for colonne in ['NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2', 'CAP', 'Temps', 'Ecart']:
            tableau[colonne] = tableau[colonne].apply(temps_en_secondes)

        lColonnesTemps = ['NATATION','T1','VELO','T2','CAP TOUR 1', 'CAP TOUR 2']
        masque = ~tableau[lColonnesTemps].eq(-1).any(axis=1)
        tableau = tableau.loc[masque].reset_index(drop=True)
        self.listeLTemps = tableau[lColonnesTemps].to_numpy(dtype=float)
        self.listeLVitesses = [self.lDist/lTemps for lTemps in self.listeLTemps]
        self.lNoms = tableau["Nom"].to_numpy()
        self.lPlaces = tableau["Pl."].to_numpy(dtype=np.int16)
        c = 1 - (self.lPlaces - self.lPlaces.min()) / (self.lPlaces.max() - self.lPlaces.min())
        self.lCouleurs = [(int(255*(1-ci)), int(255*ci), int((255*2*ci) % 255)) for ci in c]
        self.lRayons = [self.dicoRayons[self.dicoNoms[nom]] if nom in self.dicoNoms else self.dicoRayons[3] for nom in self.lNoms]

    def creer_athletes(self):
        athleteOuvreur = Athlete(lVitesses=[5]*len(self.lParcours), listeLPoints=self.listeLPoints, rayon=10, couleur=(255,255,255), nom="Ouvreur", place=0, simulation=self)
        self.listeLPointsParcours = [[(athleteOuvreur.x, athleteOuvreur.y)]]
        while athleteOuvreur.actif :
            if athleteOuvreur.bouger() and athleteOuvreur.actif:
                self.listeLPointsParcours.append([])
            self.listeLPointsParcours[-1].append((athleteOuvreur.x, athleteOuvreur.y))
        self.lAthletes = [Athlete(lVitesses=lVitesses, listeLPoints=self.listeLPoints, rayon=rayon, couleur=couleur, nom=nom, place=place, simulation=self) for lVitesses,nom,place,couleur,rayon in zip(self.listeLVitesses, self.lNoms, self.lPlaces, self.lCouleurs, self.lRayons)]
        self.lAthletesNoms = [athlete for athlete in self.lAthletes if athlete.nom in self.dicoNoms]
        for athlete in self.lAthletes:
            athlete.reset(reel=True)

    def changer_classement(self):
        if not all(self.lAthletes[i-1].dist >= self.lAthletes[i].dist for i in range(1, len(self.lAthletes))) or not hasattr(self, "lAthletesNoms"):
            self.lAthletes.sort(key = lambda athlete : athlete.dist, reverse=True)
            self.lAthletesNoms = [athlete for athlete in self.lAthletes if athlete.nom in self.dicoNoms]
            for athlete in self.lAthletesNoms:
                if athlete.actif:
                    athlete.changer_texte()

    def tester_clavier(self):
        lTouches = pygame.key.get_pressed()

        if lTouches[pygame.K_LSHIFT]:
            changement_texte_fps = False
            if lTouches[pygame.K_UP]:
                self.fps = min(self.fps+1, self.fpsMax)
                changement_texte_fps = True
            elif lTouches[pygame.K_DOWN] :
                self.fps = max(self.fps-1, self.fpsMin)
                changement_texte_fps = True
            if changement_texte_fps:
                self.changer_texte_fps()

        if lTouches[pygame.K_RIGHT]:
            self.xFE -= 1
        if lTouches[pygame.K_LEFT]:
            self.xFE += 1
        if lTouches[pygame.K_LCTRL]:
            if lTouches[pygame.K_UP]:
                self.echelleFE += 0.01
            if lTouches[pygame.K_DOWN]:
                self.echelleFE -= 0.01
        else :
            if lTouches[pygame.K_UP]:
                self.yFE += 1
            if lTouches[pygame.K_DOWN]:
                self.yFE -= 1

    def bouger(self):
        if self.depart:
            for athlete in self.lAthletes:
                athlete.bouger()
            self.changer_classement()

    def afficher(self):
        fenetre.fill((0,0,0))
        
        #self.changer_fond_ecran()
        #fenetre.blit(self.fondEcran, (self.xFE, self.yFE))
        fenetre.blit(self.titre, self.positionTitre)
        fenetre.blit(self.texteFPS, self.positionTexteFPS)

        self.fondParcours.fill((255,255,255,0))
        for couleur, lPoints in zip(self.lCouleursParcours, self.listeLPointsParcours):
            for x,y in lPoints:
                pygame.draw.circle(surface=self.fondParcours, color=couleur, center=(x,y), radius=2)
        for athlete in self.lAthletes:
            athlete.afficher()
        fenetre.blit(self.fondParcours, (self.xFondParcours, self.yFondParcours))

        pygame.display.flip()

    def changer_fond_ecran(self):
        self.fondEcran = pygame.transform.scale(surface=self.fondEcran0, size=(self.echelleFE*self.wFE0, self.echelleFE*self.hFE0))

    def changer_texte_fps(self):
        self.texteFPS = creer_texte(nom=f"FPS : {self.fps}", taille=20, gras=True, italique=False, couleur=(150,0,0))
        self.positionTexteFPS = ((1.5*wF-self.texteFPS.get_width())/2, (0.4*hF-self.texteFPS.get_height())/2)

    def run(self):
        self.depart = False
        while not self.quitterSimulation:
            horloge.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitterSimulation = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.depart = not self.depart
                        for athlete in self.lAthletes:
                            athlete.reset()
            self.tester_clavier()

            self.bouger()
            
            self.afficher()


pygame.init()
wF, hF = 800, 600
fenetre = pygame.display.set_mode((wF, hF))
pygame.display.set_caption("Animation Sélectif S 2026 Cadets Condrieur")
horloge = pygame.time.Clock()

simulation = Simulation()
simulation.run()

pygame.quit()