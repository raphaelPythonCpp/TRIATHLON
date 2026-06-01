import gpxpy
import pandas
import pygame
import numpy as np

pygame.init()
wF, hF = 800, 600
fenetre = pygame.display.set_mode((wF, hF))
pygame.display.set_caption("Animation Sélectif S 2026 Cadets Condrieur")
horloge = pygame.time.Clock()








def distance(point1, point2):
    return ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**0.5

with open("triathlon_S_3.gpx", "r", encoding="utf-8") as fichier:
    triathlon = gpxpy.parse(fichier)

lParcours, listeLPoints, lDist = [], [], []
longMin, longMax, latMin, latMax = float("inf"), -float("inf"), float('inf'), -float("inf")
for parcours in triathlon.tracks:
    lParcours.append(parcours.name)
    lPoints = []
    dist = 0 # en m
    pointAvant = None
    for segment in parcours.segments:
        for point in segment.points:
            lPoints.append((point.longitude, point.latitude))
            if pointAvant is not None:
                dist += point.distance_2d(pointAvant)
            pointAvant = point
        lDist.append(dist)
    lPoints = np.array(lPoints, dtype=np.float64)
    listeLPoints.append(lPoints)
    longMin = min(longMin, np.min(lPoints[:, 0]))
    longMax = max(longMax, np.max(lPoints[:, 0]))
    latMin = min(latMin, np.min(lPoints[:, 1]))
    latMax = max(latMax, np.max(lPoints[:, 1]))

xFondParcours, yFondParcours, wParcours, hParcours = 0.025*wF, 0.275*hF, 0.95*wF, 0.7*hF
fondParcours = pygame.Surface((wParcours, hParcours), pygame.SRCALPHA)
echelle = min(wParcours/(longMax-longMin), hParcours/(latMax-latMin))
x0, y0 = (wParcours - echelle*(longMax-longMin))/2, (hParcours - echelle*(latMax-latMin))/2
for lPoints in listeLPoints:
    lPoints[:, 0] = x0 + (lPoints[:, 0] - longMin) * echelle
    lPoints[:, 1] = hParcours - (y0 + (lPoints[:, 1] - latMin) * echelle)
    dist = sum(distance(lPoints[i], lPoints[i-1]) for i in range(1, len(lPoints)))

lCouleursParcours = []
for i, parcours in enumerate(lParcours):
    c = i/len(lParcours)
    lCouleursParcours.append((255*(1-c), 255*c, (255*2*c)%255, 80))





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

lFichiersResultats = ["S_Cadets.xls", "S_Cadettes.xls", "S_Juniors.xls", "S_Juniores.xls"]
lNomsCourses = ["Cadets Hommes (S)", "Cadettes Filles (S)", "Juniors Hommes (S)", "Juniores Filles (S)"]
iCourse = 3
fichier = pandas.read_html(lFichiersResultats[iCourse])
tableau = fichier[0]
#columns : ['Pl.', 'Dos', 'Unnamed: 2', 'Nom', 'Club', 'Sx', 'Cat', 'Par cat.', 'NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2', 'CAP', 'Temps', 'Ecart', 'Moy']
tableau["Nom"] = tableau["Nom"].str.replace('\xa0', ' ')
for colonne in ['NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2', 'CAP', 'Temps', 'Ecart']:
    tableau[colonne] = tableau[colonne].apply(temps_en_secondes)

lColonnesTemps = ['NATATION','T1','VELO','T2','CAP TOUR 1', 'CAP TOUR 2']
masque = ~tableau[lColonnesTemps].eq(-1).any(axis=1)
tableau = tableau.loc[masque].reset_index(drop=True)
listeLTemps = tableau[lColonnesTemps].to_numpy(dtype=float)
listeLVitesses = [lDist/lTemps for lTemps in listeLTemps]
lNoms = tableau["Nom"].to_numpy()
lPlaces = tableau["Pl."].to_numpy(dtype=np.int16)
c = 1 - (lPlaces - lPlaces.min()) / (lPlaces.max() - lPlaces.min())
lCouleurs = [(int(255*(1-ci)), int(255*ci), int((255*2*ci) % 255)) for ci in c]
lDicoNoms = [{"ROCHETTE TOM":1, "PERRIN MAXENCE":2, "CROIZIER MARCEAU":2, "CARRIER GASPARD":2, "ROCHET TOM":1, "GARIVIER RAPHAËL":0},
             {},
             {"BERTEAU MAEL":0},
             {"JAQUEROD LILOU":1, "MUGNIER DIANE":1, "CRON—BELGRAND ZOE":0, "HALAJDA JULIETTE":1, "LIATARD ELEA":1}]
dicoNoms = lDicoNoms[iCourse]
dicoRayons = {0:20, 1:16, 2:13, 3:5}
lRayons = [dicoRayons[dicoNoms[nom]] if nom in dicoNoms else dicoRayons[3] for nom in lNoms]






def avancer_n_metres(athlete, deltaDist):
    changementParcours = False
    while athlete.actif and distance((athlete.x, athlete.y), athlete.listeLPoints[athlete.iParcours][athlete.iProchainPoint]) <= deltaDist:
        deltaDist -= distance((athlete.x, athlete.y), athlete.listeLPoints[athlete.iParcours][athlete.iProchainPoint])
        athlete.x, athlete.y = athlete.listeLPoints[athlete.iParcours][athlete.iProchainPoint]
        athlete.iProchainPoint += 1
        if athlete.iProchainPoint >= len(athlete.listeLPoints[athlete.iParcours]):
            changementParcours = True
            athlete.iParcours += 1
            athlete.iProchainPoint = 1
            if athlete.iParcours >= len(athlete.listeLPoints):
                athlete.actif = False
            athlete.changer_texte()
    return changementParcours

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
    def __init__(self, lVitesses, listeLPoints, rayon, couleur, nom, place):
        self.actif = True

        self.lVitesses = lVitesses
        self.listeLPoints = listeLPoints
        self.rayon = rayon
        self.couleur = couleur
        self.nom = nom
        self.place = place
        self.image = creer_image(texte=str(self.place), rayon=self.rayon, couleurFond=self.couleur)
        self.wI, self.hI = self.image.get_size()

        yMin, yMax = 0.10, 0.50
        if self.nom in dicoNoms:
            self.yMilieuTexte = (yMin + (list(dicoNoms.keys()).index(self.nom)+0.5)*(yMax-yMin) / (len(dicoNoms)-1)) * hF if len(dicoNoms) != 1 else (yMin+(yMax-yMin)/2)*hF
        
        self.reset()

    def reset(self):
        self.actif = True

        self.iParcours = 0
        self.iProchainPoint = 1
        self.x, self.y = self.listeLPoints[self.iParcours][0]

        self.changer_texte()

    def bouger(self):
        if not self.actif :
            return
        deltaDist = self.lVitesses[self.iParcours]
        changementParcours = avancer_n_metres(athlete=self, deltaDist=deltaDist)
        
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
            fondParcours.blit(self.image, (self.x-self.wI/2, self.y-self.hI/2))
        #pygame.draw.circle(surface=fenetre, color=self.couleur, center=(self.x, self.y), radius=self.rayon)

    def changer_texte(self):
        if self.nom not in dicoNoms:
            self.texte = None
            return
        self.texte = creer_texte(nom=f"{self.nom} : {self.place} ({dicoNoms[self.nom]}) => {"Départ" if not depart else "Arrivée" if not self.actif else lParcours[self.iParcours]}", taille=20, gras=True, italique=False, couleur=self.couleur)
        self.positionTexte = ((0.5*wF-self.texte.get_width())/2, self.yMilieuTexte-self.texte.get_height()/2)






def tester_clavier():
    global fps, xFE, yFE, echelleFE
    lTouches = pygame.key.get_pressed()

    if lTouches[pygame.K_LSHIFT]:
        changement_texte_fps = False
        if lTouches[pygame.K_UP]:
            fps = min(fps+1, fpsMax)
            changement_texte_fps = True
        elif lTouches[pygame.K_DOWN] :
            fps = max(fps-1, fpsMin)
            changement_texte_fps = True
        if changement_texte_fps:
            changer_texte_fps()

    if lTouches[pygame.K_RIGHT]:
        xFE -= 1
    if lTouches[pygame.K_LEFT]:
        xFE += 1
    if lTouches[pygame.K_LCTRL]:
        if lTouches[pygame.K_UP]:
            echelleFE += 0.01
        if lTouches[pygame.K_DOWN]:
            echelleFE -= 0.01
    else :
        if lTouches[pygame.K_UP]:
            yFE += 1
        if lTouches[pygame.K_DOWN]:
            yFE -= 1

def bouger():
    if depart:
        for athlete in lAthletes:
            athlete.bouger()

def afficher():
    fenetre.fill((0,0,0))
    
    #changer_fond_ecran()
    #fenetre.blit(fondEcran, (xFE, yFE))
    fenetre.blit(titre, positionTitre)
    fenetre.blit(texteFPS, positionTexteFPS)

    fondParcours.fill((255,255,255,0))
    for couleur, lPoints in zip(lCouleursParcours, listeLPointsParcours):
        for x,y in lPoints:
            pygame.draw.circle(surface=fondParcours, color=couleur, center=(x,y), radius=2)
    for athlete in lAthletes:
        athlete.afficher()
    fenetre.blit(fondParcours, (xFondParcours, yFondParcours))

    pygame.display.flip()

def changer_fond_ecran():
    global fondEcran
    fondEcran = pygame.transform.scale(surface=fondEcran0, size=(echelleFE*wFE0, echelleFE*hFE0))

def changer_texte_fps():
    global texteFPS, positionTexteFPS
    texteFPS = creer_texte(nom=f"FPS : {fps}", taille=20, gras=True, italique=False, couleur=(150,0,0))
    positionTexteFPS = ((1.5*wF-texteFPS.get_width())/2, (0.4*hF-texteFPS.get_height())/2)
    








fondEcran0 = pygame.image.load("carte_2.png")
wFE0, hFE0 = fondEcran0.get_size()
xFE, yFE, echelleFE = 0, 0, 1
changer_fond_ecran()

titre = creer_texte(nom=f"Animation Sélectif Triathlon Condrieu 2026 : {lNomsCourses[iCourse]}", taille=30, gras=True, italique=False, couleur=(0,0,150))
positionTitre = ((wF-titre.get_width())/2, 0.01*hF)

fpsMin, fpsMax, fps = 1, 200, 30
changer_texte_fps()

depart = False
athleteOuvreur = Athlete(lVitesses=[5]*len(lParcours), listeLPoints=listeLPoints, rayon=10, couleur=(255,255,255), nom="Ouvreur", place=0)
listeLPointsParcours = [[(athleteOuvreur.x, athleteOuvreur.y)]]
while athleteOuvreur.actif :
    if athleteOuvreur.bouger() and athleteOuvreur.actif:
        listeLPointsParcours.append([])
    listeLPointsParcours[-1].append((athleteOuvreur.x, athleteOuvreur.y))
lAthletes = [Athlete(lVitesses=lVitesses, listeLPoints=listeLPoints, rayon=rayon, couleur=couleur, nom=nom, place=place) for lVitesses,nom,place,couleur,rayon in zip(listeLVitesses, lNoms, lPlaces, lCouleurs, lRayons)]

quitterSimulation = False
while not quitterSimulation:
    horloge.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitterSimulation = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                depart = not depart
                for athlete in lAthletes:
                    athlete.reset()
    tester_clavier()

    bouger()
    
    afficher()

pygame.quit()