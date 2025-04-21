from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry
)

stations_layer = QgsVectorLayer('"/mnt/data/stations (1).geojson"', 'Станции', 'ogr')
districts_layer = QgsVectorLayer('"/mnt/data/districts (2).geojson"', 'Районы', 'ogr')

if not stations_layer.isValid() or not districts_layer.isValid():
    raise Exception("Не удалось загрузить один из слоёв")

buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'Буферы_Глазычева', 'memory')
provider = buffer_layer.dataProvider()
provider.addAttributes(stations_layer.fields())
buffer_layer.updateFields()

buffer_features = []
for feature in stations_layer.getFeatures():
    attrs = feature.attributes()
    if 'фиолетовая' in str(attrs).lower():
        depth = None
        for i, field in enumerate(stations_layer.fields()):
            if 'глубин' in field.name().lower():
                depth = attrs[i]
                break
        if depth is not None:
            try:
                radius = (float(depth) + 10) * 20
                geom = feature.geometry().buffer(radius, 8)
                new_feat = QgsFeature()
                new_feat.setGeometry(geom)
                new_feat.setAttributes(attrs)
                buffer_features.append(new_feat)
            except ValueError:
                print(f"Ошибка преобразования глубины в число: {depth}")

provider.addFeatures(buffer_features)
buffer_layer.updateExtents()
QgsProject.instance().addMapLayer(buffer_layer)

districts_layer.removeSelection()

for buf_feat in buffer_layer.getFeatures():
    buf_geom = buf_feat.geometry()
    for dist_feat in districts_layer.getFeatures():
        if buf_geom.intersects(dist_feat.geometry()):
            districts_layer.select(dist_feat.id())
