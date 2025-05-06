from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry
)

stations_layer = iface.addVectorLayer('C:/Users/Виктория/Downloads/stations (1).geojson', 'Станции', 'ogr')
districts_layer = iface.addVectorLayer('C:/Users/Виктория/Downloads/districts (1).geojson', 'Районы', 'ogr')

buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'Буферы_Алексеева', 'memory')
provider = buffer_layer.dataProvider()
provider.addAttributes(stations_layer.fields())
buffer_layer.updateFields()

buffer_features = []
for feature in stations_layer.getFeatures():
    attrs = feature.attributes()
    if 'blue' in str(attrs).lower():
        depth = None
        for i, field in enumerate(stations_layer.fields()):
            if 'depth' in field.name().lower():
                depth = attrs[i]
                break
        if depth is not None:
            try:
                radius = (float(depth) + 1) * 25
                geom = feature.geometry().buffer(radius, 8)
                new_feat = QgsFeature()
                new_feat.setGeometry(geom)
                new_feat.setAttributes(attrs)
                buffer_features.append(new_feat)
            except ValueError:
                pass

provider.addFeatures(buffer_features)
buffer_layer.updateExtents()
QgsProject.instance().addMapLayer(buffer_layer)

districts_layer.removeSelection()

for buf_feat in buffer_layer.getFeatures():
    buf_geom = buf_feat.geometry()
    for dist_feat in districts_layer.getFeatures():
        if buf_geom.intersects(dist_feat.geometry()):
            districts_layer.select(dist_feat.id())
