path_stations = 'C:/Users/Egor/Desktop/gis-programming-class-assignment_5/stations.geojson'
path_districts = 'C:/Users/Egor/Desktop/gis-programming-class-assignment_5/districts.geojson'

ds_st = QgsVectorLayer(path_stations, 'stations')
ds_dtr = QgsVectorLayer(path_districts, 'districts')

QgsProject.instance().addMapLayer(ds_st)
QgsProject.instance().addMapLayer(ds_dtr)

layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'buffer', 'memory')
provider = layer.dataProvider()

with edit(layer):
    existing_fields = {field.name() for field in layer.fields()}
    fields_to_add = [field for field in ds_st.fields() if field.name() not in existing_fields]
    
    layer.dataProvider().addAttributes(fields_to_add)
    layer.updateFields()
    
    features_to_add = []
    
    for station in ds_st.getFeatures():
        if station['station'] == 'subway':
            depth = int(station['depth'])
            buffer_distance = (depth + 5) * 20
            
            buffer_geom = station.geometry().buffer(buffer_distance, 8)
            
            new_feature = QgsFeature(layer.fields())
            new_feature.setGeometry(buffer_geom)
            
            attrs = station.attributes()[:len(layer.fields())]
            new_feature.setAttributes(attrs)
            
            features_to_add.append(new_feature)
    layer.dataProvider().addFeatures(features_to_add)
    layer.updateExtents()
        
QgsProject.instance().addMapLayer(layer)

buffer_geoms = [f.geometry() for f in layer.getFeatures()]

selected_ids = []
for district in ds_dtr.getFeatures():
    district_geom = district.geometry()
    for buffer_feat in layer.getFeatures():
        depth = int(buffer_feat['depth'])
        if 40 <= depth <= 70 and district_geom.intersects(buffer_feat.geometry()):
            selected_ids.append(district.id())
            break

ds_dtr.selectByIds(selected_ids)
