import pandas

fichier = pandas.read_html("S_Cadets.xls")
tableau = fichier[0]
#columns : ['Pl.', 'Dos', 'Unnamed: 2', 'Nom', 'Club', 'Sx', 'Cat', 'Par cat.', 'NATATION', 'T1', 'VELO', 'T2', 'CAP TOUR 1', 'CAP TOUR 2', 'CAP', 'Temps', 'Ecart', 'Moy']
tableau["Nom"] = tableau["Nom"].str.replace('\xa0', ' ')
for index, ligne in tableau.iterrows():
    print(
        ligne["Nom"],
        ligne["NATATION"],
        ligne["VELO"],
        ligne["CAP"],
        ligne["Temps"]
    )