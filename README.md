# gis-projekt

Datenquelle: BKA (Kriminalitätsstatistik), ESRI (Basiskarte von Deutschland nach Länder aufgeteilt -> relevant: die Polygone der Bundesländer)
Daten stammen aus dem Jahr 2018 

Daten: 
BKA: https://1drv.ms/u/s!ApFsD4A1YvDciQBLcDkubcQPMjbl?e=DMs8rw
ESRI: https://1drv.ms/u/s!ApFsD4A1YvDciQcODzKBC60iLMC6?e=G9Cvwc

BKA Daten nach:
1. Länder
    + Länder Fallentwicklung
2. Kreise
    + Kreise Fallentwicklung
3. Städte ab 100.000 EW  & Landeshauptstädte 
    +Fallentwicklung 

BKA Daten: .csv 
ESRI: .csv & Shapefile 

JOIN auf Bundesländer (?) -> Geometrien 

Software: QGIS + Python 

(Notwendgie) Pakete: 
- Folium
- Shapely 
- Geopandas
- Pandas 

Jupyter Notebook oder direkt in Python?? (gute Frage)
Interaktive Tools? 
-> Maybe 

** Mit Python werden die Karten als HTML gespeichert (Folium) ** 