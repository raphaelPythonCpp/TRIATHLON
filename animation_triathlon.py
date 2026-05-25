import gpxpy

with open("triathlon_S_2.gpx", "r", encoding="utf-8") as fichier:
    triathlon = gpxpy.parse(fichier)

lParcours, listeLPoints = [], []
for parcours in triathlon.tracks:
    lParcours.append(parcours.name)
    listeLPoints.append([])
    for segment in parcours.segments:
        for point in segment.points:
            listeLPoints[-1].append((point.latitude, point.longitude))
for parcours, lPoints in zip(lParcours, listeLPoints):
    print(parcours, lPoints[:10], '\n\n')
