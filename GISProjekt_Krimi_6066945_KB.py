# -*- coding: utf-8 -*-
"""
KAYLA BARGINDA (6066945)

Geo-M-303-100 GIS-Programmierung



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

"""

import sys, os, json, geojson
import io

import pandas as pd
import geopandas as gpd
import numpy as np 
import shapely 
from shapely import geometry
from shapely.geometry import shape, GeometryCollection, Point, MultiPoint
from shapely.ops import nearest_points
import folium

from folium.plugins.draw import Draw

from PyQt5.QtWidgets import QApplication, QWidget, QDockWidget, QHBoxLayout, QVBoxLayout, QBoxLayout, QSlider,QTableView, QLabel, QPlainTextEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel

'''
Datenverwaltung

**ALLE DATEN SIND GLOBAL**

'''

#PATHs
PATH = os.getcwd()

GEO_DATEN = PATH + "/Data/landkreise_DE.geojson"
BEV_DATEN = PATH + "/Data/bev_landkreis2.csv"

#Geodaten: LANDKREISE + BKA Daten (JOINED)
DF = gpd.read_file(GEO_DATEN)
DF.head()


#Relevante Daten aus dem Dataframe laden 
LANDKREISE = DF[['GEN', 'geometry']]
LANDKREISE.set_index('GEN')
LANDKREISE.head()

#KRIMI_STATS
DF_2 = pd.read_csv(BEV_DATEN, delimiter=";")
DF_2.head()

#Kriminalitätsdaten 
KRIMI_DATEN = DF_2.copy()
KRIMI_DATEN.head()

KRIMI_STATS = KRIMI_DATEN
KRIMI_STATS['krimi'] = round((KRIMI_DATEN['erfasste_Faelle']/KRIMI_DATEN['bev']) * 100000,0)

GEO_DATEN_TEMP = DF.copy()
GEO_DATEN_TEMP2 = GEO_DATEN_TEMP[['NUTS', 'geometry']]
KRIMI_STATS2 = KRIMI_STATS[['NUTS', 'krimi']]

GEO_KRIMI = GEO_DATEN_TEMP2.merge(KRIMI_STATS2, how='inner', on='NUTS')


#Mittelpunkte der Polygone (pro LANDKREISE)
LANDKREIS_PUNKTE = DF[['GEN', 'NUTS', 'geometry']].copy()
LANDKREIS_PUNKTE['geometry'] = LANDKREIS_PUNKTE['geometry'].centroid
LANDKREIS_PUNKTE.head()

POIS = LANDKREIS_PUNKTE['geometry']
POIS = MultiPoint(POIS)


#GLOBALE VARIABLEN
CURRENT_POINT = None
CURRENT_LOC = None
NEAREST_LOC = None
DIST = None
#krimiKRIMI_STATS = None
KRIMI_GESAMT = None 

#benutzerdefinierte Choroplethenkarte
def choroplethenKarte(k):
        

        krimiDict = KRIMI_STATS.set_index("NUTS")['krimi']

        #löscht alle Leerzeichen in den Daten
        for key in krimiDict.keys():
            s = key.replace(' ', '')
            krimiDict[s] = krimiDict[key]


        
        def setFarbe(feature):
            color = ''
            identifier = feature["properties"]["NUTS"]
            krimiWert = krimiDict.loc[identifier]
            if (krimiWert < 4500):
                color = '#f1eef6'
            elif (krimiWert > 4500 and krimiWert < 6700):
                color = '#d4b9da'
            elif (krimiWert > 6700 and krimiWert < 8900):
                color = '#c994c7'
            elif (krimiWert > 8900 and krimiWert < 11000):
                color = '#DF65b0'
            elif (krimiWert > 11000 and krimiWert < 13400):
                color = '#dd1c77'
            elif (krimiWert > 13400):
                color ='#980043'
            else:
                color = ''
            return {"fillColor": color if color else "", 
                                                 "fillOpacity": 0.7,
                                                 "color":"black", 
                                                 "weight": 1,
                                                 "line_opacity":0.2}
            
        folium.GeoJson(GEO_DATEN, 
               name="LANDKREISE",
               show = True,
               tooltip = folium.features.GeoJsonTooltip(fields = ['GEN'],
                                                        aliases = ['Landkreis: '],
                                                        style=("background-color: white; color: black; font-family: arial; font-size:12px"),
                                                        sticky=True),
               style_function = setFarbe
               ).add_to(k)
    
        k.save("map.html")


#Tabelle für PyQT. Stellt eine Tabelle da, mit Kriminalitätsstatistiken 
class KrimiTabelle(QAbstractTableModel):
    
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data
    
    def rowCount(self, parent=None):
        return self._data.shape[0]
    
    def columnCount(self, parent=None):
        return self._data.shape[1]
    
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
    
    
#Applikationsfenster
class Karte(QtWidgets.QMainWindow):
    def __init__(self):
      
        super().__init__()
        self.initWindow()

    #definiert das Fenster
    def initWindow(self): 
        self.setWindowTitle('Kriminalität in Deutschland')
        self.kartenUI()
        self.showMaximized()
        
    #UI für Karte + Berechnungen 
    def kartenUI(self):
       
        '''
        ADD KRIMI KRIMI_STATS TABLE
        '''
        windowTabelle = KRIMI_STATS[['GEN', 'bev', 'erfasste_Faelle', 'krimi']].copy()
        
        def getCoords(coords):
            #print(coords)
            global CURRENT_POINT
            CURRENT_POINT = Point(coords)#Convert to shapely point
            

            polygon = DF.loc[DF['geometry'].contains(CURRENT_POINT), 'GEN'].item()
            
            global CURRENT_LOC
            
            CURRENT_LOC = polygon

            
            nearest_geom = nearest_points(CURRENT_POINT, POIS)
            
            for geom in nearest_geom: 
                global NEAREST_LOC
                global DIST
                NEAREST_LOC = DF.loc[DF['geometry'].contains(geom), 'GEN'].item()

           
            distances = []
            for i in GEO_KRIMI.values:
                DIST = round(CURRENT_POINT.distance(i[1]),2)
                distances.append(DIST)
  
            krimiWerte = GEO_KRIMI['krimi'].to_numpy()
            
            
            '''
            Gewichtete Funktion, die die gesamte (gewichtete) Kriminalität in Deutschland zu einem bestimmten Zeitpunkt berechnet.
            R = 1, Entspricht ca. 100 km (Zerfallsrate)
            '''
            
            R = 1 #Zerfallsrate, ca. 100 km 

            weights = np.exp(-1*np.asarray(distances) / R)
            weights = weights / np.sum(weights)
            
            global KRIMI_GESAMT
            KRIMI_GESAMT = round(np.sum(weights * np.asarray(krimiWerte)),0)

        
        '''
        Layout-Definitionen für PyQt-Widgets 
        '''

        appText = QLabel()
        
        appText.setText("Kriminalität in Deutschland")
        appText.setAlignment(Qt.AlignLeft)

        
        infos = QLabel()   
        outputText = QLabel() 

        infos.setText("Der Puffer des Punktes beträgt ca. 100 km (1 Grad lon/lat).\nDie berechnete Gesamtkriminalität nimmt exponentiell in Bezug auf den gesetzten Puffer ab.")
        
        
        def changeText(event):
            outputText.setText("Aktuelle Koordinaten: " + str(CURRENT_POINT) +
                               "\n" + "Aktueller Landkreis: " + str(CURRENT_LOC) + "\n"
                               "Nächstgelegene LANDKREISE: " + str(NEAREST_LOC) + "\n" + 
                               "Gewichtete Gesamtkriminalität: " + str(KRIMI_GESAMT))
    
        button = QPushButton('Berechnen!')
        button.setFixedSize(100,32)
        button.clicked.connect(changeText)
        

        #Setzt die Anzeigeparameter der QT-Tabelle
        self.table = QtWidgets.QTableView()
        self.model = KrimiTabelle(windowTabelle)
        self.table.setModel(self.model)
        self.table.setColumnWidth(0,200)
        self.table.setColumnWidth(2, 120)
        self.table.setFixedSize(550,200)
    
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(50, 50, 50, 50)

        centralWindow = QtWidgets.QWidget() #Hauptwidget viewport
        self.setCentralWidget(centralWindow)
        layout = QtWidgets.QVBoxLayout(centralWindow) #Vvrtikales Layout (für Widgets)
        
        widget_container = QtWidgets.QWidget() #Widget-Behälter
        hLayout = QtWidgets.QHBoxLayout(widget_container)  #horizontales Layout (für Widgets)
        
        internalLayout = QtWidgets.QGridLayout() #Gitter-Layout im horizontalen Layout
        hLayout.addLayout(internalLayout)   #Gitter-Layout wird zum horizontalen Layout hinzugefügt
        
        internalLayout.addWidget(appText)
        internalLayout.addWidget(infos) #
        internalLayout.addWidget(outputText) #Output Text 
        internalLayout.addWidget(button) #Butten - "Berechnen"

        hLayout.addWidget(self.table) #Krimitabelle
        layout.addWidget(widget_container)

        imagePATH = PATH + '/Data/legende.png'
        image = QLabel()
        
        legende = QPixmap(imagePATH)
        image.setPixmap(legende)
        legende = legende.scaled(20,20, Qt.KeepAspectRatio)
        dock = QDockWidget("Legende", self)
        #dock.setGeometry(0,0,0,0)
        
        dock.setWidget(image)
        dock.setFloating(True)

        '''
        Basiskarten/ Kartenlayer
        '''
        location = [51.133481, 10.018343]
        zoom = 6
    
        k = folium.Map(
            location=location, 
            zoom_start=zoom)
    
        folium.TileLayer('Cartodb Positron').add_to(k)

        drawPOI = Draw(
            position = 'topleft',
            draw_options = {'polyline': False, 
                    'rectangle': False, 
                    'circlemarker': False,
                    'marker': True,
                    'polygon': False,
                    'circle' : False
                    }
            )
        drawPOI.add_to(k)
        
        choroplethenKarte(k) #Choroplethenkarte
    
        folium.LayerControl().add_to(k) #Layerkontrolle 

        '''
        PyQt Layer-Einstellungen 
        '''
        
        #Speichert die Karte als HTML damit PyQt die Karten darstellen kann
        temp_file = QtCore.QTemporaryFile("tempMap.html", self)

        if temp_file.open():
            k.save(temp_file.fileName())
            url = QtCore.QUrl.fromLocalFile(temp_file.fileName())
            
         
            #Ruft den JS-Punktwert ab
            class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):

                def javaScriptConsoleMessage(self, level, msg, line, sourceID):
                    coords_dict = json.loads(msg)
                    temp_coordinateStorage = coords_dict['geometry']['coordinates']
                    
                    getCoords(temp_coordinateStorage)
            
            #Für die Hauptseite
            view = QtWebEngineWidgets.QWebEngineView()
            page = WebEnginePage(view)
            view.setPage(page)
            view.load(url)
        
        layout.addWidget(view)

 
'''
Führt die PyQt Webengine-Schnittstelle aus
'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget{font-size:14px};
        ''')
    
    meineKarte = Karte()
    meineKarte.show()
    
    try:
        sys.exit(app.exec_())
    
    except SystemExit:
        print('Bye bye...')