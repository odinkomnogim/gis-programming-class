from qgis.core import *

# Получаем слои
stations_layer = QgsProject.instance().mapLayersByName('stations')[0]
districts_layer = QgsProject.instance().mapLayersByName('districts')[0]

# Проверяем наличие необходимых полей
required_fields = ['some_value', 'colour']
for field in required_fields:
    if field not in stations_layer.fields().names():
        raise ValueError(f"В слое stations отсутствует поле: {field}")

# Создаем слой буферов
buffer_layer = QgsVectorLayer('Polygon?crs=EPSG:3857', 'buffers', 'memory')
buffer_provider = buffer_layer.dataProvider()
buffer_provider.addAttributes(stations_layer.fields())
buffer_layer.updateFields()

# Часть 1: Буферизация станций ветки
buffer_features = []
for station in stations_layer.getFeatures():
    try:
        some_value = float(station['some_value'])  # Преобразуем в число
        colour = station['colour']  # Получаем QVariant

        # Преобразуем QVariant в строку и очищаем
        colour_str = str(colour).strip().lower()

        if colour_str == 'red':
            radius = some_value * 20
            buffer_geom = station.geometry().buffer(radius, 8)

            new_feature = QgsFeature()
            new_feature.setGeometry(buffer_geom)
            new_feature.setAttributes(station.attributes())
            buffer_features.append(new_feature)

    except Exception as e:
        print(f"Ошибка в станции ID={station.id()}: {e}")
        continue

# Добавляем буферы в слой
buffer_provider.addFeatures(buffer_features)
buffer_layer.updateExtents()
QgsProject.instance().addMapLayer(buffer_layer)

# Часть 2: Поиск пересечений с районами
selected_districts = []
for buffer_feature in buffer_layer.getFeatures():
    for district in districts_layer.getFeatures():
        if buffer_feature.geometry().intersects(district.geometry()):
            selected_districts.append(district.id())

# Выделяем районы
districts_layer.select(selected_districts)
print(f"Выделено районов: {len(selected_districts)}")