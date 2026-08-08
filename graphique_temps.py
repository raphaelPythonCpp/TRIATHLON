import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def couleur(c):
    return (max(0, -1 + 2*c), max(0, 1 - 2*c), 1 - abs(1 - 2*c))

def normalisation(l):
    lMin = min(l)
    lMax = max(l)

    if lMax == lMin:
        return [0 for _ in l]

    return [(x - lMin) / (lMax - lMin) for x in l]

def moyenne(l):
    return sum(l) / len(l)

def afficher():
    yMin = min(min(lTempsObjectifs1D), min(lTemps1D))
    yMax = max(max(lTempsObjectifs1D), max(lTemps1D))
    deltaY = yMax - yMin

    # ============================================================
    # Graphique des barres
    # ============================================================
    axeGraphiqueBar.clear()

    lYGB = lTemps1D
    lXGB = list(range(1, len(lYGB) + 1))
    lTGB = lTempsObjectifs1D
    lXTGB = []
    iSerie = 1
    for lT in lTempsObjectifs:
        lXTGB.append([])
        for t in lT:
            lXTGB[-1].append(iSerie)
            iSerie += 1

    if iModeCouleur == 0:
        lCGB = [couleurModeMonochrome for _ in lXGB]
    elif iModeCouleur == 1:
        l = [i for i, lTemps in enumerate(lTemps2D) for _ in lTemps]
        c = normalisation(l)
        lCGB = [couleur(x) for x in c]
    elif iModeCouleur == 2:
        c = normalisation(lYGB)
        lCGB = [couleur(x) for x in c]

    for lX, lT in zip(lXTGB, lTempsObjectifs):
        axeGraphiqueBar.plot(lX, lT, linestyle="--", linewidth=1, alpha=0.7, color="black", zorder=10)
    axeGraphiqueBar.bar(lXGB, lYGB, color=lCGB, alpha=1)

    xMinGB = min(lXGB)
    xMaxGB = max(lXGB)
    bordureXGB = 0.1 * (xMaxGB - xMinGB)

    axeGraphiqueBar.set_xlim(xMinGB - bordureXGB, xMaxGB + bordureXGB)
    axeGraphiqueBar.set_ylim(yMin - 0.1 * deltaY, yMax + 0.1 * deltaY)

    axeGraphiqueBar.set_xlabel("Tour n°")
    axeGraphiqueBar.set_ylabel("Temps (s)")
    axeGraphiqueBar.set_title("Graphique de toutes les séries")


    # ============================================================
    # Graphique simultané
    # ============================================================
    axeGraphiqueSimultane.clear()

    listeLYGS = lTemps2D
    lXGS = [list(range(1, len(lYGS) + 1)) for lYGS in listeLYGS]
    lXGS1D = [x for lX in lXGS for x in lX]
    lYGS1D = [y for lYGS in listeLYGS for y in lYGS]
    lTGS = lTempsObjectifs

    if iModeCouleur == 0:
        lCGS = [couleurModeMonochrome for _ in lYGS1D]
    elif iModeCouleur == 1:
        l = [i for i, lYGS in enumerate(listeLYGS) for _ in lYGS]
        c = normalisation(l)
        lCGS = [couleur(x) for x in c]
    elif iModeCouleur == 2:
        c = normalisation(lYGS1D)
        lCGS = [couleur(x) for x in c]

    for lX, lT in zip(lXGS, lTGS):
        axeGraphiqueSimultane.plot(lX, lT, linestyle="--", linewidth=1, alpha=0.7, color="black", zorder=10)
    axeGraphiqueSimultane.scatter(lXGS1D, lYGS1D, c=lCGS)

    xMinGS = min(lXGS1D)
    xMaxGS = max(lXGS1D)
    margeXGS = 0.1 * (xMaxGS - xMinGS)

    axeGraphiqueSimultane.set_xlim(xMinGS - margeXGS, xMaxGS + margeXGS)
    axeGraphiqueSimultane.set_ylim(yMin - 0.1 * deltaY, yMax + 0.1 * deltaY)

    axeGraphiqueSimultane.set_xlabel("Tour n°")
    axeGraphiqueSimultane.set_ylabel("Temps (s)")
    axeGraphiqueSimultane.set_title("Graphique de la superposition des séries")


    # ============================================================
    # Graphique vertical
    # ============================================================
    axeGraphiqueVertical.clear()

    listeLYGV = lTemps2D
    lXGV = [[i + 1 for _ in lYGV] for i, lYGV in enumerate(listeLYGV)]
    lXGV1D = [x for lX in lXGV for x in lX]
    lYGV1D = [y for lYGV in listeLYGV for y in lYGV]
    lTGV = [[moyenne(lT), moyenne(lT)] for lT in lTempsObjectifs]
    lXTGV = [[i-0.5, i+0.5] for i in range(1, len(lTGV)+1)]

    if iModeCouleur == 0:
        lCGV = [couleurModeMonochrome for _ in lYGV1D]
    elif iModeCouleur == 1:
        c = normalisation(lXGV1D)
        lCGV = [couleur(x) for x in c]
    elif iModeCouleur == 2:
        c = normalisation(lYGV1D)
        lCGV = [couleur(x) for x in c]

    for lX, lT in zip(lXTGV, lTGV):
        axeGraphiqueVertical.plot(lX, lT, linestyle="--", linewidth=1, alpha=0.7, color="black", zorder=10)
    axeGraphiqueVertical.scatter(lXGV1D, lYGV1D, c=lCGV, alpha=1)

    xMinGV = min(lXGV1D)
    xMaxGV = max(lXGV1D)
    margeXGV = 0.1 * (xMaxGV - xMinGV)

    axeGraphiqueVertical.set_xlim(xMinGV - margeXGV, xMaxGV + margeXGV)
    axeGraphiqueVertical.set_ylim(yMin - 0.1 * deltaY, yMax + 0.1 * deltaY)

    axeGraphiqueVertical.set_xlabel("Bloc n°")
    axeGraphiqueVertical.set_ylabel("Temps (s)")
    axeGraphiqueVertical.set_title("Graphique des Blocs")


    # ============================================================
    # Graphique d'erreur
    # ============================================================
    axeGraphiqueErreur.clear()

    lYGE = [moyenne(lY) for lY in lTemps2D]
    lYMinGE = [min(lY) for lY in lTemps2D]
    lYMaxGE = [max(lY) for lY in lTemps2D]
    lXGE = list(range(1, len(lTemps2D) + 1))
    lTGE = [[moyenne(lT), moyenne(lT)] for lT in lTempsObjectifs]
    lXTGE = [[i-0.5, i+0.5] for i in range(1, len(lTGE)+1)]

    if iModeCouleur == 0:
        lCGE = [couleurModeMonochrome for _ in lXGE]
    elif iModeCouleur == 1:
        c = normalisation(lXGE)
        lCGE = [couleur(x) for x in c]
    elif iModeCouleur == 2:
        c = normalisation(lYGE)
        lCGE = [couleur(x) for x in c]

    for lX, lT in zip(lXTGE, lTGE):
        axeGraphiqueErreur.plot(lX, lT, linestyle="--", linewidth=1, alpha=0.7, color="black", zorder=10)
    for i in range(len(lXGE)):
        axeGraphiqueErreur.errorbar(lXGE[i], lYGE[i], yerr=[[lYGE[i] - lYMinGE[i]], [lYMaxGE[i] - lYGE[i]]], fmt='o', capsize=5, color=lCGE[i], ecolor=lCGE[i], alpha=1)

    xMinGE = min(lXGE)
    xMaxGE = max(lXGE)
    margeXGE = 0.1 * (xMaxGE - xMinGE)

    axeGraphiqueErreur.set_xlim(xMinGE - margeXGE, xMaxGE + margeXGE)
    axeGraphiqueErreur.set_ylim(yMin - 0.1 * deltaY, yMax + 0.1 * deltaY)

    axeGraphiqueErreur.set_xlabel("Bloc n°")
    axeGraphiqueErreur.set_ylabel("Temps (s)")
    axeGraphiqueErreur.set_title("Graphique d'erreur des Blocs")

    fig.canvas.draw_idle()


def changer_mode_couleur(_):
    global iModeCouleur

    iModeCouleur = (iModeCouleur + 1) % len(lModesCouleur)
    boutonChangerModeCouleur.label.set_text(f"Mode {lModesCouleur[iModeCouleur]}")
    afficher()


"""....................A REMPLIR ....................."""
lTemps2D = [???]
lTempsObjectifs = [???]
texteTitre = "???"
"""...................FIN A REMPLIR...................."""


""".....................EXEMPLE........................

lTemps2D = [[49.18, 50.68, 49.97, 49.41],
            [48.86, 51.64, 50.70, 48.63],
            [49.12, 52.77, 50.77, 49.57],
            [50.83, 53.69, 52.74, 51.44],
            [51.42, 54.23, 53.10, 49.81]]
# Pour le temps, soit recopier l'exemple 1 si c'est toujours le même objectif, sinon l'exemple 2
lTempsObjectifs = [[50]*len(lT) for lT in lTemps2D] #ex 1
lTempsObjectifs = [[50, 50, 50, 50],                #ex 2
                   [50, 50, 50, 50],
                   [50, 50, 50, 50],
                   [50, 50, 50, 50],
                   [50, 50, 50, 50]]
texteTitre = "Graphique du 5*1000m D=4' sur piste"
......................FIN EXEMPLE......................."""


lTemps1D = [t for lTemps in lTemps2D for t in lTemps]
lTempsObjectifs1D = [t for lTemps in lTempsObjectifs for t in lTemps]

print(f"lTemps2D arrondie : {[[round(t, 1) for t in lT] for lT in lTemps2D]}")
print(f"lTempsMoyenParBloc : {[round(moyenne(lT), 1) for lT in lTemps2D]}")
print(f"lSommeTempsBlocs : {[round(sum(lT), 1) for lT in lTemps2D]}")

fig = plt.figure()
titre = fig.suptitle(texteTitre, fontsize=16, fontweight="bold", fontstyle="italic")

axeGraphiqueBar = plt.axes([0.05, 0.55, 0.4, 0.325])
axeGraphiqueSimultane = plt.axes([0.05, 0.1, 0.4, 0.325])
axeGraphiqueVertical = plt.axes([0.55, 0.55, 0.4, 0.325])
axeGraphiqueErreur = plt.axes([0.55, 0.1, 0.4, 0.325])

axeBoutonChangerModeCouleur = plt.axes([0.025, 0.925, 0.15, 0.05])
boutonChangerModeCouleur = Button(axeBoutonChangerModeCouleur, "None", color=(0.8, 0.8, 0.8), hovercolor=(0.5, 0.5, 0.5))
boutonChangerModeCouleur.on_clicked(changer_mode_couleur)

lModesCouleur = ["Monochrome", "Par bloc", "Par allure"]
iModeCouleur = -1
couleurModeMonochrome = (0, 0, 0.5)

changer_mode_couleur(None)

plt.show()


"""........................FONCTIONNEMENT........................

- Remplir les 3 variables dans la zone 'Remplir' comme dans l'exemple
  (tableau 2D des temps en sec + tempsObjectif/tour + distance/tour (inutile))

- Lancer le programme

- Changer de mode de couleur avec le bouton en haut à gauche (appuyer)

.........................FIN FONCTIONNEMENT........................."""
