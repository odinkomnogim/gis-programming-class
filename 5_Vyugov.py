q = QgsProject.instance()

stations_path = 'C:/Users/vyugo/OneDrive/Documents/Geoinformatics/sem_2/stations.geojson'
districts_path = 'C:/Users/vyugo/OneDrive/Documents/Geoinformatics/sem_2/districts.geojson'

stations = QgsVectorLayer(path_stations, 'stations')
districts = QgsVectorLayer(path_districts, 'districts')

new_stations = QgsVectorLayer('Polygon?crs=EPSG:3857', "new_stations", "memory")
prov = new_stations.dataProvider()
prov.addAttributes(stations.fields())
new_stations.updateFields() 

some_value = 25
radius = some_value * 25 

for i in stations.getFeatures():
    if i['colour'] == 'green':
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(i.geometry().asPoint()).buffer(radius, 8))
        feat.setAttributes(i.attributes())
        prov.addFeature(feat)

new_districts = QgsVectorLayer('Polygon?crs=EPSG:3857', "new_districts", "memory") 
new_districts.updateFields()
new_provider = new_districts.dataProvider()
new_provider.addAttributes(districts.fields())

for i in districts.getFeatures():
    districts_geometry = i.geometry()
    for j in new_stations.getFeatures():
        stations_geometry = j.geometry()
        if stations_geometry.intersects(districts_geometry):
            new_feat = QgsFeature()
            new_feat.setGeometry(districts_geometry) 
            new_feat.setAttributes(i.attributes()) 
            new_provider.addFeature(new_feat)
            break

new_districts.updateExtents() 
q.addMapLayer(new_districts)

new_stations.updateExtents()
q.addMapLayer(new_stations)
stations.setSubsetString('') #Для наглядности