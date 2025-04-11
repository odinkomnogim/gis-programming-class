from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsSpatialIndex
)
from PyQt5.QtCore import QVariant
import random

# === ОТКРЫТИЕ СЛОЁВ ===
station_layer = QgsVectorLayer('"/mnt/data/stations (1).geojson"', 'Станции', 'ogr')
districts_layer = QgsVectorLayer('"/mnt/data/districts (2).geojson"', 'Районы', 'ogr')

if not station_layer.isValid() or not districts_layer.isValid():
    raise Exception("Один из слоёв не загрузился")

# === СОЗДАНИЕ ВРЕМЕННОГО СЛОЯ ДЛЯ БУФЕРОВ ===
buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'Буферы_Федотов', 'memory')
prov = buffer_layer.dataProvider()

# Копируем атрибуты
prov.addAttributes(station_layer.fields())
buffer_layer.updateFields()

# === БУФЕРИЗАЦИЯ ОРАНЖЕВЫХ СТАНЦИЙ ===
random_1 = random.randint(0, 5)
buffer_radius = (random_1 + 1) * 30
print(f"Используем радиус буфера: {buffer_radius} м")

buffer_features = []
for feat in station_layer.getFeatures():
    attrs = feat.attributes()
    if 'оранжевая' in str(attrs).lower():
        geom = feat.geometry().buffer(buffer_radius, 8)
        new_feat = QgsFeature()
        new_feat.setGeometry(geom)
        new_feat.setAttributes(attrs)
        buffer_features.append(new_feat)

prov.addFeatures(buffer_features)
buffer_layer.updateExtents()
QgsProject.instance().addMapLayer(buffer_layer)

# === СОЗДАНИЕ ПРОСТРАНСТВЕННОГО ИНДЕКСА ДЛЯ РАЙОНОВ ===
spatial_index = QgsSpatialIndex(districts_layer.getFeatures())

# === ВЫДЕЛЕНИЕ ПЕРЕСЕКАЮЩИХСЯ РАЙОНОВ С ИСПОЛЬЗОВАНИЕМ ИНДЕКСА ===
districts_layer.removeSelection()

for buf_feat in buffer_layer.getFeatures():
    buf_geom = buf_feat.geometry()
    intersect_ids = spatial_index.intersects(buf_geom.boundingBox())
    for fid in intersect_ids:
        district_feat = districts_layer.getFeature(fid)
        if buf_geom.intersects(district_feat.geometry()):
            districts_layer.select(fid)

print("Скрипт Федотова с пространственным индексом выполнен. Районы выделены.")
