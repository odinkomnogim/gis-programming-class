ds_st = QgsVectorLayer('C:/Users/yermakoovaa/Desktop/gis-programming-class-assignment_5/stations.geojson', 'stations')
ds_dtr = QgsVectorLayer('C:/Users/yermakoovaa/Desktop/gis-programming-class-assignment_5/districts.geojson', 'districts')

QgsProject.instance().addMapLayer(ds_st)
QgsProject.instance().addMapLayer(ds_dtr)

buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'buffer', 'memory')
buffer_layer.dataProvider().addAttributes(ds_st.fields())
buffer_layer.updateFields()

with edit(buffer_layer):
    for station in ds_st.getFeatures():
        if station['station'] == 'subway':
            buffer_geom = station.geometry().buffer((int(station['depth']) + 5) * 25, 8)
            new_feature = QgsFeature(buffer_layer.fields())
            new_feature.setGeometry(buffer_geom)
            new_feature.setAttributes(station.attributes())
            buffer_layer.dataProvider().addFeature(new_feature)

QgsProject.instance().addMapLayer(buffer_layer)

selected_ids = set()
for district in ds_dtr.getFeatures():
    district_geom = district.geometry()
    
    for buffer_feat in buffer_layer.getFeatures():
        depth = int(buffer_feat['depth'])
        if depth < 60 and district_geom.intersects(buffer_feat.geometry()):
            selected_ids.add(district.id())
            break  

ds_dtr.selectByIds(list(selected_ids))
print(f"Выделено районов: {len(selected_ids)} из {ds_dtr.featureCount()}")