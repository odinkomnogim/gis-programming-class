Python 3.13.0 (tags/v3.13.0:60403a5, Oct  7 2024, 09:38:07) [MSC v.1941 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from osgeo import gdal
from qgis.core import QgsVectorLayer, QgsProject

import numpy as np
import os

input_raster_path = '/content/drive/MyDrive/4 (2).tif'
output_raster_path = '/content/drive/MyDrive/4 (2)_copy.tif'
footprint_path = '/content/drive/MyDrive/footprint_4.geojson'

raster = gdal.Open(input_raster_path)
if raster is None:
    raise RuntimeError("Не удалось открыть растровый файл")

bands_data = []
for band_index in range(1, raster.RasterCount + 1):
    band = raster.GetRasterBand(band_index)
    band_array = band.ReadAsArray().astype(np.float32)
    bands_data.append(band_array)

print(f"Загружено каналов: {len(bands_data)}")

driver = gdal.GetDriverByName('GTiff')
out_raster = driver.Create(
    output_raster_path,
    raster.RasterXSize,
    raster.RasterYSize,
...     raster.RasterCount,
...     gdal.GDT_Float32
... )
... 
... for idx, data_array in enumerate(bands_data):
...     out_band = out_raster.GetRasterBand(idx + 1)
...     out_band.WriteArray(data_array)
...     out_band.FlushCache()
... 
... footprint_layer = QgsVectorLayer(footprint_path, 'footprint', 'ogr')
... if not footprint_layer.isValid():
...     raise Exception("Не удалось загрузить векторный слой")
... 
... features = footprint_layer.getFeatures()
... feature = next(features)
... geometry = feature.geometry()
... polygon = geometry.asPolygon()[0]  
... 
... corner_coords = []
... for pt in polygon[:4]:
...     corner_coords.append((pt.x(), pt.y()))
... 
... 
... crs = footprint_layer.crs()
... wkt = crs.toWkt()
... out_raster.SetProjection(wkt)
... 
... img_width = raster.RasterXSize
... img_height = raster.RasterYSize
... 
... control_points = [
...     gdal.GCP(corner_coords[0][0], corner_coords[0][1], 0, 0, 0),
...     gdal.GCP(corner_coords[1][0], corner_coords[1][1], 0, img_width - 1, 0),
...     gdal.GCP(corner_coords[2][0], corner_coords[2][1], 0, img_width - 1, img_height - 1),
...     gdal.GCP(corner_coords[3][0], corner_coords[3][1], 0, 0, img_height - 1)
... ]
... 
... out_raster.SetGCPs(control_points, wkt)
