# gis-projekt

Autor: Kayla Barginda 6066945 (kayla.barginda@hcu-hamburg.de) 
HafenCity Universität | M.sc. Geodäsie und Geoinformatik (GIT) | Kurs: GIS Programmierung 
GitHub: kbanane (KB)

#----------------------------------------------------------------------#
#Datenquellen#

Daten stammen aus dem Jahr 2018 

Daten: 
BKA: https://1drv.ms/u/s!ApFsD4A1YvDciQBLcDkubcQPMjbl?e=DMs8rw
ESRI: https://1drv.ms/u/s!ApFsD4A1YvDciQcODzKBC60iLMC6?e=G9Cvwc

BKA Daten nach:
1. Länder
    + Länder Fallentwicklung
2. Kreise
    + Kreise Fallentwicklung


BKA Daten:
https://www.bka.de/DE/AktuelleInformationen/StatistikenLagebilder/PolizeilicheKriminalstatistik/PKS2018/pks2018_node.html
	Quellenangabe:(PKS Bundeskriminalamt, 2018, PKS-Tabellen 2018: F-03-T01-Kreise)
	Datei: BKA-LKS-F-03-T01-Kreise_csv.csv 

Landkreisdaten:
http://opendatalab.de/projects/geojson-utilities/#

NUTS-Klassifikationsdaten: 
(Eurostat)
https://www.esf.de/portal/SharedDocs/PDFs/DE/FP%202014-2020/nuts-klassifikation.pdf?__blob=publicationFile&v=4

Bevölkerungsdaten:
https://www.destatis.de


#----------------------------------------------------------------------#
#Packages#

Dieses Projekt wurde mit Python V 3.x erstellt. UI wurde mit PyQt5 erstellt.

Notwendige Packages: 
- Folium
- Shapely 
- Geopandas
- Pandas 
- PyQt5
- Qt WebEngine 

#----------------------------------------------------------------------#
#Notizen (intern, löschen)#

ä,ö,ü,ß => deadly 

Erledigt: 
	- Choroplethenkarte (Grundlage, Feinheiten fehlen noch)
	- % Krimi. pro Landkreis
	- Tooltip popup 
	- Interface mit Tabelle + Slider (muss noch programmiert werden)
	- Punkt + auslesen des Wertes 
	
To Do:
	- Link slider to buffer around point 
		-> slider controls the buffer's radius 
	- Button "berechnen" calculates the Krimiwert
		Algorithm: 
			1. In which polygon is the point located?
				- Take value from this polygon, calculate the distance the point is from the centre of the placed polygon
			2. What polygons cross paths with the buffer? 
				- calc the distance from the center of the overlapping polygon to the point
			3. calc the weighted "Krimiwert" from this (Krimiwert is valid for entire polygon
				
