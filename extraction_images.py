from PIL import Image
from collections import deque
import os

lNomImages = ["asset_textes_2.png"]

dossierOutput = "EXTRACTIONS"
os.makedirs(dossierOutput, exist_ok=True)
for nomFichier in os.listdir(dossierOutput):
    chemin = os.path.join(dossierOutput, nomFichier)
    os.remove(chemin)

lDXY = [(dx,dy) for dx in range(-1,2) for dy in range(-1,2) if dx != 0 or dy != 0]
seuilAlpha = 50
surfaceMin = 30 #px

iImage = 0

for nomImage in lNomImages:
    image = Image.open(nomImage).convert("RGBA")
    pixels = image.load()
    w,h = image.size
    vu = [[False]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if vu[y][x] or pixels[x,y][3] < seuilAlpha:
                continue
            pile = deque([(x,y)])
            vu[y][x] = True
            xMin, xMax, yMin, yMax = x, x, y, y
            while pile:
                x,y = pile.popleft()
                for dx,dy in lDXY:
                    x2 = x+dx
                    y2 = y+dy
                    if (0 <= x2 < w) and (0 <= y2 < h) and not vu[y2][x2] and pixels[x2,y2][3] > seuilAlpha:
                        pile.append((x2,y2))
                        vu[y2][x2] = True
                        xMin = min(xMin, x2)
                        xMax = max(xMax, x2)
                        yMin = min(yMin, y2)
                        yMax = max(yMax, y2)
            if (xMax+1-xMin)*(yMax+1-yMin) >= surfaceMin:
                image2 = image.crop((xMin, yMin, xMax+1, yMax+1))
                image2.save(f"{dossierOutput}\\{iImage}.png")
                iImage += 1
