from qgis.core import *


s_layer = QgsProject.instance().mapLayersByName('stations')[0]
d_layer = QgsProject.instance().mapLayersByName('districts')[0]


required_fields = ['some_value', 'colour']
for field in required_fields:
    if field not in s_layer.fields().names():
        raise ValueError(f"В слое stations отсутствует поле: {field}")


b_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'buffers', 'memory')
b_provider = b_layer.dataProvider()
b_provider.addAttributes(s_layer.fields())
b_layer.updateFields()


b_features = []
for station in s_layer.getFeatures():
    try:
        some_value = float(station['some_value'])
        colour = station['colour']


        colour_str = str(colour).strip().lower()

        if colour_str == 'orange':
            radius = (some_value +1) * 25
            b_geom = station.geometry().buffer(radius, 10)

            new_feature = QgsFeature()
            new_feature.setGeometry(b_geom)
            new_feature.setAttributes(station.attributes())
            b_features.append(new_feature)

    except Exception as e:
        print(f"Ошибка в станции ID={station.id()}: {e}")
        continue


b_provider.addFeatures(b_features)
b_layer.updateExtents()
QgsProject.instance().addMapLayer(b_layer)


selected_districts = []
for buffer_feature in b_layer.getFeatures():
    for district in d_layer.getFeatures():
        if buffer_feature.geometry().intersects(district.geometry()):
            selected_districts.append(district.id())


d_layer.select(selected_districts)
print(f"Выделено районов: {len(selected_districts)}")