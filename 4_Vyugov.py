from osgeo import gdal
from qgis.core import QgsProject

# Импортировав gdal, открыть растровое изображение без привязки из папки no_crs
input_raster_path = r'C:\Users\vyugo\OneDrive\Documents\Geoinformatics\sem_2\3.tif'
output_raster_path = r'C:\Users\vyugo\OneDrive\Documents\Geoinformatics\sem_2\out_3.tif'
footprint_path = r'C:\Users\vyugo\OneDrive\Documents\Geoinformatics\sem_2\footprint_3.geojson'

f = gdal.Open(input_raster_path)

# Для каждого канала от 1 до RasterCount+1 (тут отсчёт ведётся не с нуля), получить этот канал (GetRasterBand)
# Затем преобразовать каждый из них в массив (ReadAsArray), где тип данных (astype) – с плавающей запятой.
# Каждый из этих массивов добавить в заранее созданный пустой список массивов
bands = []
for i in range(1, f.RasterCount+1):
    band = f.GetRasterBand(i)
    bands.append(band.ReadAsArray().astype(float))

# Создать копию исходного изображения
driver = gdal.GetDriverByName('GTiff')
copy = driver.Create(
    output_raster_path,
    f.RasterXSize,
    f.RasterYSize,
    f.RasterCount,
    gdal.GDT_Float32
)
for i in range(len(bands)):
    copy.GetRasterBand(i+1).WriteArray(bands[i])

# Далее необходимо получить 4 угловые координаты границ, хранящиеся в файле footprint_3
footprint_layer = QgsProject.instance().addMapLayer(QgsVectorLayer(footprint_path, 'footprint_3', 'ogr'))
feature = footprint_layer.getFeature(0)
geometry = feature.geometry().asPolygon()[0]

# Созданной ранее копии растрового изображения задать проекцию (SetProjection), как у векторного слоя (crs и authid)
copy.SetProjection(footprint_layer.crs().toWkt())

# Создать список, в которого войдут 4 gdal.GCP(x, y, z, pixel, line)
coords = []
for i in geometry[:4]:
    coords.append((i.x(), i.y()))
gcp = []
width = copy.RasterXSize
height = copy.RasterYSize
gcp.append(gdal.GCP(coords[0][0], coords[0][1], 0, 0, 0))  # Северо-западная точка
gcp.append(gdal.GCP(coords[1][0], coords[1][1], 0, width - 1, 0))  # Северо-восточная точка
gcp.append(gdal.GCP(coords[2][0], coords[2][1], 0, width - 1, height - 1))  # Юго-восточная точка
gcp.append(gdal.GCP(coords[3][0], coords[3][1], 0, 0, height - 1))  # Юго-западная точка

# Установить опорные точки для скопированного ранее растрового изображения (SetGCPs), подав в качестве аргумента список GCP и проекцию растрового изображения (GetProjection)
# После чего очистить кэш (изрбражение.FlushCache())
copy.SetGCPs(gcp, footprint_layer.crs().toWkt())
copy.FlushCache()