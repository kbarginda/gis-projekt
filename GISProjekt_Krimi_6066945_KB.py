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
from folium import plugins
from folium.plugins.draw import Draw
import fiona
from shapely.geometry import *
import branca

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
from PyQt5 import QtWebEngineWidgets

def choroplethenKarte(k):
        '''
        Datenverwaltung
        
        '''
        #Paths
        path = os.getcwd()
        
        geo_daten = path + r"\Data\Landkreise_DE.geojson"
        bev_daten = path + r"\Data\bev_landkreis.csv"
        
        
        #Geodaten: Landkreise + BKA Daten (JOINED)
        df = gpd.read_file(geo_daten)
        df.head()
        
        #Relevante Daten aus dem Dataframe laden 
        landkreise = df[['GEN', 'geometry']]
        landkreise.set_index('GEN')
        landkreise.head()
        
        #Stats
        df_2 = pd.read_table(bev_daten)
        df_2.head()
        
        #Kriminalitätsdaten 
        krimi_daten = df_2.copy()
        krimi_daten.head()
        
        #obj_int = {'erfasste_Faelle': int} #erfasste_Faelle wird als Object kopiert. Muss wieder als INT gespeichert werden
        #krimi_daten = krimi_daten.astype(obj_int)
        
        stats = krimi_daten
        
        stats['krimi'] = (krimi_daten['erfasste_Faelle']/krimi_daten['bev']) * 100000
        
        #Testing
        #display(krimi_daten)
        
        
        #Mittelpunkte der Polygone (pro Landkreise)
        punkte = df[['GEN','geometry']].copy()
        punkte['geometry'] = punkte['geometry'].centroid
        punkte.head()
        
        folium.GeoJson(geo_daten, 
               name="Landkreise",
               show = False,
               ).add_to(k)

        folium.Choropleth(geo_data=geo_daten,
            data=stats,
            columns=['GEN', 'krimi'],
            key_on='feature.properties.GEN',
            fill_opacity=0.7, line_opacity=0.2,
            fill_color = 'PuRd',
            legend_name='Allgemeine Kriminalität pro Landkreis (pro 100.000 Einwohner)',
            name='Krimi Statistik').add_to(k)

        
#Karte
class Karte(QWidget):
    def __init__(self):
        
        #class specs
        super().__init__()
        self.setWindowTitle('Kriminalität in Deutschland')
        #self.view = QWebEngineView()
        layout = QVBoxLayout()
        self.setLayout(layout)

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

        choroplethenKarte(k)
        
        
        
        #Layer Control
        folium.LayerControl().add_to(k)

   


        temp_file = QtCore.QTemporaryFile("tempMap.html", self)
        
        if temp_file.open():
            k.save(temp_file.fileName())
            url = QtCore.QUrl.fromLocalFile(temp_file.fileName())
            
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