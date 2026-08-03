import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np

def couleur(c):
    return (np.maximum(0, -1+2*c), np.maximum(0, 1-2*c), 1-np.abs(1-2*c))

def normalisation(l):
    return (l - np.min(l)) / (np.max(l)-np.min(l))

def afficher():
    yMin = np.min(lTemps1D)
    yMax = np.max(lTemps1D)
    deltaY = yMax-yMin

    axeGraphiqueBar.clear()
    lYGB = lTemps1D
    lXGB = np.arange(1, len(lYGB)+1)
    if (iModeCouleur == 0):
        lCGB = np.tile(couleurModeMonochrome, (len(lXGB), 1))
    elif (iModeCouleur == 1):
        c = normalisation(np.array([np.full(len(lTemps), i) for i, lTemps in enumerate(lTemps2D)]).flatten())
        lCGB = np.stack(couleur(c), axis=-1)
    elif iModeCouleur == 2:
        c = normalisation(lYGB)
        lCGB = np.stack(couleur(c), axis=-1)
    axeGraphiqueBar.bar(lXGB, lYGB, color=lCGB)
    axeGraphiqueBar.axhline(y=tempsObjectif, linestyle="--", linewidth=1, alpha=0.7, color="black")
    xMinGB, xMaxGB = np.min(lXGB), np.max(lXGB)
    bordureXGB = 0.1*(xMaxGB-xMinGB)
    axeGraphiqueBar.set_xlim(xMinGB-bordureXGB, xMaxGB+bordureXGB)
    axeGraphiqueBar.set_ylim(yMin-0.1*deltaY, yMax+0.1*deltaY)
    axeGraphiqueBar.set_xlabel("Tour n°")
    axeGraphiqueBar.set_ylabel("Temps (s)")
    axeGraphiqueBar.set_title("Graphique de toutes les séries")

    axeGraphiqueSimultane.clear()
    listeLYGS = lTemps2D
    lXGS = np.array([np.arange(1, len(lYGS)+1) for lYGS in listeLYGS])
    if iModeCouleur == 0:
        lCGS = np.tile(couleurModeMonochrome, (*lXGS.shape, 1))
    elif iModeCouleur == 1:
        c = normalisation(np.array([np.full(len(lYGS), i) for i, lYGS in enumerate(listeLYGS)]))
        lCGS = np.stack(couleur(c), axis=-1)
    elif iModeCouleur == 2:
        c = normalisation(listeLYGS)
        lCGS = np.stack(couleur(c), axis=-1)
    axeGraphiqueSimultane.scatter(lXGS, listeLYGS, c=lCGS.reshape(-1, 3))
    axeGraphiqueSimultane.axhline(y=tempsObjectif, linestyle="--", linewidth=1, alpha=0.7, color="black")
    xMinGS, xMaxGS = np.min(lXGS), np.max(lXGS)
    margeXGS = 0.1*(xMaxGS-xMinGS)
    axeGraphiqueSimultane.set_xlim(xMinGS-margeXGS, xMaxGS+margeXGS)
    axeGraphiqueSimultane.set_ylim(yMin-0.1*deltaY, yMax+0.1*deltaY)
    axeGraphiqueSimultane.set_xlabel("Tour n°")
    axeGraphiqueSimultane.set_ylabel("Temps (s)")
    axeGraphiqueSimultane.set_title("Graphique de la superposition des séries")

    axeGraphiqueVertical.clear()
    listeLYGV = lTemps2D
    lXGV = np.array([np.full(len(listeLYGV[i]), i+1) for i in range(len(listeLYGS))])
    if iModeCouleur == 0:
        lCGV = np.tile(couleurModeMonochrome, (*lXGV.shape, 1))
    elif iModeCouleur == 1:
        c = normalisation(lXGV)
        lCGV = np.stack(couleur(c), axis=-1)
    elif iModeCouleur == 2:
        c = normalisation(listeLYGV)
        lCGV = np.stack(couleur(c), axis=-1)
    axeGraphiqueVertical.scatter(lXGV, listeLYGV, c=lCGV.reshape(-1, 3))
    axeGraphiqueVertical.axhline(y=tempsObjectif, linestyle="--", linewidth=1, alpha=0.7, color="black")
    xMinGV, xMaxGV = np.min(lXGV), np.max(lXGV)
    margeXGV = 0.1*(xMaxGV-xMinGV)
    axeGraphiqueVertical.set_xlim(xMinGV-margeXGV, xMaxGV+margeXGV)
    axeGraphiqueVertical.set_ylim(yMin-0.1*deltaY, yMax+0.1*deltaY)
    axeGraphiqueVertical.set_xlabel("Bloc n°")
    axeGraphiqueVertical.set_ylabel("Temps (s)")
    axeGraphiqueVertical.set_title("Graphique des Blocs")

    axeGraphiqueErreur.clear()
    lYGE = np.array([np.mean(lY) for lY in lTemps2D])
    lYMinGE = np.array([np.min(lY) for lY in lTemps2D])
    lYMaxGE = np.array([np.max(lY) for lY in lTemps2D])
    lXGE = np.arange(1, len(lTemps2D)+1)
    if iModeCouleur == 0:
        lCGE = np.tile(couleurModeMonochrome, (*lXGE.shape, 1))
    elif iModeCouleur == 1:
        c = normalisation(lXGE)
        lCGE = np.stack(couleur(c), axis=-1)
    elif iModeCouleur == 2:
        c = normalisation(lYGE)
        lCGE = np.stack(couleur(c), axis=-1)
    for i in range(len(lXGE)):
        axeGraphiqueErreur.errorbar(lXGE[i], lYGE[i], yerr=[[lYGE[i]-lYMinGE[i]], [lYMaxGE[i]-lYGE[i]]], fmt='o', capsize=5, color=lCGE[i], ecolor=lCGE[i])
    axeGraphiqueErreur.axhline(y=tempsObjectif, linestyle="--", linewidth=1, alpha=0.7, color="black")
    xMinGE, xMaxGE = np.min(lXGE), np.max(lXGE)
    margeXGE = 0.1*(xMaxGE-xMinGE)
    axeGraphiqueErreur.set_xlim(xMinGE-margeXGE, xMaxGE+margeXGE)
    axeGraphiqueErreur.set_ylim(yMin-0.1*deltaY, yMax+0.1*deltaY)
    axeGraphiqueErreur.set_xlabel("Bloc n°")
    axeGraphiqueErreur.set_ylabel("Temps (s)")
    axeGraphiqueErreur.set_title("Graphique d'erreur des Blocs")

    fig.canvas.draw_idle()

def changer_mode_couleur(_):
    global iModeCouleur
    iModeCouleur = (iModeCouleur+1)%len(lModesCouleur)
    boutonChangerModeCouleur.label.set_text(f"Mode {lModesCouleur[iModeCouleur]}")

    afficher()

"""....................A REMPLIR ....................."""
lTemps2D = np.array([]) #s
tempsObjectif = 0 #s
distance = 0 #m
"""...................FIN A REMPLIR...................."""
""".....................EXEMPLE........................
lTemps2D = np.array([[49.18, 50.68, 49.97, 49.41], #s
                     [48.86, 51.64, 50.70, 48.63],
                     [49.12, 52.77, 50.77, 49.57],
                     [50.83, 53.69, 52.74, 51.44], 
                     [51.42, 54.23, 53.10, 49.81]])
tempsObjectif = 53 #s
distance = 250 #m
......................FIN EXEMPLE......................."""
lTemps1D = lTemps2D.flatten()
print(f"lTemps2D arrondie : {[[round(t, 1) for t in lT] for lT in lTemps2D.tolist()]}")

fig = plt.figure()
axeGraphiqueBar = plt.axes([0.05, 0.55, 0.4, 0.325])
axeGraphiqueSimultane = plt.axes([0.05, 0.1, 0.4, 0.325])
axeGraphiqueVertical = plt.axes([0.55, 0.55, 0.4, 0.325])
axeGraphiqueErreur = plt.axes([0.55, 0.1, 0.4, 0.325])

axeBoutonChangerModeCouleur = plt.axes([0.025, 0.925, 0.15, 0.05])
boutonChangerModeCouleur = Button(axeBoutonChangerModeCouleur, "None", color=(0.8, 0.8, 0.8), hovercolor=(0.5, 0.5, 0.5))
boutonChangerModeCouleur.on_clicked(changer_mode_couleur)
lModesCouleur = [("Monochrome"), ("Par bloc"), ("Par allure")]
iModeCouleur = -1
couleurModeMonochrome = (0, 0, 0.5)#(1, 0.84, 0)

plt.suptitle("Graphique du 5*1000m D=4' sur piste", fontsize=20, fontweight="bold", fontstyle="italic")
changer_mode_couleur(None)

plt.show()

"""........................FONCTIONNEMENT........................
- Remplir les 3 variables dans la zone 'Remplir' comme dans l'exemple (tableau 2D des temps en sec + tempsObjectif/tour + distance/tour (inutile))
- Lancer le programme
- Changer de mode de couleur avec le bouton en haut à gauche (appuyer)
.........................FIN FONCTIONNEMENT......................"""