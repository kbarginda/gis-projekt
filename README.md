# gis-projekt

Autor: Kayla Barginda 6066945 (kayla.barginda@hcu-hamburg.de) 
HafenCity Universität | GIT - Kurs: GIS Programmierung 
GitHub: kbanane (KB)

#----------------------------------------------------------------------#

Datenquellen: BKA (Kriminalitätsstatistik), ESRI (Basiskarte von Deutschland nach Länder aufgeteilt -> relevant: die Polygone der Bundesländer)

Daten stammen aus dem Jahr 2018 

BKA Daten nach:
1. Länder
    + Länder Fallentwicklung
2. Kreise
    + Kreise Fallentwicklung
3. Städte ab 100.000 EW  & Landeshauptstädte 
    +Fallentwicklung 

BKA Daten: .csv 
ESRI: .csv & Shapefile 

#----------------------------------------------------------------------#

Dieses Projekt wurde mit Jupyter Notebook (Python V 3.x, Jupyter Notebook V 6.x) erstellt.

(Notwendgie) Pakete: 
- Folium
- Shapely 
- Geopandas
- Pandas 
- Ipyleaflet
    Install via pip: pip install ipyleaflet
    Enable via: jupyter nbextension enable --py --sys-prefix ipyleaflet

#----------------------------------------------------------------------#
Notizen (intern, löschen)

JOIN auf Bundesländer (?) -> Geometrien 

Software: QGIS(? Plug-in?) + Python (Jupyter Notebook)