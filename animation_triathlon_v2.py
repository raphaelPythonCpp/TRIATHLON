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

def recuperer_texte(nom, taille, gras, italique, souligne, couleur, reel):
    global dicoPolices
    cle = (taille, gras, italique)
    if cle not in dicoPolices:
        dicoPolices[cle] = pygame.font.SysFont("Segoe UI Symbol", taille, bold=gras, italic=italique)
    dicoPolices[cle].set_underline(souligne)
    if reel:
        return dicoPolices[cle].render(nom, True, couleur)
    else:
        return dicoPolices[cle]

def creer_texte(nom, w, h, gras, italique, souligne, couleur, c=None):
    if couleur is None:
        couleur = donner_couleur(c)
    
    #1ere dichotomie sur w
    wMin, wMax = 0, w
    while wMin+1 < wMax:
        wMilieu = int((wMin+wMax)/2)
        if recuperer_texte(nom=nom, taille=wMilieu, gras=gras, italique=italique, souligne=souligne, couleur=couleur, reel=False).size(nom)[0] <= w:
            wMin = wMilieu
        else :
            wMax = wMilieu-1
    
    #2eme dichotomie sur h
    hMin, hMax = 0, h
    while hMin+1 < hMax:
        hMilieu = int((hMin+hMax)/2)
        if recuperer_texte(nom=nom, taille=hMilieu, gras=gras, italique=italique, souligne=souligne, couleur=couleur, reel=False).size(nom)[1] <= h:
            hMin = hMilieu
        else :
            hMax = hMilieu-1

    taille = min(wMin, hMin)
    if True:
        return recuperer_texte(nom=nom, taille=taille, gras=gras, italique=italique, souligne=souligne, couleur=couleur, reel=True)
    else :
        surface = pygame.Surface((w,h))
        surface.fill(color=couleur)
        return surface

dicoPolices = {}

def creer_image(texte, rayon, couleurFond, c=None):
    fond = pygame.Surface((2*rayon, 2*rayon), pygame.SRCALPHA)
    if couleurFond is None:
        couleurFond = donner_couleur(c)
    pygame.draw.circle(surface=fond, color=couleurFond, center=(rayon, rayon), radius=rayon)
    surfaceTexte = creer_texte(nom=texte, w=round(1.5*rayon), h=round(1.5*rayon), gras=False, italique=False, souligne=False, couleur=(255,255,255))
    fond.blit(surfaceTexte, ((2*rayon-surfaceTexte.get_width())/2, (2*rayon-surfaceTexte.get_height())/2))
    return fond

def donner_couleur(c): # c entre [0, 1]
    r = max(0, 255*(2*c-1))
    g = max(0, 255*(1-1.5*c))
    b = 255* (1 - 2*abs(c-0.5))
    return (r,g,b)









class Athlete(object):
    def __init__(self, simulation, lVitesses, listeLPoints, rayon, nom, place, visuel):
        self.simulation = simulation
        self.visuel = visuel

        self.lVitesses = lVitesses
        self.listeLPoints = listeLPoints
        self.rayon = rayon
        self.nom = nom
        self.placeArrivee = place
        self.image = creer_image(texte=str(self.placeArrivee), rayon=self.rayon, couleurFond=(255,255,255))
        self.wI, self.hI = self.image.get_size()

        self.xMinTexte, self.xMaxTexte, self.yMinTexte, self.yMaxTexte = 0.025,0.5, 0.20, 0.5
        
        self.reset(reel=False)

    def reset(self, reel=True, enCourse=False):
        self.actif = True

        self.iParcours = 0
        self.iProchainPoint = 1
        self.interpolation = 0
        self.placeActu = None
        self.x, self.y, _ = self.listeLPoints[self.iParcours][0]
        self.x0, self.y0 = self.x, self.y
        self.dist, self.tempsArrivee = 0, None

        if reel and self.visuel:
            if enCourse:
                place, placeMax = None, None
            else :
                place, placeMax = self.placeArrivee, np.max(self.simulation.lPlaces)
            self.changer_texte(place=place, placeMax=placeMax)

    def avancer_n_metres(self, deltaDist):
        changementParcours = False
        while self.actif and (1-self.interpolation)*self.listeLPoints[self.iParcours][self.iProchainPoint][2] <= deltaDist:
            deltaDist -= (1-self.interpolation)*self.listeLPoints[self.iParcours][self.iProchainPoint][2]
            self.x, self.y, _ = self.listeLPoints[self.iParcours][self.iProchainPoint]
            self.x0, self.y0 = self.x, self.y
            self.iProchainPoint += 1
            self.interpolation = 0
            if self.iProchainPoint >= len(self.listeLPoints[self.iParcours]):
                changementParcours = True
                self.iParcours += 1
                self.iProchainPoint = 1
                if self.iParcours >= len(self.listeLPoints):
                    self.actif = False
                    self.tempsArrivee = self.simulation.temps
                    self.placeActu = self.placeArrivee
                self.changer_texte(garder_place=True)
        return changementParcours, deltaDist

    def bouger(self):
        if not self.actif:
            return
        deltaDist = self.lVitesses[self.iParcours] * self.simulation.dt
        changementParcours, deltaDistResidu = self.avancer_n_metres(deltaDist=deltaDist)

        if self.actif:
            x2, y2, dist = self.listeLPoints[self.iParcours][self.iProchainPoint]
            if dist != 0:
                self.interpolation += deltaDistResidu / dist
                self.x = self.x0 + (x2 - self.x0) * self.interpolation
                self.y = self.y0 + (y2 - self.y0) * self.interpolation
            self.dist += deltaDist  # en course : tout est parcouru
        else:
            self.dist += deltaDist - deltaDistResidu  # arrivée : seulement le résidu consommé

        return changementParcours

    def afficher(self):
        if not self.visuel:
            return
        if self.texte is not None:
            fenetre.blit(self.texte, self.positionTexte)
        if self.actif :
            self.simulation.surfaceParcours.blit(self.image, (self.x-self.wI/2, self.y-self.hI/2))

    def changer_texte(self, place=None, placeMax=None, garder_place=False):
        if not self.visuel: 
            return
        placeAvant = self.placeActu
        if not garder_place:
            self.placeActu = 1+self.simulation.lAthletes.index(self) if place is None else place
        if placeAvant == self.placeActu:
            pass#return
        c = min(1, max(0, self.placeActu/ (len(self.simulation.lAthletes) if placeMax is None else placeMax)))
        self.image = creer_image(texte=str(self.placeActu), rayon=self.rayon, couleurFond=None, c=c)
        if self.nom in self.simulation.dicoNoms:
            self.xMilieuTexte = (self.xMinTexte + (self.xMaxTexte-self.xMinTexte)/2) * wF
            self.yMilieuTexte = (self.yMinTexte + (self.simulation.lAthletesNoms.index(self) + 0.5) * (self.yMaxTexte - self.yMinTexte) / len(self.simulation.lAthletesNoms)) * hF
            if self.simulation.enCourse:
                if self.actif:
                    parcours = self.simulation.lParcours[self.iParcours]
                    vitesse = 3.6*self.lVitesses[self.iParcours]
                    dist = self.dist
                else :
                    parcours = "Arrivée"
                    vitesse = 3.6*sum(self.lVitesses)/len(self.lVitesses)
                    dist = self.dist
            else :
                parcours = "Départ"
                vitesse = 0
                dist = 0
            self.texte = creer_texte(nom=f"{self.nom} : {self.placeActu}e => {parcours} : {vitesse:.2f} km/h || {dist/1000:.3f} km", w=wF*(self.xMaxTexte-self.xMinTexte), h=hF*(self.yMaxTexte-self.yMinTexte)/len(self.simulation.lAthletesNoms), gras=False, italique=False, souligne=False, couleur=None, c=c)
            self.positionTexte = (self.xMilieuTexte-(self.texte.get_width())/2, self.yMilieuTexte-self.texte.get_height()/2)
        else :
            self.texte = None
        










class Simulation(object):
    def __init__(self):
        self.quitterSimulation = False
        self.enCourse = False

        self.lFichiersResultats = ["XS_Benjamin(e)s.xls", "XS_Minimes_H.xls", "XS_Minimes_F.xls", "S_Cadets.xls", "S_Cadettes.xls", "S_Juniors.xls", "S_Juniores.xls"]
        self.lNomsCourses = ["Benjamin(e)s (XS)", "Minimes Hommes (XS)", "Minimes Femmes (XS)", "Cadets Hommes (S)", "Cadettes Filles (S)", "Juniors Hommes (S)", "Juniores Filles (S)"]
        self.iCourse = 1
        self.typeCourse = "XS" if self.iCourse <= 2 else "S"
        self.lDicoNoms = [{"JOUFFRET JULES":2, "BILLON NALIA":1, "MARTIN AMBRE":1}, 
                          {"BIEBER MANOE":2, "CAUDAL ADRIEN":0, "BILLY HUGO":0, "RIVOIRE PIEGAY HECTOR":1, },
                          {"MARTIN LUCILE":1, "GARIVIER ALICE":0}, 
                          {"ROCHETTE TOM":1, "PERRIN MAXENCE":2, "CROIZIER MARCEAU":2, "CARRIER GASPARD":2, "ROCHET TOM":1, "GARIVIER RAPHAËL":0},
                          {},
                          {"BERTEAU MAEL":0},
                          {"JAQUEROD LILOU":1, "MUGNIER DIANE":1, "CRON—BELGRAND ZOE":0, "HALAJDA JULIETTE":1, "LIATARD ELEA":1}]
        self.dicoNoms = self.lDicoNoms[self.iCourse]
        self.dicoRayons = {0:15, 1:15, 2:15, 3:15}
        self.dicoRayons = {0:20, 1:16, 2:13, 3:8} #A MODIFIER

        self.fps = 30
        self.dtMin, self.dtMax, self.dt, self.deltaDt = 0/self.fps, 1000/self.fps, 30/self.fps, 1.05

        self.xMinSurfaceParcours, self.xMaxSurfaceParcours, self.yMinSurfaceParcours, self.yMaxSurfaceParcours = 0.025, 0.975, 0.35, 0.975
        self.wParcours, self.hParcours = (self.xMaxSurfaceParcours-self.xMinSurfaceParcours)*wF, (self.yMaxSurfaceParcours-self.yMinSurfaceParcours)*hF
        self.xSurfaceParcours, self.ySurfaceParcours = self.xMinSurfaceParcours*wF, self.yMinSurfaceParcours*hF
        #self.xMilieuSurfaceParcours, self.yMilieuSurfaceParcours = self.xMinSurfaceParcours*wF + self.wParcours/2, self.yMinSurfaceParcours*hF + self.hParcours/2
        self.surfaceParcours = pygame.Surface((self.wParcours, self.hParcours), pygame.SRCALPHA)
        #self.xSurfaceParcours, self.ySurfaceParcours = self.xMilieuSurfaceParcours-self.surfaceParcours.get_width()/2, self.yMilieuSurfaceParcours-self.surfaceParcours.get_height()/2
        

        self.fondEcran0 = pygame.image.load("carte_2.png")
        self.wFE0, self.hFE0 = self.fondEcran0.get_size()
        self.xFE, self.yFE, self.echelleFE = 0, 0, 1
        self.changer_fond_ecran()

        self.charger_gpx()
        self.charger_resultats()

        self.xMinTexteTitre, self.xMaxTexteTitre, self.yMinTexteTitre, self.yMaxTexteTitre = 0.1, 0.9, 0.01, 0.1
        self.xMilieuTexteTitre = (self.xMinTexteTitre + (self.xMaxTexteTitre-self.xMinTexteTitre)/2)*wF
        self.yMilieuTexteTitre = (self.yMinTexteTitre + (self.yMaxTexteTitre-self.yMinTexteTitre)/2)*hF
        self.changer_texte_titre()
                
        self.xMinTexteDt, self.xMaxTexteDt, self.yMinTexteDt, self.yMaxTexteDt = 0.6, 0.9, 0.2, 0.25
        self.xMilieuTexteDt = (self.xMinTexteDt + (self.xMaxTexteDt-self.xMinTexteDt)/2)*wF
        self.yMilieuTexteDt = (self.yMinTexteDt + (self.yMaxTexteDt-self.yMinTexteDt)/2)*hF
        self.changer_texte_dt()
        
        self.xMinTexteTemps, self.xMaxTexteTemps, self.yMinTexteTemps, self.yMaxTexteTemps = 0.6, 0.9, 0.25, 0.30
        self.xMilieuTexteTemps = (self.xMinTexteTemps + (self.xMaxTexteTemps-self.xMinTexteTemps)/2)*wF
        self.yMilieuTexteTemps = (self.yMinTexteTemps + (self.yMaxTexteTemps-self.yMinTexteTemps)/2)*hF
        
        self.xMinTexteClassementVirtuel, self.xMaxTexteClassementVirtuel, self.yMinTexteClassementVirtuel, self.yMaxTexteClassementVirtuel = 0.025, 0.5, 0.125, 0.2
        self.xMilieuTexteClassementVirtuel = (self.xMinTexteClassementVirtuel + (self.xMaxTexteClassementVirtuel-self.xMinTexteClassementVirtuel)/2)*wF
        self.yMilieuTexteClassementVirtuel = (self.yMinTexteClassementVirtuel + (self.yMaxTexteClassementVirtuel-self.yMinTexteClassementVirtuel)/2)*hF
        self.changer_texte_classement_virtuel()

        self.xMinTexteDonnees, self.xMaxTexteDonnees, self.yMinTexteDonnees, self.yMaxTexteDonnees = 0.6, 0.9, 0.125, 0.2
        self.xMilieuTexteDonnees = (self.xMinTexteDonnees + (self.xMaxTexteDonnees-self.xMinTexteDonnees)/2)*wF
        self.yMilieuTexteDonnees = (self.yMinTexteDonnees + (self.yMaxTexteDonnees-self.yMinTexteDonnees)/2)*hF
        self.changer_texte_donnees()

        self.creer_athletes()

    def charger_gpx(self):
        dicoFichierGPX = {"XS" : "triathlon_XS.gpx", "S" : "triathlon_S_4.gpx"}
        fichierGPX = dicoFichierGPX[self.typeCourse]
        with open(fichierGPX, "r", encoding="utf-8") as fichier:
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
                    deltaDist = 0 if pointAvant is None else point.distance_2d(pointAvant)
                    lPoints.append((point.longitude, point.latitude, deltaDist))
                    dist += deltaDist
                    pointAvant = point
            self.lDist.append(dist)
            lPoints = np.array(lPoints, dtype=np.float64)
            self.listeLPoints.append(lPoints)
            longMin = min(longMin, np.min(lPoints[:, 0]))
            longMax = max(longMax, np.max(lPoints[:, 0]))
            latMin = min(latMin, np.min(lPoints[:, 1]))
            latMax = max(latMax, np.max(lPoints[:, 1]))

        self.propXParcours, self.propYParcours = 0.9, 0.9
        echelle = min(self.propXParcours*self.wParcours/(longMax-longMin), self.propYParcours*self.hParcours/(latMax-latMin))
        x0, y0 = (self.wParcours - echelle*(longMax-longMin))/2, (self.hParcours - echelle*(latMax-latMin))/2
        for lPoints in self.listeLPoints:
            lPoints[:, 0] = x0 + (lPoints[:, 0] - longMin) * echelle
            lPoints[:, 1] = self.hParcours - (y0 + (lPoints[:, 1] - latMin) * echelle)

        self.lCouleursParcours = []
        for i, parcours in enumerate(self.lParcours):
            c = i/len(self.lParcours)
            self.lCouleursParcours.append(donner_couleur(c)+(100,))

    def charger_resultats(self):
        fichier = pandas.read_html(self.lFichiersResultats[self.iCourse])
        tableau = fichier[0]
        #columns : ['Pl.', 'Dos', 'Unnamed: 2', 'Nom', 'Club', 'Sx', 'Cat', 'Par cat.', 'NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2', 'CAP', 'Temps', 'Ecart', 'Moy']
        dicoLColonnesTemps = {"XS" : ['NATATION', 'T1', 'VELO', 'T2', 'CAP'],
                              "S" : ['NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2']}
        lColonnesTemps = dicoLColonnesTemps[self.typeCourse]
        tableau["Nom"] = tableau["Nom"].str.replace('\xa0', ' ')
        for colonne in lColonnesTemps:
            tableau[colonne] = tableau[colonne].apply(temps_en_secondes)

        masque = ~tableau[lColonnesTemps].eq(-1).any(axis=1)

        tableauExclu = tableau[~masque]
        if len(tableauExclu) > 0:
            print(f"\n{len(tableauExclu)} athlètes non comptabilisé (bug valeurs temps):")
            for _, ligne in tableauExclu.iterrows():
                lColonnesMauvaises = [colonne for colonne in lColonnesTemps if ligne[colonne] == -1]
                print(f" - {ligne['Nom']} ({ligne['Pl.']}e) : bug sur [{" + ".join(lColonnesMauvaises)}]")
            print()

        tableau = tableau.loc[masque].reset_index(drop=True)
        self.listeLTemps = tableau[lColonnesTemps].to_numpy(dtype=float)
        self.listeLVitesses = [self.lDist/lTemps for lTemps in self.listeLTemps]
        self.lNoms = tableau["Nom"].to_numpy()
        self.lPlaces = tableau["Pl."].to_numpy(dtype=np.int16)
        self.lRayons = [self.dicoRayons[self.dicoNoms[nom]] if nom in self.dicoNoms else self.dicoRayons[3] for nom in self.lNoms]

    def creer_athletes(self):
        self.lAthletes = [Athlete(lVitesses=lVitesses, listeLPoints=self.listeLPoints, rayon=rayon, nom=nom, place=place, simulation=self, visuel=True) for lVitesses,nom,place,rayon in zip(self.listeLVitesses, self.lNoms, self.lPlaces, self.lRayons)]
        self.lAthletesNoms = [athlete for athlete in self.lAthletes if athlete.nom in self.dicoNoms]
        for athlete in self.lAthletes:
            athlete.reset(reel=True)
        
        athleteOuvreur = Athlete(lVitesses=[1]*len(self.lParcours), listeLPoints=self.listeLPoints, rayon=10, nom="Ouvreur", place=0, simulation=self, visuel=False)
        self.listeLPointsParcours = [[(athleteOuvreur.x, athleteOuvreur.y)]]
        self.temps = 0
        while athleteOuvreur.actif :
            if athleteOuvreur.bouger() and athleteOuvreur.actif:
                self.listeLPointsParcours.append([])
            self.listeLPointsParcours[-1].append((athleteOuvreur.x, athleteOuvreur.y))
        self.fondParcours = pygame.Surface((self.wParcours, self.hParcours), pygame.SRCALPHA)
        for couleur, lPoints in zip(self.lCouleursParcours, self.listeLPointsParcours):
            for x,y in lPoints:
                pygame.draw.circle(surface=self.fondParcours, color=couleur, center=(x,y), radius=2)
        

    def changer_classement(self):
        tri = False
        if self.enCourse:
            if True or not all(self.lAthletes[i-1].dist >= self.lAthletes[i].dist for i in range(1, len(self.lAthletes))):
                self.lAthletes.sort(key = lambda athlete : (athlete.tempsArrivee if athlete.tempsArrivee is not None else float("inf"), -athlete.dist))
                tri = True
        else:
            if not all(self.lAthletes[i-1].placeArrivee < self.lAthletes[i].placeArrivee for i in range(1, len(self.lAthletes))):
                self.lAthletes.sort(key = lambda athlete : (athlete.placeArrivee))
                tri = True
        if tri:
            self.lAthletesNoms = [athlete for athlete in self.lAthletes if athlete.nom in self.dicoNoms]
            for athlete in self.lAthletes:
                athlete.changer_texte()

    def tester_clavier(self):
        lTouches = pygame.key.get_pressed()

        if lTouches[pygame.K_LSHIFT]:
            #changement_texte_fps = False
            changement_texte_dt = False
            if lTouches[pygame.K_UP]:
                #self.fps = min(self.fps+5, self.fpsMax)
                #changement_texte_fps = True
                self.dt = min(self.dtMax, max(self.dt+0.01, self.dt*self.deltaDt))
                changement_texte_dt = True
            elif lTouches[pygame.K_DOWN] :
                #self.fps = max(self.fps-5, self.fpsMin)
                #changement_texte_fps = True
                self.dt = max(self.dtMin, min(self.dt-0.01, self.dt/self.deltaDt))
                changement_texte_dt = True
            #if changement_texte_fps:
                #self.changer_texte_fps()
            if changement_texte_dt:
                self.changer_texte_dt()

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
        if self.enCourse:
            for athlete in self.lAthletes:
                athlete.bouger()
            self.changer_classement()
            self.enCourse = any(athlete.actif for athlete in self.lAthletes)

    def afficher(self):
        fenetre.fill((0,0,0))
        
        #self.changer_fond_ecran()
        #fenetre.blit(self.fondEcran, (self.xFE, self.yFE))
        fenetre.blit(self.texteTitre, self.positionTitre)
        #fenetre.blit(self.texteFPS, self.positionTexteFPS)
        fenetre.blit(self.texteDt, self.positionTexteDt)
        fenetre.blit(self.texteTemps, self.positionTexteTemps)
        fenetre.blit(self.texteClassementVirtuel, self.positionTexteClassementVirtuel)
        fenetre.blit(self.texteDonnees, self.positionTexteDonnees)

        self.surfaceParcours.fill((255,255,255,0))
        self.surfaceParcours.blit(self.fondParcours, (0,0))
        for athlete in self.lAthletes[::-1]:
            if athlete not in self.lAthletesNoms:
                athlete.afficher()
        for athlete in self.lAthletesNoms[::-1]:
            athlete.afficher()
        fenetre.blit(self.surfaceParcours, (self.xSurfaceParcours, self.ySurfaceParcours))

        pygame.display.flip()

    def changer_fond_ecran(self):
        self.fondEcran = pygame.transform.scale(surface=self.fondEcran0, size=(self.echelleFE*self.wFE0, self.echelleFE*self.hFE0))

    def changer_texte_titre(self):
        self.texteTitre = creer_texte(nom=f"Animation Sélectif Triathlon Condrieu 2026 : {self.lNomsCourses[self.iCourse]}", w=wF*(self.xMaxTexteTitre-self.xMinTexteTitre), h=hF*(self.yMaxTexteTitre-self.yMinTexteTitre), gras=True, italique=False, souligne=True, couleur=(255,255,255))
        self.positionTitre = (self.xMilieuTexteTitre - self.texteTitre.get_width()/2, self.yMilieuTexteTitre - self.texteTitre.get_height()/2)

    def changer_texte_dt(self):
        #lCar pour double-flèche : ⇌ ⇼ ⟿ ➻ ➽ ➳ ➠ ➢ ↭
        self.texteDt = creer_texte(nom=f"1 sec Simulation ➽ {self.dt*self.fps:.2f} sec Course", w=wF*(self.xMaxTexteDt-self.xMinTexteDt), h=hF*(self.yMaxTexteDt-self.yMinTexteDt), gras=False, italique=False, souligne=False, couleur=(150,0,0))
        self.positionTexteDt = (self.xMilieuTexteDt - self.texteDt.get_width()/2, self.yMilieuTexteDt - self.texteDt.get_height()/2)

    def changer_texte_temps(self):
        self.texteTemps = creer_texte(nom=f"Temps Cummulé : {int(self.temps/3600)} h {int(self.temps%3600/60)} min {round(self.temps%60)} sec", w=wF*(self.xMaxTexteTemps-self.xMinTexteTemps), h=hF*(self.yMaxTexteTemps-self.yMinTexteTemps), gras=False, italique=False, souligne=False, couleur=(150,0,0))
        self.positionTexteTemps = (self.xMilieuTexteTemps - self.texteTemps.get_width()/2, self.yMilieuTexteTemps - self.texteTemps.get_height()/2)

    def changer_texte_classement_virtuel(self):
        self.texteClassementVirtuel = creer_texte(nom=f"Classement Virtuel :", w=wF*(self.xMaxTexteClassementVirtuel-self.xMinTexteClassementVirtuel), h=hF*(self.yMaxTexteClassementVirtuel-self.yMinTexteClassementVirtuel), gras=False, italique=False, souligne=True, couleur=(150,150,150))
        self.positionTexteClassementVirtuel = (self.xMilieuTexteClassementVirtuel - self.texteClassementVirtuel.get_width()/2, self.yMilieuTexteClassementVirtuel - self.texteClassementVirtuel.get_height()/2)

    def changer_texte_donnees(self):
        self.texteDonnees = creer_texte(nom=f"Donnees :", w=wF*(self.xMaxTexteDonnees-self.xMinTexteDonnees), h=hF*(self.yMaxTexteDonnees-self.yMinTexteDonnees), gras=False, italique=False, souligne=True, couleur=(150,150,150))
        self.positionTexteDonnees = (self.xMilieuTexteDonnees - self.texteDonnees.get_width()/2, self.yMilieuTexteDonnees - self.texteDonnees.get_height()/2)


    def run(self):
        self.enCourse = False
        self.temps = 0
        self.changer_texte_temps()
        while not self.quitterSimulation:
            horloge.tick(self.fps)
            #horloge.tick(30)
            if self.enCourse :
                self.temps += self.dt
                self.changer_texte_temps()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitterSimulation = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.enCourse = not self.enCourse
                        self.temps = 0
                        for athlete in self.lAthletes:
                            athlete.reset(reel=True, enCourse=self.enCourse)
                        self.changer_classement()
            self.tester_clavier()

            self.bouger()
            
            self.afficher()


pygame.init()
wF, hF = 1000, 600
fenetre = pygame.display.set_mode((wF, hF))
pygame.display.set_caption("Animation Triathlon, Mai-Juin 2026")
horloge = pygame.time.Clock()

simulation = Simulation()
simulation.run()

pygame.quit()