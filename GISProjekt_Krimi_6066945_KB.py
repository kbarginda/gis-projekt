# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 17:45:17 2021

@author: Kayla
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

from haversine import haversine
from folium.plugins.draw import Draw

from PyQt5.QtWidgets import QApplication, QWidget, QDockWidget, QHBoxLayout, QVBoxLayout, QBoxLayout, QSlider,QTableView, QLabel, QPlainTextEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel

'''
Datenverwaltung

'''

#RENAME TO CAP NAMES BC GLOBAL 

#Paths
path = os.getcwd()

geo_daten = path + "/Data/Landkreise_DE.geojson"
bev_daten = path + "/Data/bev_landkreis2.csv"

#Geodaten: Landkreise + BKA Daten (JOINED)
df = gpd.read_file(geo_daten)
df.head()


#Relevante Daten aus dem Dataframe laden 
landkreise = df[['GEN', 'geometry']]
landkreise.set_index('GEN')
landkreise.head()

#Stats
df_2 = pd.read_csv(bev_daten, delimiter=";")
df_2.head()

#Kriminalitätsdaten 
krimi_daten = df_2.copy()
krimi_daten.head()


stats = krimi_daten

stats['krimi'] = round((krimi_daten['erfasste_Faelle']/krimi_daten['bev']) * 100000,0)

geoDaten = df.copy()
geoDaten2 = geoDaten[['NUTS', 'geometry']]

stats2 = stats[['NUTS', 'krimi']]

geoKrimi = geoDaten2.merge(stats2, how='inner', on='NUTS')


#Mittelpunkte der Polygone (pro Landkreise)
punkte = df[['GEN', 'NUTS', 'geometry']].copy()
punkte['geometry'] = punkte['geometry'].centroid
punkte.head()

POIS = punkte['geometry']
POIS = MultiPoint(POIS)


#SET GLOBALS 
point = None
currentLocation = None
nearestRegion = None
dist = None
krimiStats = None
total = None 

#basiskarte: choroplethenkarte
def choroplethenKarte(k):
        
        
        #set for custom choropleth
        krimiDict = stats.set_index("NUTS")['krimi']

        #check and get rid of any spaces 
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
                color = '#df65b0'
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
            
        folium.GeoJson(geo_daten, 
               name="Landkreise",
               show = True,
               tooltip = folium.features.GeoJsonTooltip(fields = ['GEN'],
                                                        aliases = ['Landkreis: '],
                                                        style=("background-color: white; color: black; font-family: arial; font-size:12px"),
                                                        sticky=True),
               style_function = setFarbe
               ).add_to(k)
    
        k.save("map.html")



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
    
    
#application widnow
class Karte(QtWidgets.QMainWindow):
    def __init__(self):
      
        #initialise class
        super().__init__()
        self.initWindow()

    #set and define window 
    def initWindow(self): 
        self.setWindowTitle('Kriminalität in Deutschland')
        self.kartenUI()
        self.showMaximized()
        

            
    def kartenUI(self):
       
        '''
        ADD KRIMI STATS TABLE
        '''
        windowTabelle = stats[['GEN', 'bev', 'erfasste_Faelle', 'krimi']].copy()
        
        def getCoords(coords):
            #print(coords)
            global point
            point = Point(coords)#Convert to shapely point
            

            polygon = df.loc[df['geometry'].contains(point), 'GEN'].item()
            
            global currentLocation
            
            currentLocation = polygon

            
            nearest_geom = nearest_points(point, POIS)
            
            for geom in nearest_geom: 
                global nearestRegion
                global dist
                nearestRegion = df.loc[df['geometry'].contains(geom), 'GEN'].item()

           
            distances = []
            for i in geoKrimi.values:
                dist = round(point.distance(i[1]),2)
                distances.append(dist)
  
            krimiWerte = geoKrimi['krimi'].to_numpy() #convert to numpy
            
            
            """
            CALC KRIMI WERT
            """
            R = 0.7 #decayrate, ca. 80 km 

            weights = np.exp(-1*np.asarray(distances) / R)
            weights = weights / np.sum(weights)
            
            global total
            total = round(np.sum(weights * np.asarray(krimiWerte)),0)

        
        """ LABELS ETC FOR GUI """

        appText = QLabel()
        
        appText.setText("Kriminalität in Deutschland")
        appText.setAlignment(Qt.AlignLeft)

        
        infos = QLabel()   
        outputText = QLabel() 

        infos.setText("Der Puffer des Punktes beträgt ca. 80 km (1 Grad lon/lat).\nDie berechnete Gesamtkriminalität nimmt exponentiell in Bezug auf den gesetzten Puffer ab.")
        
        
        def changeText(event):
            outputText.setText("Aktuelle Koordinaten: " + str(point) +
                               "\n" + "Aktueller Landkreis: " + str(currentLocation) + "\n"
                               "Nächstgelegene Landkreise: " + str(nearestRegion) + "\n" + 
                               "Gewichtete Gesamtkriminalität: " + str(total))
    
        button = QPushButton('Berechnen!')
        button.setFixedSize(100,32)
        button.clicked.connect(changeText)
        

        #defines my QT Table
        self.table = QtWidgets.QTableView()
        self.model = KrimiTabelle(windowTabelle)
        self.table.setModel(self.model)
        self.table.setColumnWidth(0,200)
        self.table.setColumnWidth(2, 120)
        self.table.setFixedSize(550,200)
    
        
        
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(50, 50, 50, 50)

        centralWindow = QtWidgets.QWidget() #main widget viewport
        self.setCentralWidget(centralWindow)
        layout = QtWidgets.QVBoxLayout(centralWindow)   #create vertical layout
        
        widget_container = QtWidgets.QWidget() #creates a container for my widgets
        hLayout = QtWidgets.QHBoxLayout(widget_container)   #creates a horizontal container for my widgets
        
        internalLayout = QtWidgets.QGridLayout() #creates grid layout within the horizontal layout 
        hLayout.addLayout(internalLayout)   #add my grid box to the horizontal layout out(layout within layout)

        
        internalLayout.addWidget(appText)
        internalLayout.addWidget(infos)
        internalLayout.addWidget(outputText)
        internalLayout.addWidget(button)

        
        
        hLayout.addWidget(self.table) # add krimi table
         
        layout.addWidget(widget_container)


#ADD LEGEND!?!?!?!?
        bildLabel = QLabel()
        legende = QPixmap(path + 'legende.jpg')
        bildLabel.setPixmap(legende)
        
        dock = QDockWidget("Legende")
        dock.setGeometry(100,100,500,400)
        dock.setWidget(bildLabel)
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
        
        choroplethenKarte(k) #add choropleth map
    
        folium.LayerControl().add_to(k) #layer control

   
        '''
        SAVE HTML MAP TO OPEN IN QT ENGINE 
        '''

        temp_file = QtCore.QTemporaryFile("tempMap.html", self)
    
        
        if temp_file.open():
            k.save(temp_file.fileName())
            url = QtCore.QUrl.fromLocalFile(temp_file.fileName())
            
            '''
            GET POINT JS VALUE 
            '''            
            class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):

                def javaScriptConsoleMessage(self, level, msg, line, sourceID):
                    coords_dict = json.loads(msg)
                    temp_coordinateStorage = coords_dict['geometry']['coordinates']
                    
                    getCoords(temp_coordinateStorage)
  
            view = QtWebEngineWidgets.QWebEngineView()
            page = WebEnginePage(view)
            view.setPage(page)
            view.load(url)

        layout.addWidget(view)

 
#GUI
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