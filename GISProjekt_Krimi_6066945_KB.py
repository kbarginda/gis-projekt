# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 17:45:17 2021

@author: Kayla
"""

import sys, os, json, geojson
import io

import pandas as pd
import geopandas as gpd

import folium
#from folium import plugins
from folium.plugins.draw import Draw

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QBoxLayout, QSlider,QTableView, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView

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

stats['krimi'] = (krimi_daten['erfasste_Faelle']/krimi_daten['bev']) * 100000

#basiskarte: choroplethenkarte
def choroplethenKarte(k):
        """     
        '''
        Datenverwaltung
        
        '''
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

        stats['krimi'] = (krimi_daten['erfasste_Faelle']/krimi_daten['bev']) * 100000
        """
        
        #Mittelpunkte der Polygone (pro Landkreise)
        punkte = df[['NUTS','geometry']].copy()
        punkte['geometry'] = punkte['geometry'].centroid
        punkte.head()
        
        
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
        
        
        """folium.Choropleth(geo_data=geo_daten,
            data=stats,
            columns=['GEN', 'krimi'],
            key_on='feature.properties.GEN',
            fill_opacity=0.7, line_opacity=0.2,
            fill_color = 'PuRd',
            legend_name='Allgemeine Kriminalität pro Landkreis (pro 100.000 Einwohner)',
            name='Krimi Statistik').add_to(k)"""
     
    
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
        #self.view = QWebEngineView()
        #layout = QVBoxLayout()
        #self.setLayout(layout)
    
    #set and define window 
    def initWindow(self): 
        self.setWindowTitle('Kriminalität in Deutschland')
        self.kartenUI()
        self.showMaximized()
        
    def kartenUI(self):
        bufferSlider = QSlider(Qt.Horizontal, self)
        bufferSlider.setGeometry(30, 40, 200, 30)
        #bufferSlider.valueChanged[int].connect(changeValue)
        bufferSlider.setMinimum(0)
        bufferSlider.setMaximum(500)
        
        
        '''
        ADD KRIMI STATS TABLE
        '''
        windowTabelle = stats[['GEN', 'bev', 'erfasste_Faelle', 'krimi']].copy()
  
        #defines my QT Table
        self.table = QtWidgets.QTableView()
        self.model = KrimiTabelle(windowTabelle)
        self.table.setModel(self.model)
        self.table.setColumnWidth(0,200)
        self.table.setColumnWidth(2, 120)
        self.table.setFixedSize(550,200)
        
        #probably a place holder idk yet 
        getKrimiwert_button = QtWidgets.QPushButton(self.tr("Krimiwert berechnen"))
        getKrimiwert_button.setFixedSize(200, 50)
        
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(50, 50, 50, 50)

        centralWindow = QtWidgets.QWidget() #main widget viewport
        self.setCentralWidget(centralWindow)
        layout = QtWidgets.QVBoxLayout(centralWindow)   #create vertical layout
        
        widget_container = QtWidgets.QWidget() #creates a container for my widgets
        hLayout = QtWidgets.QHBoxLayout(widget_container)   #creates a horizontal container for my widgets
        
        internalLayout = QtWidgets.QGridLayout() #creates grid layout within the horizontal layout 
        hLayout.addLayout(internalLayout)   #add my grid box to the horizontal layout out(layout within layout)
        
        #internalLayout.setSpacing(0)
        internalLayout.addWidget(bufferSlider)
        internalLayout.addWidget(getKrimiwert_button)
        #internalLayout.addStretch()
        
        hLayout.addWidget(self.table) # add krimi table
        #verticalLayout.addStretch()
         
        layout.addWidget(widget_container)


        

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
                    'polygon': False,
                    'circle' : True
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
                    coords = coords_dict['geometry']['coordinates']
                    print(coords)
        
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